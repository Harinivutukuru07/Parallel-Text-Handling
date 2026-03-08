import streamlit as st
import pandas as pd
import time
from multiprocessing import Pool, cpu_count

from processor import process_text
from database import setup_database, insert_results
from mail import send_email

st.set_page_config(page_title="Parallel Text Processor", layout="wide")

st.title("Parallel Text Handling Processor")

# ---------------- SESSION STATE ----------------
if "files" not in st.session_state:
    st.session_state.files = {}

if "texts" not in st.session_state:
    st.session_state.texts = []

if "result_df" not in st.session_state:
    st.session_state.result_df = None

if "processing_time" not in st.session_state:
    st.session_state.processing_time = None

if "pie_chart_path" not in st.session_state:
    st.session_state.pie_chart_path = None

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Files",
    type=["csv", "txt", "xlsx"],
    accept_multiple_files=True
)

# ---------------- STORE FILE DATA ----------------
if uploaded_files:

    for uploaded_file in uploaded_files:

        filename = uploaded_file.name.lower()

        try:
            uploaded_file.seek(0)

            if filename.endswith(".csv"):
                df = pd.read_csv(uploaded_file, low_memory=False)
                st.session_state.files[uploaded_file.name] = df

            elif filename.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                st.session_state.files[uploaded_file.name] = df

            elif filename.endswith(".txt"):
                content = uploaded_file.read().decode("utf-8")
                st.session_state.files[uploaded_file.name] = content

        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")

# ---------------- PAGE LAYOUT ----------------
left, right = st.columns([1,3])

# ---------------- LEFT PANEL ----------------
with left:

    st.subheader("Uploaded Files")

    if st.session_state.files:

        selected_file = st.radio(
            "Select File",
            list(st.session_state.files.keys())
        )

    else:
        st.info("Upload files to view.")

# ---------------- RIGHT PANEL ----------------
with right:

    if st.session_state.files:

        content = st.session_state.files[selected_file]

        st.subheader("File Preview")

        # ---------- DATAFRAME FILE ----------
        if isinstance(content, pd.DataFrame):

            st.dataframe(content.head(100), use_container_width=True)

            if "Text" in content.columns:
                st.session_state.texts = content["Text"].dropna().astype(str).tolist()
            else:
                st.error("File must contain a 'Text' column")
                st.session_state.texts = []

        # ---------- TEXT FILE ----------
        else:

            st.text_area("Content", content, height=300)
            st.session_state.texts = content.splitlines()

        texts = st.session_state.texts

        # ---------------- PROCESS BUTTON ----------------
        if texts:

            st.write("Total Reviews Loaded:", len(texts))

            if st.button("Run Sentiment Processing"):

                setup_database()

                start_time = time.time()

                with st.spinner("Processing reviews..."):

                    with Pool(cpu_count()) as pool:
                        results = list(pool.imap(process_text, texts, chunksize=1000))

                end_time = time.time()

                processing_time = round(end_time - start_time, 2)

                insert_results(results)

                # Persist results so Send Email works across reruns.
                st.session_state.result_df = pd.DataFrame(
                    results,
                    columns=["Text", "Score", "Sentiment", "Patterns", "Timestamp"]
                )
                st.session_state.processing_time = processing_time

                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                st.session_state.result_df["Sentiment"].value_counts().plot.pie(
                    autopct="%1.1f%%",
                    ax=ax
                )
                pie_chart_path = "sentiment_pie_chart.png"
                fig.savefig(pie_chart_path, dpi=100, bbox_inches="tight")
                plt.close(fig)
                st.session_state.pie_chart_path = pie_chart_path

                st.success("Processing Completed")

            if st.session_state.result_df is not None:
                result_df = st.session_state.result_df
                processing_time = st.session_state.processing_time
                pie_chart_path = st.session_state.pie_chart_path

                st.write("Processing Time:", processing_time, "seconds")

                # ---------------- SUMMARY ----------------
                st.subheader("Summary")

                total = len(result_df)
                positives = (result_df["Sentiment"] == "Positive").sum()
                negatives = (result_df["Sentiment"] == "Negative").sum()
                neutrals = (result_df["Sentiment"] == "Neutral").sum()

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total Reviews", total)
                col2.metric("Positive", positives)
                col3.metric("Negative", negatives)
                col4.metric("Neutral", neutrals)

                # ---------------- CHART ----------------
                st.subheader("Sentiment Distribution")
                st.bar_chart(result_df["Sentiment"].value_counts())

                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                result_df["Sentiment"].value_counts().plot.pie(
                    autopct="%1.1f%%",
                    ax=ax
                )
                st.pyplot(fig)
                plt.close(fig)

                # ---------------- SAMPLE REVIEWS ----------------
                st.subheader("Example Reviews")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.write("Positive Examples")
                    st.write(
                        result_df[result_df["Sentiment"] == "Positive"]["Text"].head(10)
                    )

                with c2:
                    st.write("Negative Examples")
                    st.write(
                        result_df[result_df["Sentiment"] == "Negative"]["Text"].head(10)
                    )

                with c3:
                    st.write("Neutral Examples")
                    st.write(
                        result_df[result_df["Sentiment"] == "Neutral"]["Text"].head(10)
                    )

                # ---------------- FULL TABLE ----------------
                with st.expander("Show Full Results (First 1000 rows)"):
                    st.dataframe(result_df.head(1000), use_container_width=True)
                    st.write(f"Total rows in results: {len(result_df)}")
                    st.write("Note: CSV with all results will be sent via email")

                # ---------------- EMAIL SECTION ----------------
                st.subheader("Send Results by Email")

                email = st.text_input("Enter Email Address", placeholder="example@gmail.com")

                if st.button("Send Email"):
                    if not email or email.strip() == "":
                        st.error("Please enter a valid email address")
                    elif "@" not in email or "." not in email:
                        st.error("Invalid email format. Please enter a valid email address")
                    else:
                        try:
                            st.write(f"Sending email to: {email}")

                            # Send report summary in email body and include chart only.
                            attachments = []
                            if pie_chart_path:
                                attachments.append((pie_chart_path, "sentiment_pie_chart.png"))

                            response = send_email(
                                email,
                                total,
                                positives,
                                negatives,
                                neutrals,
                                processing_time,
                                attachments=attachments
                            )

                            message_id = response.get("id") if isinstance(response, dict) else "N/A"
                            st.success(f"Email sent successfully with attachments to {email}")
                            st.info(f"Gmail Message ID: {message_id}")
                        except Exception as e:
                            st.error(f"Email failed: {str(e)}")
                            