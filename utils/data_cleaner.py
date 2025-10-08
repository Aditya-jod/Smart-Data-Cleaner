import pandas as pd
import numpy as np
from io import StringIO

class DataCleaner:
    """
    A class to handle various data cleaning operations on a pandas DataFrame safely.
    Supports method chaining for a fluent interface.
    """

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initializes the DataCleaner with a copy of the dataframe.
        Ensures the input is a pandas DataFrame.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = dataframe.copy()  # Work on a copy to avoid modifying original data

    def get_summary(self):
        """
        Generates a summary of the current state of the dataframe.
        Returns info, description, missing values, and duplicate count.
        """
        info_buf = StringIO()  # Buffer to capture DataFrame info output
        self.df.info(buf=info_buf)
        info_str = info_buf.getvalue()
        summary = {
            "info": info_str,                                    # DataFrame structure and types
            "description": self.df.describe(include='all').T,    # Statistical summary
            "missing_values": self.df.isnull().sum(),            # Count of missing values per column
            "duplicate_count": self.df.duplicated().sum()        # Number of duplicate rows
        }
        return summary

    def remove_duplicates(self):
        """
        Removes duplicate rows from the dataframe.
        Resets index after dropping duplicates.
        Returns self for method chaining.
        """
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        return self

    def handle_missing_values(self, strategy: str, columns: list = None):
        """
        Handles missing values in specified columns using a chosen strategy.
        Supported strategies: 'drop', 'mean', 'median', 'mode'.
        If columns not specified, applies to all columns.
        Returns self for chaining.
        """
        if columns is None:
            columns = self.df.columns.tolist()

        for col in columns:
            # Skip columns with no missing values or not present in DataFrame
            if col not in self.df.columns or self.df[col].isnull().sum() == 0:
                continue

            if strategy == 'drop':
                # Drop rows where column value is missing
                self.df.dropna(subset=[col], inplace=True)
            elif strategy in ['mean', 'median'] and pd.api.types.is_numeric_dtype(self.df[col]):
                # Fill missing values with mean or median for numeric columns
                fill_value = self.df[col].mean() if strategy == 'mean' else self.df[col].median()
                self.df[col].fillna(fill_value, inplace=True)
            elif strategy == 'mode':
                # Fill missing values with mode (most frequent value)
                if not self.df[col].mode().empty:
                    fill_value = self.df[col].mode()[0]
                    self.df[col].fillna(fill_value, inplace=True)
        return self

    def handle_outliers(self, column: str, strategy: str = 'iqr'):
        """
        Handles outliers in a numerical column by capping them using the IQR method.
        Only applies to numeric columns.
        Returns self for chaining.
        """
        if column in self.df.columns and pd.api.types.is_numeric_dtype(self.df[column]):
            if strategy == 'iqr':
                # Calculate IQR and cap values outside 1.5*IQR from Q1 and Q3
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                self.df[column] = self.df[column].clip(lower=lower_bound, upper=upper_bound)
        return self

    def convert_data_types(self, columns: list = None):
        """
        Attempts to convert columns to the best possible data types.
        For object columns, tries to convert to numeric if possible.
        Uses pandas' convert_dtypes to infer optimal types.
        Returns self for chaining.
        """
        if columns is None:
            columns = self.df.columns.tolist()

        for col in columns:
            if col in self.df.columns and self.df[col].dtype == 'object':
                # Try converting object columns to numeric, ignore errors
                self.df[col] = pd.to_numeric(self.df[col], errors='ignore')

        # Let pandas infer the best types for all columns
        self.df = self.df.convert_dtypes()
        return self

    def get_cleaned_data(self):
        """
        Returns a copy of the cleaned dataframe.
        Ensures the original cleaned data is not modified externally.
        """
        return self.df.copy()
    