# 🧹 Smart Data Cleaner

**An interactive Streamlit web app to automatically analyze, clean, and visualize your CSV datasets.**

---

## 🎯 Project Overview

Data preprocessing is often the most time-consuming phase of any data science workflow. This application automates the essential steps of data cleaning, allowing users to focus on analysis and modeling rather than tedious cleanup tasks.

With just a CSV upload, the app:
-   Generates a comprehensive data quality report.
-   Intelligently detects and quantifies missing values, duplicates, and outliers.
-   Provides dynamic and interactive controls to clean the data.
-   Offers rich visualizations to understand the dataset's state before and after cleaning.
-   Allows instant download of the cleaned dataset.

## ✨ Key Features

-   **Interactive Dashboard**: A clean, tab-based interface built with Streamlit.
-   **Data Summary**: Get instant metrics on rows, columns, duplicates, and missing values.
-   **Duplicate Removal**: Remove duplicate rows with a single click.
-   **Missing Value Imputation**: Handle missing data using various strategies (drop, mean, median, mode).
-   **Outlier Handling**: Detect and cap outliers using the IQR (Interquartile Range) method.
-   **Dynamic Visualizations**:
    -   Missing value heatmaps.
    -   Distribution plots for numerical columns.
    -   Box plots to identify outliers.
    -   Count plots for categorical columns.
-   **Data Download**: Download the cleaned DataFrame as a new CSV file.

## 🛠️ Tech Stack

-   **Python**: Core programming language.
-   **Streamlit**: For building the interactive web application.
-   **Pandas**: For data manipulation and analysis.
-   **NumPy**: For numerical operations, especially in outlier handling.
-   **Matplotlib & Seaborn**: For generating data visualizations.

## 📂 Folder Structure

```
smart_data_cleaner/
│
├── .streamlit/
│   └── config.toml         # App theme configuration
│
├── app.py                  # Main Streamlit app
│
├── utils/
│   ├── data_cleaner.py     # All cleaning functions
│   └── visualizer.py       # Data visualization helper functions
│
├── requirements.txt        # Dependencies list
└── README.md               # Project overview and guide
```

## 🚀 Setup and Usage

Follow these steps to run the application locally:

**1. Clone the Repository**
```bash
git clone https://github.com/your-username/smart-data-cleaner.git
cd smart-data-cleaner
```

**2. Create and Activate a Virtual Environment**

-   **Windows**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
-   **macOS / Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the Streamlit App**
```bash
streamlit run app.py
```

A new tab should open in your web browser at `http://localhost:8501`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.