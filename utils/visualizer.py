import logging
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.figure import Figure

logger = logging.getLogger("smart_data_cleaner.visualizer")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Theme colors for all plots
PRIMARY_COLOR = "#6c63ff"
TEXT_COLOR = "#fafafa"
BACKGROUND_COLOR = "none"  # Transparent background for plots

sns.set_theme(style="darkgrid")  # base theme; style_plot will refine visuals


def style_plot(fig: Figure, ax, title: str) -> None:
    """Apply dark theme and consistent style to a plot."""
    try:
        fig.patch.set_facecolor(BACKGROUND_COLOR)
        ax.set_facecolor(BACKGROUND_COLOR)

        if title:
            ax.set_title(title, color=TEXT_COLOR, pad=12)
        ax.tick_params(colors=TEXT_COLOR, which="both")
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)

        for spine in ax.spines.values():
            spine.set_edgecolor(TEXT_COLOR)

        plt.tight_layout()
    except Exception as exc:
        logger.exception("Failed to style plot: %s", exc)


def _validate_df(df: pd.DataFrame) -> bool:
    if not isinstance(df, pd.DataFrame):
        logger.warning("Visualizer received non-DataFrame input.")
        return False
    if df.empty:
        logger.debug("Visualizer received empty DataFrame.")
        return False
    return True


def plot_missing_values(df: pd.DataFrame) -> Optional[Figure]:
    """
    Show a horizontal bar chart of missing value counts for each column.
    Returns matplotlib.figure.Figure or None if nothing to plot.
    """
    if not _validate_df(df):
        return None

    try:
        missing_counts = df.isnull().sum()
        missing_counts = missing_counts[missing_counts > 0]  # Only columns with missing values

        if missing_counts.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        missing_counts.sort_values().plot(kind="barh", ax=ax, color=PRIMARY_COLOR)
        ax.set_xlabel("Number of Missing Values", color=TEXT_COLOR)
        style_plot(fig, ax, "Missing Value Counts per Column")
        return fig
    except Exception as exc:
        logger.exception("plot_missing_values failed: %s", exc)
        return None


def plot_distribution(df: pd.DataFrame, column: str) -> Optional[Figure]:
    """Show histogram and KDE for a numeric column."""
    if not _validate_df(df) or column not in df.columns:
        return None
    try:
        col = df[column].dropna()
        if col.empty:
            return None

        if pd.api.types.is_numeric_dtype(col):
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(col, kde=True, ax=ax, color=PRIMARY_COLOR)
            ax.set_xlabel(column, color=TEXT_COLOR)
            style_plot(fig, ax, f"Distribution of {column}")
            return fig
        logger.debug("Column %s is not numeric; distribution plot skipped.", column)
        return None
    except Exception as exc:
        logger.exception("plot_distribution failed for %s: %s", column, exc)
        return None


def plot_boxplot(df: pd.DataFrame, column: str) -> Optional[Figure]:
    """Show box plot for a numeric column to highlight outliers."""
    if not _validate_df(df) or column not in df.columns:
        return None
    try:
        col = df[column].dropna()
        if col.empty:
            return None

        if pd.api.types.is_numeric_dtype(col):
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.boxplot(x=col, ax=ax, color=PRIMARY_COLOR)
            style_plot(fig, ax, f"Box Plot of {column}")
            return fig
        logger.debug("Column %s is not numeric; boxplot skipped.", column)
        return None
    except Exception as exc:
        logger.exception("plot_boxplot failed for %s: %s", column, exc)
        return None


def plot_countplot(df: pd.DataFrame, column: str, top_n: int = 15) -> Optional[Figure]:
    """
    Show bar chart for most common categories in a column.
    If there are many categories, group less common ones as "Other".
    Returns matplotlib.figure.Figure or None.
    """
    if not _validate_df(df) or column not in df.columns:
        return None
    if not isinstance(top_n, int) or top_n <= 0:
        logger.warning("top_n must be a positive integer. Received: %s", top_n)
        return None

    try:
        col_data = df[column].dropna()
        if col_data.empty:
            return None

        if pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
            value_counts = col_data.value_counts()
            if value_counts.empty:
                return None

            # Only show top_n categories, group the rest as "Other"
            if len(value_counts) > top_n:
                top_counts = value_counts.nlargest(top_n).copy()
                other_count = int(value_counts.iloc[top_n:].sum())
                # ensure 'Other' is added at the end
                top_counts = pd.concat([top_counts, pd.Series({"Other": other_count})])
                counts_to_plot = top_counts
            else:
                counts_to_plot = value_counts

            fig, ax = plt.subplots(figsize=(10, max(4, 0.3 * len(counts_to_plot))))
            sns.barplot(y=counts_to_plot.index.astype(str), x=counts_to_plot.values, ax=ax, color=PRIMARY_COLOR, orient="h")
            style_plot(fig, ax, f"Top {min(top_n, len(value_counts))} Categories in {column}")
            return fig
        logger.debug("Column %s is not categorical/object; countplot skipped.", column)
        return None
    except Exception as exc:
        logger.exception("plot_countplot failed for %s: %s", column, exc)
        return None

# End of utils/visualizer.py