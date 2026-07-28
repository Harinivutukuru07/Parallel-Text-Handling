import streamlit as st
import pandas as pd
import sqlite3

def render_results_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f2f4f8 0%, #eef1f6 100%);
        }
        h1, h2, h3 {
            color: #1c3559;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Processing Results Dashboard")
    
    if "result_df" not in st.session_state or st.session_state.result_df is None:
        st.warning("No results found. Please run the sentiment processing on the main page first.")
        return

    st.success(st.session_state.get("processing_summary", "Processing completed successfully!"))
    
    st.subheader("Visualizations")
    col1, col2 = st.columns(2)
    
    with col1:
        if "pie_chart_path" in st.session_state:
            st.image(st.session_state.pie_chart_path, caption="Sentiment Distribution (Pie)")
        if "issue_chart_path" in st.session_state:
            st.image(st.session_state.issue_chart_path, caption="Issue Patterns")
            
    with col2:
        if "bar_chart_path" in st.session_state:
            st.image(st.session_state.bar_chart_path, caption="Sentiment Distribution (Bar)")

    st.subheader("Data Sample")
    st.dataframe(st.session_state.result_df.head(100), use_container_width=True)
    
    st.subheader("Downloads")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        if "full_csv_path" in st.session_state:
            try:
                with open(st.session_state.full_csv_path, "rb") as file:
                    st.download_button(
                        label="Download Full Results (CSV)",
                        data=file,
                        file_name="sentiment_results_full.csv",
                        mime="text/csv",
                    )
            except FileNotFoundError:
                pass

    with col_dl2:
        if "sample_csv_path" in st.session_state:
            try:
                with open(st.session_state.sample_csv_path, "rb") as file:
                    st.download_button(
                        label="Download Sample Results (CSV)",
                        data=file,
                        file_name="sentiment_results_sample.csv",
                        mime="text/csv",
                    )
            except FileNotFoundError:
                pass

st.set_page_config(page_title="Results Dashboard", layout="wide")
render_results_page()