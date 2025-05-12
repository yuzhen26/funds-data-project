"""This module provides utility functions for handling file operations, including extracting fund names from file names, listing CSV files in a given folder, extracting dates from file names, and exporting data to Excel.

Functions:
- extract_fund_names: Extracts fund names from a file name.
- list_csv_files: Lists all CSV files in a given directory.
- extract_date_from_file_name: Extracts a date from a file name based on multiple patterns.
- export_to_excel: Exports a DataFrame to an Excel file.

"""

import re
from pathlib import Path

import pandas as pd
from dateutil import parser


class FileUtils:
    """A utility class that provides various file handling operations including extracting fund names, listing CSV files, and processing date information from file names.

    This class also provides functionality to export data to Excel.
    """

    @staticmethod
    def extract_fund_names(file_name: str) -> str | None:
        """Extracts the fund name from the given file name.

        Args:
            file_name (str): The name of the file from which to extract the fund name.

        Returns:
            str | None: The fund name if found in the predefined list, otherwise None.
        """
        funds_list = [
            "Whitestone",
            "Wallington",
            "Catalysm",
            "Belaware",
            "Gohen",
            "Applebead",
            "Magnum",
            "Trustmind",
            "Leeder",
            "Virtous",
        ]
        for fund in funds_list:
            if fund in file_name:
                return fund
        return None

    @staticmethod
    def list_csv_files(folder: str):
        """Lists all CSV files in the given folder.

        Args:
            folder (str): The directory to search for CSV files.

        Returns:
            list: A list of Path objects representing CSV files in the specified folder.
        """
        fund_files = list(Path(folder).glob("*.csv"))
        return fund_files

    @staticmethod
    def extract_date_from_file_name(file_name: str) -> str | None:
        """Extracts a date from a file name using multiple possible date formats.

        Args:
            file_name (str): The name of the file from which to extract the date.

        Returns:
            str | None: The extracted date in "YYYY-MM-DD" format, or None if no valid date is found.
        """
        patterns = [
            r"\b\d{4}[-_]\d{2}[-_]\d{2}\b",  # YYYY-MM-DD or YYYY_MM_DD
            r"\b\d{8}\b",  # YYYYMMDD
            r"\b\d{2}[-_]\d{2}[-_]\d{4}\b",  # DD-MM-YYYY or MM-DD-YYYY
            r"\b\d{4}[-_]\d{2}\b",  # YYYY-MM or YYYY_MM
            r"\b\d{6}\b",  # YYYYMM
        ]

        for pattern in patterns:
            match = re.search(pattern, file_name)
            if match:
                try:
                    dt = parser.parse(match.group(), dayfirst=False, yearfirst=True)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return None

    @staticmethod
    def export_to_excel(df: pd.DataFrame, output_path: Path, columns: list = None):
        """Exports a DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): The DataFrame to export.
            output_path (Path): The destination file path for the Excel report.
            columns (list, optional): A list of columns to include in the exported file. Defaults to None.

        Raises:
            ValueError: If the DataFrame is empty.
            KeyError: If any specified columns are missing in the DataFrame.
        """
        try:
            if df.empty:
                raise ValueError("The DataFrame is empty. Nothing to export.")

            if columns:
                missing_cols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    raise KeyError(
                        f"The following columns are missing from the DataFrame: {missing_cols}"
                    )
                df = df[columns]

            output_path.parent.mkdir(
                parents=True, exist_ok=True
            )  # Ensure output directory exists
            df.to_excel(output_path, index=False)
            print(f"Excel report saved to: {output_path}")

        except Exception as e:
            print(f"Failed to export Excel report to {output_path}: {e}")
