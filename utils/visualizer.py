import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Define theme colors for consistency
PRIMARY_COLOR = "#6c63ff"
TEXT_COLOR = "#fafafa"
BACKGROUND_COLOR = "none" # Use 'none' for transparency

def style_plot(fig, ax, title):
    """Applies a consistent dark theme style to a plot."""
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
    """Generates a heatmap to visualize missing values with a dark theme."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False, ax=ax)
    
    style_plot(fig, ax, 'Missing Values Heatmap')
    return fig

def plot_distribution(df: pd.DataFrame, column: str):
    """Generates a themed distribution plot for a numerical column."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns or df[column].dropna().empty:
        return None
        
    if pd.api.types.is_numeric_dtype(df[column]):
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(df[column], kde=True, ax=ax, color=PRIMARY_COLOR)
        
        style_plot(fig, ax, f'Distribution of {column}')
        return fig
    return None

def plot_boxplot(df: pd.DataFrame, column: str):
    """Generates a themed box plot to visualize outliers."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns or df[column].dropna().empty:
        return None
        
    if pd.api.types.is_numeric_dtype(df[column]):
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(x=df[column], ax=ax, color=PRIMARY_COLOR)
        
        style_plot(fig, ax, f'Box Plot of {column}')
        return fig
    return None

def plot_countplot(df: pd.DataFrame, column: str):
    """Generates a themed count plot for a categorical column."""
    col_data = df[column].dropna()
    if not isinstance(df, pd.DataFrame) or column not in df.columns or col_data.empty:
        return None

    if pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(y=col_data, order=col_data.value_counts().index, ax=ax, color=PRIMARY_COLOR)
        
        style_plot(fig, ax, f'Count Plot of {column}')
        return fig
    return None