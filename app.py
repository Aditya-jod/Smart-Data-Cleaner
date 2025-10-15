import logging

import streamlit as st
import pandas as pd
from utils.data_cleaner import DataCleaner
import utils.visualizer as viz

logger = logging.getLogger("smart_data_cleaner.app")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Data Cleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0

# --- Helper Function ---
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    # Convert DataFrame to CSV bytes safely
    if df is None:
        return b""
    try:
        if df.empty:
            return b""
        return df.to_csv(index=False).encode('utf-8')
    except Exception as exc:
        logger.exception("Failed to convert DataFrame to CSV: %s", exc)
        return b""

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='color: #0072B5;'>⚙️ Cleaning Controls</h1>", unsafe_allow_html=True)

    if st.session_state.original_df is None:
        st.info("Upload a CSV file to begin cleaning.")
    else:
        # Ensure cleaned_df exists
        if st.session_state.cleaned_df is None:
            st.session_state.cleaned_df = st.session_state.original_df.copy()

        # --- Reset Button ---
        if st.button("Reset and Upload New File"):
            with st.spinner("Resetting..."):
                st.session_state.original_df = None
                st.session_state.cleaned_df = None
                st.session_state.file_uploader_key += 1
                st.rerun()

        # 1. Convert Data Types
        if st.button("Optimize Data Types"):
            with st.spinner("Optimizing types..."):
                try:
                    cleaner = DataCleaner(st.session_state.cleaned_df)
                    cleaner.convert_data_types()
                    st.session_state.cleaned_df = cleaner.get_cleaned_data()
                    st.success("Data types optimized.")
                    st.rerun()
                except Exception:
                    logger.exception("Optimize Data Types failed")
                    st.error("Failed to optimize data types. See logs.")

        # 2. Handle Duplicates
        if st.button("Remove Duplicates"):
            with st.spinner("Removing duplicates..."):
                try:
                    rows_before = len(st.session_state.cleaned_df)
                    cleaner = DataCleaner(st.session_state.cleaned_df)
                    cleaner.remove_duplicates()
                    st.session_state.cleaned_df = cleaner.get_cleaned_data()
                    rows_after = len(st.session_state.cleaned_df)
                    rows_removed = rows_before - rows_after
                    st.success(f"Removed {rows_removed} duplicate rows.")
                    st.rerun()
                except Exception:
                    logger.exception("Remove Duplicates failed")
                    st.error("Failed to remove duplicates. See logs.")

        # 3. Handle Missing Values
        with st.expander("Handle Missing Values", expanded=True):
            df = st.session_state.cleaned_df
            if df is None or df.empty:
                st.write("No data loaded.")
            else:
                try:
                    missing_cols = df.columns[df.isnull().any()].tolist()
                except Exception:
                    missing_cols = []

                if not missing_cols:
                    st.write("No missing values found.")
                else:
                    # Select missing value handling strategy and columns
                    strategy = st.selectbox("Strategy", ["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"], key="mv_strategy")
                    selected_cols = st.multiselect("Select columns", missing_cols, default=missing_cols, key="mv_cols")

                    if st.button("Apply Missing Value Strategy"):
                        with st.spinner("Handling missing values..."):
                            try:
                                cleaner = DataCleaner(st.session_state.cleaned_df)
                                strategy_map = {
                                    "Drop Rows": "drop", "Fill with Mean": "mean",
                                    "Fill with Median": "median", "Fill with Mode": "mode"
                                }
                                cleaner.handle_missing_values(strategy=strategy_map[strategy], columns=selected_cols)
                                st.session_state.cleaned_df = cleaner.get_cleaned_data()
                                st.success("Handled missing values.")
                                st.rerun()
                            except Exception:
                                logger.exception("Handle Missing Values failed")
                                st.error("Failed to handle missing values. See logs.")

        # 4. Handle Outliers
        with st.expander("Handle Outliers (IQR Method)", expanded=True):
            df = st.session_state.cleaned_df
            if df is None or df.empty:
                st.write("No data loaded.")
            else:
                numeric_cols = df.select_dtypes(include='number').columns.tolist()
                if not numeric_cols:
                    st.write("No numerical columns for outlier detection.")
                else:
                    # Select column for outlier handling
                    outlier_col = st.selectbox("Select column", numeric_cols, key="out_col")
                    if st.button("Cap Outliers"):
                        with st.spinner("Capping outliers..."):
                            try:
                                cleaner = DataCleaner(st.session_state.cleaned_df)
                                cleaner.handle_outliers(column=outlier_col, strategy='iqr')
                                st.session_state.cleaned_df = cleaner.get_cleaned_data()
                                st.success(f"Capped outliers in '{outlier_col}'.")
                                st.rerun()
                            except Exception:
                                logger.exception("Cap Outliers failed")
                                st.error("Failed to cap outliers. See logs.")

        # --- Download Button ---
        st.markdown("<h2 style='color: #0072B5;'>Download</h2>", unsafe_allow_html=True)
        csv_bytes = convert_df_to_csv(st.session_state.cleaned_df)
        if csv_bytes:
            st.download_button(
                label="Download Cleaned Data",
                data=csv_bytes,
                file_name='cleaned_data.csv',
                mime='text/csv',
            )
        else:
            st.info("No data available to download.")

# --- Main Panel ---
st.markdown("<h1 style='color: #0072B5;'>🧹 Smart Data Cleaner</h1>", unsafe_allow_html=True)
st.write("Upload your CSV, analyze its quality, clean it interactively, and download the result.")

if st.session_state.original_df is None:
    # File uploader for CSV
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )
    if uploaded_file is not None:
        with st.spinner("Loading data..."):
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.original_df = df
                st.session_state.cleaned_df = df.copy()
                st.rerun()
            except Exception:
                logger.exception("Failed to read uploaded CSV")
                st.error("Failed to read CSV. Please ensure the file is a valid CSV.")
else:
    # Main dashboard with tabs
    tab1, tab2, tab3 = st.tabs(["📊 Data Summary", "📈 Visualizations", "✨ Cleaned Data"])

    with tab1:
        st.markdown("<h2 style='color: #0072B5;'>Original Data Summary</h2>", unsafe_allow_html=True)
        try:
            summary = DataCleaner(st.session_state.original_df).get_summary()
        except Exception:
            logger.exception("Failed to generate original data summary")
            st.error("Failed to generate data summary.")
            summary = {"duplicate_count": 0, "missing_values": pd.Series(dtype=int)}

        # Show metrics for original data
        col1, col2, col3, col4 = st.columns(4)
        original_df = st.session_state.original_df if st.session_state.original_df is not None else pd.DataFrame()
        col1.metric("Total Rows", int(original_df.shape[0]))
        col2.metric("Total Columns", int(original_df.shape[1]))
        col3.metric("Duplicate Rows", int(summary.get('duplicate_count', 0)))
        col4.metric("Total Missing Values", int(summary.get('missing_values', pd.Series(dtype=int)).sum()))

        st.markdown("<h3 style='color: #0072B5;'>Data Preview</h3>", unsafe_allow_html=True)
        st.dataframe(original_df.head())

        st.markdown("<h3 style='color: #0072B5;'>Column Types and Non-Null Counts</h3>", unsafe_allow_html=True)
        df = original_df
        info_df = pd.DataFrame({
            "Non-Null Count": df.count(),
            "Data Type": df.dtypes
        }).reset_index().rename(columns={'index': 'Column Name'})

        info_df['Data Type'] = info_df['Data Type'].astype(str)

        try:
            styled = info_df.style.bar(
                subset=['Non-Null Count'],
                color='#6c63ff',
                align='left',
                vmax=len(df) if len(df) > 0 else 1
            )
            st.dataframe(styled, width='stretch')
        except Exception:
            logger.exception("Styling info_df failed; rendering without style")
            st.dataframe(info_df, width='stretch')

    with tab2:
        st.markdown("<h2 style='color: #0072B5;'>Data Visualizations (on Cleaned Data)</h2>", unsafe_allow_html=True)
        df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else pd.DataFrame()

        st.markdown("<h3 style='color: #0072B5;'>Missing Values</h3>", unsafe_allow_html=True)
        try:
            fig_missing = viz.plot_missing_values(df)
            if fig_missing:
                st.pyplot(fig_missing)
            else:
                st.success("✅ No missing values found!")
        except Exception:
            logger.exception("Failed to render missing values plot")
            st.error("Could not render missing values plot.")

        st.markdown("<h3 style='color: #0072B5;'>Column-wise Plots</h3>", unsafe_allow_html=True)
        if df.empty:
            st.write("No data to visualize.")
        else:
            plot_col = st.selectbox("Select a column to visualize", df.columns.tolist())
            if plot_col:
                try:
                    if pd.api.types.is_numeric_dtype(df[plot_col]):
                        st.write(f"**Distribution of {plot_col}**")
                        fig_dist = viz.plot_distribution(df, plot_col)
                        if fig_dist:
                            st.pyplot(fig_dist)

                        st.write(f"**Box Plot of {plot_col}**")
                        fig_box = viz.plot_boxplot(df, plot_col)
                        if fig_box:
                            st.pyplot(fig_box)
                    else:
                        st.write(f"**Count Plot of {plot_col}**")
                        fig_count = viz.plot_countplot(df, plot_col)
                        if fig_count:
                            st.pyplot(fig_count)
                except Exception:
                    logger.exception("Failed to render plots for column %s", plot_col)
                    st.error("Failed to render plots for the selected column.")

    with tab3:
        st.markdown("<h2 style='color: #0072B5;'>Cleaned Data Preview</h2>", unsafe_allow_html=True)
        cleaned_df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else pd.DataFrame()
        st.dataframe(cleaned_df)

        st.markdown("<h3 style='color: #0072B5;'>Summary of Cleaned Data</h3>", unsafe_allow_html=True)
        try:
            summary_cleaned = DataCleaner(cleaned_df).get_summary()
        except Exception:
            logger.exception("Failed to generate cleaned data summary")
            summary_cleaned = {"duplicate_count": 0, "missing_values": pd.Series(dtype=int)}

        # Show metrics for cleaned data
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", int(cleaned_df.shape[0]))
        col2.metric("Total Columns", int(cleaned_df.shape[1]))
        col3.metric("Duplicate Rows", int(summary_cleaned.get('duplicate_count', 0)))
        col4.metric("Total Missing Values", int(summary_cleaned.get('missing_values', pd.Series(dtype=int)).sum()))

        st.markdown("<h3 style='color: #0072B5;'>Column Types and Non-Null Counts (Cleaned)</h3>", unsafe_allow_html=True)
        info_df_cleaned = pd.DataFrame({
            "Non-Null Count": cleaned_df.count(),
            "Data Type": cleaned_df.dtypes
        }).reset_index().rename(columns={'index': 'Column Name'})

        info_df_cleaned['Data Type'] = info_df_cleaned['Data Type'].astype(str)

        try:
            styled_cleaned = info_df_cleaned.style.bar(
                subset=['Non-Null Count'],
                color='#6c63ff',
                align='left',
                vmax=len(cleaned_df) if len(cleaned_df) > 0 else 1
            )
            st.dataframe(styled_cleaned, width='stretch')
        except Exception:
            logger.exception("Styling info_df_cleaned failed; rendering without style")
            st.dataframe(info_df_cleaned, width='stretch')
# --- End of File ---