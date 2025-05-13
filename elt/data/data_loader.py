"""This module contains the `DataLoader` class, which is responsible for loading and processing data from various sources (e.g., databases, files)."""

from pathlib import Path

import pandas as pd

from constants.constants import FundPositionsColumnNames, TableNames
from elt.data.db_manager import DbManager
from utils.file_utils import FileUtils


class DataLoader:
    """A class for loading and processing data from various sources.

    This class provides functionality to load data from CSV files, enrich the data with
    additional information (like fund name and date), and save the data to a database.

    Attributes:
        db (DbManager): The database manager object used for interacting with the database.
    """

    def __init__(self, db: DbManager):
        """Initializes the DataLoader instance.

        Args:
            db (DbManager): The database manager instance used to interact with the database.
        """
        self.db = db

    def load_fund_positions(self, folder: str):
        """This method looks for CSV files in the provided folder, loads the data, adds new columns, saves the combined data into the database table specified in `TableNames.FUND_POSITIONS`.

        Args:
            folder (str): The path to the folder containing the CSV files to be loaded.

        Prints:
            A message indicating whether the data was successfully loaded into the database
            or if no valid data was found.
        """
        fund_files = FileUtils.list_csv_files(folder)
        all_dataframes = [
            self._load_and_enrich_file(file_path) for file_path in fund_files
        ]
        if all_dataframes:
            df_all = pd.concat(all_dataframes, ignore_index=True)
            self._save_to_database(df_all)
            print(
                f"Loaded validated fund_data into '{TableNames.FUND_POSITIONS.value}'."
            )
        else:
            print("No valid fund data loaded.")

    def _save_to_database(self, df_combined: pd.DataFrame) -> None:
        self.db.connection.register("temp_df", df_combined)
        self.db.connection.execute(f"""
            CREATE OR REPLACE TABLE {TableNames.FUND_POSITIONS.value} AS
            SELECT * FROM temp_df
            """)

    @staticmethod
    def _load_and_enrich_file(file_path: Path) -> pd.DataFrame:
        file_name = file_path.stem
        fund_name = FileUtils.extract_fund_names(file_name)

        df = pd.read_csv(file_path)

        df[FundPositionsColumnNames.FUND_NAME.value] = fund_name
        df[FundPositionsColumnNames.DATETIME.value] = (
            FileUtils.extract_date_from_file_name(file_name)
        )

        return df
