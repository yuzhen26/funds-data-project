"""This module provides utility functions for date manipulation and processing.

Functions:
- parse_datetime_column: Converts a specified column in a DataFrame to datetime format.
- parse_datetime_column_and_add_month: Converts a specified column in a DataFrame to datetime format and adds a "month" column based on the datetime.
"""

import pandas as pd


class DateUtils:
    """A utility class for date-related operations on DataFrames, specifically for parsing and manipulating datetime columns.

    Provides methods to convert columns to datetime and add month information.
    """

    @staticmethod
    def parse_datetime_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Converts the specified column in the DataFrame to datetime format.

        Args:
            df (pd.DataFrame): The DataFrame containing the column to convert.
            column (str): The name of the column to be converted to datetime.

        Returns:
            pd.DataFrame: The DataFrame with the specified column converted to datetime format.
        """
        df[column] = pd.to_datetime(df[column])
        return df

    @staticmethod
    def parse_datetime_column_and_add_month(
        df: pd.DataFrame, column: str
    ) -> pd.DataFrame:
        """Converts the specified column in the DataFrame to datetime format and adds a new column representing the month (as a Period).

        Args:
            df (pd.DataFrame): The DataFrame containing the column to convert.
            column (str): The name of the column to be converted to datetime.

        Returns:
            pd.DataFrame: The DataFrame with the specified column converted to datetime format
                          and a new "month" column added.
        """
        df[column] = pd.to_datetime(df[column])
        df["month"] = df[column].dt.to_period("M")
        return df
