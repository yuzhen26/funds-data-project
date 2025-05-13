"""Module to manage database connections and executing SQL operations using DuckDB."""

import duckdb
import pandas as pd


class DbManager:
    """A class for managing database connections and executing SQL operations using DuckDB.

    This class provides functionality to connect to a DuckDB database, run SQL files,
    and load tables into pandas DataFrames.

    Attributes:
        connection (duckdb.DuckDBPyConnection): The connection object used to interact with the DuckDB database.
    """

    def __init__(self, db_path: str = ":memory:"):
        """Initializes the DbManager instance and establishes a connection to the DuckDB database.

        Args:
            db_path (str): The path to the DuckDB database file. Defaults to ":memory:" for an in-memory database.
        """
        self.connection = duckdb.connect(database=db_path)

    def run_sql_file(self, sql_file_path: str):
        """Executes a SQL file on the connected DuckDB database.

        This method reads the SQL file from the provided path and executes its contents.

        Args:
            sql_file_path (str): The file path to the SQL file to be executed.

        Raises:
            FileNotFoundError: If the specified SQL file cannot be found.
            Exception: If there is an error executing the SQL queries in the file.
        """
        try:
            with open(sql_file_path) as f:
                sql = f.read()
            self.connection.execute(sql)
        except FileNotFoundError:
            print(f"Error: The SQL file at '{sql_file_path}' was not found.")
        except Exception as e:
            print(f"Error executing SQL from file '{sql_file_path}': {e}")

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Loads a table from the DuckDB database into a pandas DataFrame.

        Args:
            table_name (str): The name of the table to load from the database.

        Returns:
            pd.DataFrame: The table data as a pandas DataFrame.

        Raises:
            Exception: If there is an error loading the table or if the table does not exist.
        """
        try:
            return self.connection.execute(f"SELECT * FROM {table_name}").fetchdf()
        except Exception as e:
            print(f"Error loading table '{table_name}': {e}")
            raise
