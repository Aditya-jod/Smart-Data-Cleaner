import streamlit as st
import pandas as pd
from utils.data_cleaner import DataCleaner
import utils.visualizer as viz

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
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='color: #0072B5;'>⚙️ Cleaning Controls</h1>", unsafe_allow_html=True)

    if st.session_state.original_df is None:
        st.info("Upload a CSV file to begin cleaning.")
    else:
        # --- Reset Button ---
        if st.button("Reset and Upload New File"):
            with st.spinner("Resetting..."):
                st.session_state.original_df = None
                st.session_state.cleaned_df = None
                st.session_state.file_uploader_key += 1
                st.rerun()

        # 1. Handle Duplicates
        if st.button("Remove Duplicates"):
            with st.spinner("Handling duplicates..."):
                cleaner = DataCleaner(st.session_state.cleaned_df)
                rows_removed = cleaner.remove_duplicates()
                st.session_state.cleaned_df = cleaner.get_cleaned_data()
                st.toast(f"Removed {rows_removed} duplicate rows.")
                st.rerun()

        # 2. Handle Missing Values
        with st.expander("Handle Missing Values", expanded=True):
            df = st.session_state.cleaned_df
            missing_cols = df.columns[df.isnull().any()].tolist()
            if not missing_cols:
                st.write("No missing values found.")
            else:
                strategy = st.selectbox("Strategy", ["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"], key="mv_strategy")
                selected_cols = st.multiselect("Select columns", missing_cols, default=missing_cols, key="mv_cols")
                
                if st.button("Apply Missing Value Strategy"):
                    cleaner = DataCleaner(st.session_state.cleaned_df)
                    strategy_map = {
                        "Drop Rows": "drop", "Fill with Mean": "mean",
                        "Fill with Median": "median", "Fill with Mode": "mode"
                    }
                    cleaner.handle_missing_values(strategy=strategy_map[strategy], columns=selected_cols)
                    st.session_state.cleaned_df = cleaner.get_cleaned_data()
                    st.toast("Handled missing values.")
                    st.rerun()

        # 3. Handle Outliers
        with st.expander("Handle Outliers (IQR Method)", expanded=True):
            df = st.session_state.cleaned_df
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                st.write("No numerical columns for outlier detection.")
            else:
                outlier_col = st.selectbox("Select column", numeric_cols, key="out_col")
                if st.button("Cap Outliers"):
                    cleaner = DataCleaner(st.session_state.cleaned_df)
                    cleaner.handle_outliers(column=outlier_col, strategy='iqr')
                    st.session_state.cleaned_df = cleaner.get_cleaned_data()
                    st.toast(f"Capped outliers in '{outlier_col}'.")
                    st.rerun()

        # --- Download Button ---
        st.markdown("<h2 style='color: #0072B5;'>Download</h2>", unsafe_allow_html=True)
        csv = convert_df_to_csv(st.session_state.cleaned_df)
        st.download_button(
            label="Download Cleaned Data",
            data=csv,
            file_name='cleaned_data.csv',
            mime='text/csv',
        )

# --- Main Panel ---
st.markdown("<h1 style='color: #0072B5;'>🧹 Smart Data Cleaner</h1>", unsafe_allow_html=True)
st.write("Upload your CSV, analyze its quality, clean it interactively, and download the result.")

if st.session_state.original_df is None:
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv", 
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.original_df = df
        st.session_state.cleaned_df = df.copy()
        st.rerun()
else:
    # Main dashboard with tabs
    tab1, tab2, tab3 = st.tabs(["📊 Data Summary", "📈 Visualizations", "✨ Cleaned Data"])

    with tab1:
        st.markdown("<h2 style='color: #0072B5;'>Original Data Summary</h2>", unsafe_allow_html=True)
        summary = DataCleaner(st.session_state.original_df).get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", st.session_state.original_df.shape[0])
        col2.metric("Total Columns", st.session_state.original_df.shape[1])
        col3.metric("Duplicate Rows", summary['duplicate_count'])
        col4.metric("Total Missing Values", int(summary['missing_values'].sum()))

        st.markdown("<h3 style='color: #0072B5;'>Data Preview</h3>", unsafe_allow_html=True)
        st.dataframe(st.session_state.original_df.head())

        st.markdown("<h3 style='color: #0072B5;'>Column Types and Non-Null Counts</h3>", unsafe_allow_html=True)
        df = st.session_state.original_df
        info_df = pd.DataFrame({
            "Non-Null Count": df.count(),
            "Data Type": df.dtypes
        }).reset_index().rename(columns={'index': 'Column Name'})
        
        # Convert dtype objects to strings for Arrow compatibility
        info_df['Data Type'] = info_df['Data Type'].astype(str)
        
        st.dataframe(
            info_df.style.bar(
                subset=['Non-Null Count'], 
                color='#6c63ff',
                align='left',
                vmax=len(df)
            ), 
            use_container_width=True
        )

    with tab2:
        st.markdown("<h2 style='color: #0072B5;'>Data Visualizations (on Cleaned Data)</h2>", unsafe_allow_html=True)
        df = st.session_state.cleaned_df
        
        st.markdown("<h3 style='color: #0072B5;'>Missing Values Heatmap</h3>", unsafe_allow_html=True)
        fig_missing = viz.plot_missing_values(df)
        if fig_missing:
            st.pyplot(fig_missing)
        else:
            st.write("No data to display.")

        st.markdown("<h3 style='color: #0072B5;'>Column-wise Plots</h3>", unsafe_allow_html=True)
        plot_col = st.selectbox("Select a column to visualize", df.columns)
        
        if plot_col:
            if pd.api.types.is_numeric_dtype(df[plot_col]):
                st.write(f"**Distribution of {plot_col}**")
                fig_dist = viz.plot_distribution(df, plot_col)
                if fig_dist: st.pyplot(fig_dist)

                st.write(f"**Box Plot of {plot_col}**")
                fig_box = viz.plot_boxplot(df, plot_col)
                if fig_box: st.pyplot(fig_box)
            else:
                st.write(f"**Count Plot of {plot_col}**")
                fig_count = viz.plot_countplot(df, plot_col)
                if fig_count: st.pyplot(fig_count)

    with tab3:
        st.markdown("<h2 style='color: #0072B5;'>Cleaned Data Preview</h2>", unsafe_allow_html=True)
        st.dataframe(st.session_state.cleaned_df)
        
        st.markdown("<h3 style='color: #0072B5;'>Summary of Cleaned Data</h3>", unsafe_allow_html=True)
        cleaned_df = st.session_state.cleaned_df
        summary_cleaned = DataCleaner(cleaned_df).get_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", cleaned_df.shape[0])
        col2.metric("Total Columns", cleaned_df.shape[1])
        col3.metric("Duplicate Rows", summary_cleaned['duplicate_count'])
        col4.metric("Total Missing Values", int(summary_cleaned['missing_values'].sum()))

        st.markdown("<h3 style='color: #0072B5;'>Column Types and Non-Null Counts (Cleaned)</h3>", unsafe_allow_html=True)
        info_df_cleaned = pd.DataFrame({
            "Non-Null Count": cleaned_df.count(),
            "Data Type": cleaned_df.dtypes
        }).reset_index().rename(columns={'index': 'Column Name'})

        # Convert dtype objects to strings for Arrow compatibility
        info_df_cleaned['Data Type'] = info_df_cleaned['Data Type'].astype(str)

        st.dataframe(
            info_df_cleaned.style.bar(
                subset=['Non-Null Count'],
                color='#6c63ff',
                align='left',
                vmax=len(cleaned_df) if len(cleaned_df) > 0 else 1
            ),
            use_container_width=True 
        )