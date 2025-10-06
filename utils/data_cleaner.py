import pandas as pd
import numpy as np

class DataCleaner:
    """
    A class to handle various data cleaning operations on a pandas DataFrame safely.
    """
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initializes the DataCleaner with a dataframe.
        """
        self.df = dataframe.copy()

    def get_summary(self):
        """
        Generates a summary of the dataframe including data info, description, missing values.
        Ensures that no data is modified during the process.
        """
        from io import StringIO
        info_buf = StringIO()
        self.df.info(buf=info_buf)
        info_str = info_buf.getvalue()
        summary = {
            "info": info_str,
            "description": self.df.describe(include='all').T,
            "missing_values": self.df.isnull().sum(),
            "duplicate_count": self.df.duplicated().sum()
        }
        return summary

    def remove_duplicates(self):
        """
        Removes duplicate rows from the dataframe safely.
        """
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates()
        rows_removed = initial_rows - len(self.df)
        return rows_removed

    def handle_missing_values(self, strategy: str, columns: list = None):
        """
        Handles missing values in specified columns using a given strategy safely.

        Args:
            strategy (str): The strategy to use ('drop', 'mean', 'median', 'mode').
            columns (list, optional): The list of columns to apply the strategy on. 
                                      Defaults to all columns.
        """
        df_copy = self.df.copy()
        if columns is None:
            columns = df_copy.columns.tolist()

        for col in columns:
            if col not in df_copy.columns:
                continue
            if df_copy[col].isnull().sum() > 0:
                try:
                    if strategy == 'drop':
                        df_copy = df_copy.dropna(subset=[col])
                    elif strategy in ['mean', 'median'] and pd.api.types.is_numeric_dtype(df_copy[col]):
                        fill_value = df_copy[col].mean() if strategy == 'mean' else df_copy[col].median()
                        df_copy[col] = df_copy[col].fillna(fill_value)
                    elif strategy == 'mode':
                        fill_value = df_copy[col].mode()[0]
                        df_copy[col] = df_copy[col].fillna(fill_value)
                except Exception:
                    continue
        self.df = df_copy
        return self.df

    def handle_outliers(self, column: str, strategy: str = 'iqr'):
        """
        Handles outliers in a numerical column using the IQR method safely.
        
        Args:
            column (str): The numerical column to handle outliers in.
            strategy (str): The method to use. Currently supports 'iqr'.
        """
        df_copy = self.df.copy()
        if column in df_copy.columns and pd.api.types.is_numeric_dtype(df_copy[column]):
            if strategy == 'iqr':
                Q1 = df_copy[column].quantile(0.25)
                Q3 = df_copy[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                df_copy[column] = np.where(
                    df_copy[column] < lower_bound,
                    lower_bound,
                    df_copy[column]
                )
                df_copy[column] = np.where(
                    df_copy[column] > upper_bound,
                    upper_bound,
                    df_copy[column]
                )
        self.df = df_copy
        return self.df

    def get_cleaned_data(self):
        """
        Returns the cleaned dataframe.
        """
        return self.df.copy()