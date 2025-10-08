import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Theme colors for all plots
PRIMARY_COLOR = "#6c63ff"
TEXT_COLOR = "#fafafa"
BACKGROUND_COLOR = "none" # Transparent background for plots

def style_plot(fig, ax, title):
    """Apply dark theme and consistent style to a plot."""
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)
    
    ax.set_title(title, color=TEXT_COLOR, pad=20)
    ax.tick_params(colors=TEXT_COLOR, which='both')
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    
    for spine in ax.spines.values():
        spine.set_edgecolor(TEXT_COLOR)
    
    plt.tight_layout()

def plot_missing_values(df: pd.DataFrame):
    """
    Show a bar chart of missing value counts for each column.
    Only columns with missing data are shown.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
    
    missing_counts = df.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0] # Only columns with missing values

    if missing_counts.empty:
        # No missing values found
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    missing_counts.sort_values().plot(kind='barh', ax=ax, color=PRIMARY_COLOR)
    ax.set_xlabel("Number of Missing Values")
    ax.set_title("Missing Value Counts per Column")
    
    style_plot(fig, ax, 'Missing Value Counts per Column')
    return fig

def plot_distribution(df: pd.DataFrame, column: str):
    """Show histogram and KDE for a numeric column."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns or df[column].dropna().empty:
        return None
        
    if pd.api.types.is_numeric_dtype(df[column]):
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(df[column], kde=True, ax=ax, color=PRIMARY_COLOR)
        
        style_plot(fig, ax, f'Distribution of {column}')
        return fig
    return None

def plot_boxplot(df: pd.DataFrame, column: str):
    """Show box plot for a numeric column to highlight outliers."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns or df[column].dropna().empty:
        return None
        
    if pd.api.types.is_numeric_dtype(df[column]):
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(x=df[column], ax=ax, color=PRIMARY_COLOR)
        
        style_plot(fig, ax, f'Box Plot of {column}')
        return fig
    return None

def plot_countplot(df: pd.DataFrame, column: str, top_n: int = 15):
    """
    Show bar chart for most common categories in a column.
    If there are many categories, group less common ones as "Other".
    """
    col_data = df[column].dropna()
    if not isinstance(df, pd.DataFrame) or column not in df.columns or col_data.empty:
        return None

    if pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
        fig, ax = plt.subplots(figsize=(10, 8))
        
        value_counts = col_data.value_counts()
        
        # Only show top_n categories, group the rest as "Other"
        if len(value_counts) > top_n:
            top_counts = value_counts.nlargest(top_n)
            other_count = value_counts.nsmallest(len(value_counts) - top_n).sum()
            top_counts['Other'] = other_count
            counts_to_plot = top_counts
        else:
            counts_to_plot = value_counts

        sns.barplot(y=counts_to_plot.index, x=counts_to_plot.values, ax=ax, color=PRIMARY_COLOR, orient='h')
        
        style_plot(fig, ax, f'Top {min(top_n, len(value_counts))} Categories in {column}')
        return fig
    return None
