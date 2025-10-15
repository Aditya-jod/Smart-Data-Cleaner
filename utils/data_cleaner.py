import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np
from io import StringIO

logger = logging.getLogger("smart_data_cleaner.data_cleaner")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class DataCleaner:
    """
    A class to handle various data cleaning operations on a pandas DataFrame safely.
    Supports method chaining for a fluent interface.
    """

    ALLOWED_MISSING_STRATEGIES = {"drop", "mean", "median", "mode"}
    ALLOWED_OUTLIER_STRATEGIES = {"iqr"}

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initializes the DataCleaner with a copy of the dataframe.
        Ensures the input is a pandas DataFrame.
        """
        if not isinstance(dataframe, pd.DataFrame):
            logger.error("DataCleaner initialization failed: input not a DataFrame")
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = dataframe.copy(deep=True)  # Work on a copy to avoid modifying original data
        logger.info("DataCleaner initialized with %d rows and %d columns", *self.df.shape)

    def get_summary(self) -> Dict[str, Any]:
        """
        Generates a summary of the current state of the dataframe.
        Returns a dict with info (str), description (DataFrame), missing_values (Series), and duplicate_count (int).
        """
        info_buf = StringIO()  # Buffer to capture DataFrame info output
        try:
            self.df.info(buf=info_buf)
            info_str = info_buf.getvalue()
        except Exception as exc:
            logger.exception("Failed to get DataFrame info: %s", exc)
            info_str = "Failed to generate info."

        try:
            description = self.df.describe(include="all").T
        except Exception:
            # protect against describe failures on mixed dtypes
            description = pd.DataFrame()

        summary = {
            "info": info_str,  # DataFrame structure and types
            "description": description,  # Statistical summary
            "missing_values": self.df.isnull().sum(),  # Count of missing values per column
            "duplicate_count": int(self.df.duplicated().sum()),  # Number of duplicate rows
        }
        return summary

    def remove_duplicates(self) -> "DataCleaner":
        """
        Removes duplicate rows from the dataframe.
        Resets index after dropping duplicates.
        Returns self for method chaining.
        """
        before = self.df.shape[0]
        try:
            self.df.drop_duplicates(inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            after = self.df.shape[0]
            logger.info("Removed %d duplicate rows", before - after)
        except Exception as exc:
            logger.exception("Error removing duplicates: %s", exc)
        return self

    def handle_missing_values(self, strategy: str, columns: Optional[List[str]] = None) -> "DataCleaner":
        """
        Handles missing values in specified columns using a chosen strategy.
        Supported strategies: 'drop', 'mean', 'median', 'mode'.
        If columns not specified, applies to all columns.
        Returns self for chaining.
        """
        if not isinstance(strategy, str) or strategy not in self.ALLOWED_MISSING_STRATEGIES:
            raise ValueError(f"strategy must be one of {self.ALLOWED_MISSING_STRATEGIES}")

        if columns is None:
            columns = self.df.columns.tolist()
        if not isinstance(columns, (list, tuple)):
            raise TypeError("columns must be a list or tuple of column names")

        for col in columns:
            if col not in self.df.columns:
                logger.warning("Skipping missing-value handling for unknown column: %s", col)
                continue

            missing_count = int(self.df[col].isnull().sum())
            if missing_count == 0:
                logger.debug("No missing values in column %s. Skipping.", col)
                continue

            try:
                if strategy == "drop":
                    logger.info("Dropping %d rows where %s is missing", missing_count, col)
                    self.df.dropna(subset=[col], inplace=True)
                    self.df.reset_index(drop=True, inplace=True)
                elif strategy in {"mean", "median"}:
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        fill_value = (
                            float(self.df[col].mean()) if strategy == "mean" else float(self.df[col].median())
                        )
                        logger.info("Filling %d missing values in %s with %s=%s", missing_count, col, strategy, fill_value)
                        self.df[col].fillna(fill_value, inplace=True)
                    else:
                        logger.warning("Column %s is not numeric, cannot apply %s. Skipping.", col, strategy)
                elif strategy == "mode":
                    mode_ser = self.df[col].mode(dropna=True)
                    if not mode_ser.empty:
                        fill_value = mode_ser.iloc[0]
                        logger.info("Filling %d missing values in %s using mode=%s", missing_count, col, fill_value)
                        self.df[col].fillna(fill_value, inplace=True)
                    else:
                        logger.warning("No mode found for column %s. Skipping.", col)
            except Exception as exc:
                logger.exception("Failed to handle missing values for column %s: %s", col, exc)

        return self

    def handle_outliers(self, column: str, strategy: str = "iqr") -> "DataCleaner":
        """
        Handles outliers in a numerical column by capping them using the IQR method.
        Only applies to numeric columns. Currently supports 'iqr' strategy.
        Returns self for chaining.
        """
        if not isinstance(column, str):
            raise TypeError("column must be a string")

        if strategy not in self.ALLOWED_OUTLIER_STRATEGIES:
            raise ValueError(f"Unsupported outlier strategy: {strategy}")

        if column not in self.df.columns:
            logger.warning("Column %s not found in DataFrame. Skipping outlier handling.", column)
            return self

        if not pd.api.types.is_numeric_dtype(self.df[column]):
            logger.warning("Column %s is not numeric. Skipping outlier handling.", column)
            return self

        try:
            col_series = self.df[column].dropna()
            if col_series.empty:
                logger.debug("Column %s has no non-null values. Skipping outlier handling.", column)
                return self

            if strategy == "iqr":
                Q1 = col_series.quantile(0.25)
                Q3 = col_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                logger.info(
                    "Capping values in %s to [%s, %s] using IQR method (Q1=%s, Q3=%s, IQR=%s)",
                    column,
                    lower_bound,
                    upper_bound,
                    Q1,
                    Q3,
                    IQR,
                )
                # Use clip to cap outliers; preserve NaNs
                self.df[column] = self.df[column].clip(lower=lower_bound, upper=upper_bound)
        except Exception as exc:
            logger.exception("Failed to handle outliers for column %s: %s", column, exc)

        return self

    def convert_data_types(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        """
        Attempts to convert columns to the best possible data types.
        For object columns, tries to convert to numeric if possible.
        Uses pandas' convert_dtypes to infer optimal types.
        Returns self for chaining.
        """
        if columns is None:
            columns = self.df.columns.tolist()
        if not isinstance(columns, (list, tuple)):
            raise TypeError("columns must be a list or tuple of column names")

        for col in columns:
            if col not in self.df.columns:
                logger.debug("Skipping convert for unknown column: %s", col)
                continue
            try:
                if self.df[col].dtype == "object":
                    # Try numeric conversion first (safe)
                    converted = pd.to_numeric(self.df[col], errors="ignore")
                    self.df[col] = converted
            except Exception as exc:
                logger.exception("Failed converting column %s to numeric: %s", col, exc)

        try:
            self.df = self.df.convert_dtypes()
            logger.info("convert_data_types applied; inferred dtypes: %s", dict(self.df.dtypes))
        except Exception as exc:
            logger.exception("convert_dtypes failed: %s", exc)
        return self

    def get_cleaned_data(self) -> pd.DataFrame:
        """
        Returns a copy of the cleaned dataframe.
        Ensures the original cleaned data is not modified externally.
        """
        return self.df.copy()
