import streamlit as st
import pandas as pd
import time
import sqlite3
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt

from processor.processor import process_text
from storage.database import setup_database
from storage.queries import insert_results

SENTIMENT_ORDER = ["Positive", "Negative", "Neutral"]
SENTIMENT_COLORS = {
    "Positive": "#2e8b57",
    "Negative": "#d9534f",
    "Neutral": "#8a93a6",
}
ISSUE_SUMMARY_KEYS = [
    ("phishing", "Phishing"),
    ("scam_risk", "Scam"),
    ("delivery_issue", "Delivery Issue"),
    ("product_damage", "Product Damage"),
    ("customer_service", "Customer Service"),
]

# Reserve one CPU core for the OS and use remaining cores for workers.
WORKER_PROCESSES = max(1, cpu_count() - 1)


def format_timestamp(value):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%d %b %Y, %I:%M %p").replace(", 0", ", ")


def build_sentiment_counts(result_df):
    return result_df["Sentiment"].value_counts().reindex(SENTIMENT_ORDER, fill_value=0)


def build_issue_counts(result_df):
    pattern_sets = (
        result_df["Patterns"]
        .fillna("none")
        .astype(str)
        .str.lower()
        .apply(lambda value: {item.strip() for item in value.split(",") if item.strip() and item.strip() != "none"})
    )

    return {
        label: int(pattern_sets.apply(lambda labels: key in labels).sum())
        for key, label in ISSUE_SUMMARY_KEYS
    }


def save_chart_images(result_df):
    counts = build_sentiment_counts(result_df)
    total = max(int(counts.sum()), 1)
    percentages = (counts / total) * 100
    colors = [SENTIMENT_COLORS[label] for label in counts.index]

    fig, ax = plt.subplots(figsize=(3.4, 3.4), dpi=120)
    ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 9},
    )
    ax.set_ylabel("")
    fig.tight_layout()
    pie_path = "pie_chart.png"
    fig.savefig(pie_path)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.2, 3.2), dpi=120)
    bars = ax.bar(counts.index, counts.values, color=colors, width=0.58)
    ax.bar_label(
        bars,
        labels=[f"{percentage:.1f}%" for percentage in percentages],
        padding=3,
        fontsize=9,
    )
    ax.tick_params(axis="x", rotation=0)
    ax.set_xlabel("")
    ax.set_ylabel("Reviews")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(counts.max() * 1.2, 1))
    fig.tight_layout()
    bar_path = "bar_chart.png"
    fig.savefig(bar_path)
    plt.close(fig)

    issue_counts = build_issue_counts(result_df)
    issue_labels = [label for _, label in ISSUE_SUMMARY_KEYS]
    issue_values = [issue_counts[label] for label in issue_labels]

    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=120)
    bars = ax.bar(issue_labels, issue_values, color="#4f6a8a", width=0.58)
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.tick_params(axis="x", rotation=20)
    ax.set_xlabel("")
    ax.set_ylabel("Reviews")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(max(issue_values) * 1.25 if issue_values else 0, 1))
    fig.tight_layout()
    issue_path = "issue_pattern_chart.png"
    fig.savefig(issue_path)
    plt.close(fig)

    return pie_path, bar_path, issue_path

st.set_page_config(page_title="Parallel Text Processor", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f2f4f8 0%, #eef1f6 100%);
    }
    [data-testid="stSidebar"] {
        background: #e9edf3;
        border-right: 1px solid #cfd6e2;
    }
    h1, h2, h3 {
        color: #1c3559;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #b5bcc8;
        background-color: #f3f5f9;
        color: #243b5f;
        font-weight: 600;
        padding: 0.4rem 1rem;
    }
    .stButton > button:hover {
        border-color: #7f8ca3;
        background-color: #e9edf5;
    }
    .stDownloadButton > button {
        border-radius: 10px;
    }
    [data-testid="stTextInputRootElement"] input {
        background: #ffffff;
        border: 1px solid #b8c2d3;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Parallel Text Handling Processor")

# session storage
if "result_df" not in st.session_state:
    st.session_state.result_df = None

# ---------------- FILE UPLOAD ----------------
st.sidebar.header("Navigation")
st.sidebar.subheader("Upload Files")

uploaded_file = st.sidebar.file_uploader(
    "Drag and drop files here",
    type=["csv","txt","xlsx"]
)

texts = []

if uploaded_file:

    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.sidebar.write(f"Selected: {uploaded_file.name}")
    st.sidebar.caption(f"{file_size_mb:.1f} MB")

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file, usecols=["Text"])
            texts = df["Text"].dropna().astype(str).str.strip()
            texts = texts[texts != ""].tolist()
            st.dataframe(
                df.head(50),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Text": st.column_config.TextColumn("Review Text", width="large")
                },
            )

        elif filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, usecols=["Text"])
            texts = df["Text"].dropna().astype(str).str.strip()
            texts = texts[texts != ""].tolist()
            st.dataframe(
                df.head(50),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Text": st.column_config.TextColumn("Review Text", width="large")
                },
            )

        elif filename.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
            texts = [line.strip() for line in content.splitlines() if line.strip()]
            preview_df = pd.DataFrame({"Text": texts[:50]})
            st.dataframe(
                preview_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Text": st.column_config.TextColumn("Review Text", width="large")
                },
            )
    except ValueError:
        st.error("The uploaded file must contain a 'Text' column.")
    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty.")
    except UnicodeDecodeError:
        st.error("The text file could not be decoded as UTF-8.")
    except Exception as exc:
        st.error(f"Could not read the uploaded file: {exc}")

    if uploaded_file and not texts:
        st.warning("The uploaded file does not contain any non-empty text rows to process.")

# ---------------- PROCESS ----------------
if texts:

    st.write("Total Reviews:", f"{len(texts):,}")
    st.sidebar.divider()
    st.sidebar.subheader("System Info")
    st.sidebar.write("CPU Cores:", cpu_count())
    st.sidebar.write("Worker Processes:", WORKER_PROCESSES)
    st.sidebar.write("Reserved for OS:", 1)

    if st.button("Run Sentiment Processing"):
        try:
            setup_database()
        except sqlite3.OperationalError as exc:
            st.error(f"Database is busy. Close other tools using sentiment_project.db and try again. Details: {exc}")
            st.stop()

        start = time.time()

        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        results = []
        update_interval = max(1, len(texts) // 200)

        with st.spinner("Processing Reviews..."):
            with Pool(WORKER_PROCESSES) as pool:
                for index, result in enumerate(pool.imap(process_text, texts, chunksize=1000), start=1):
                    results.append(result)
                    if index == 1 or index % update_interval == 0 or index == len(texts):
                        progress_bar.progress(index / len(texts))
                        status_placeholder.caption(f"Processing reviews... {index:,}/{len(texts):,}")

        end = time.time()
        progress_bar.empty()
        status_placeholder.empty()

        processing_time = round(end-start,2)

        try:
            insert_results(results)
        except sqlite3.OperationalError as exc:
            st.error(f"Could not save results because the database is busy. Details: {exc}")
            st.stop()

        result_df = pd.DataFrame(
            results,
            columns=["Text","Sentiment Score","Sentiment","Patterns","Timestamp"]
        )

        result_df["Patterns"] = result_df["Patterns"].replace("", "none").fillna("none")
        result_df["Timestamp"] = result_df["Timestamp"].apply(format_timestamp)

        st.session_state.result_df = result_df
        st.session_state.processing_time = processing_time
        avg_ms_per_review = (processing_time / len(result_df)) * 1000 if len(result_df) else 0
        st.session_state.avg_ms_per_review = round(avg_ms_per_review, 2)
        issue_counts = build_issue_counts(result_df)
        issue_summary_text = ", ".join(
            f"{label}: {issue_counts[label]:,}" for _, label in ISSUE_SUMMARY_KEYS
        )
        st.session_state.processing_summary = (
            f"{len(result_df):,} reviews processed in {processing_time:.2f}s "
            f"({avg_ms_per_review:.2f} ms per review). "
            f"Key issues - {issue_summary_text}"
        )

        # ---------- SAVE FULL CSV ----------
        full_csv_path = "sentiment_results_full.csv"
        result_df.to_csv(full_csv_path,index=False)
        st.session_state.full_csv_path = full_csv_path

        # ---------- SAVE SAMPLE CSV ----------
        sample_csv_path = "sentiment_results_sample.csv"
        result_df.head(5000).to_csv(sample_csv_path,index=False)
        st.session_state.sample_csv_path = sample_csv_path

        pie_path, bar_path, issue_path = save_chart_images(result_df)

        st.session_state.pie_chart_path = pie_path
        st.session_state.bar_chart_path = bar_path
        st.session_state.issue_chart_path = issue_path

        st.success(st.session_state.processing_summary)

        st.info("Open the Results page from the sidebar.")