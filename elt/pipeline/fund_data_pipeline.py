"""Module to manage the pipeline for loading, processing, and reporting fund data."""

from pathlib import Path

from constants.constants import FilePaths
from elt.data.data_loader import DataLoader
from elt.data.db_manager import DbManager
from elt.reports.performance_analyzer import PerformanceAnalyzer

from elt.reports.price_reconciler import PriceReconciler


class FundDataPipeline:
    """A class to manage the pipeline for loading, processing, and reporting fund data.

    This class is responsible for setting up the database, loading data, and generating reports.
    It uses various components like `DataLoader` for loading data, `PriceReconciler`, and `PerformanceAnalyzer`
    for generating reports.

    Attributes:
        base_dir (Path): The base directory where input data and SQL files are located.
        db (DbManager): The database manager instance used for interacting with the database.
        loader (DataLoader): The data loader instance used for loading fund data.
        report_generators (list): A list of report generator instances used to generate reports.
    """

    def __init__(self, base_dir: Path):
        """Initializes the `FundDataPipeline` class with the base directory and sets up the necessary components.

        Args:
            base_dir (Path): The base directory where input data, SQL files, and other resources are located.
        """
        self.base_dir = base_dir
        self.db = DbManager()
        self.loader = DataLoader(db=self.db)
        self.report_generators = [
            PriceReconciler(db=self.db),
            PerformanceAnalyzer(db=self.db),
        ]

    def setup_database(self):
        """Sets up the database by running the master reference SQL file.

        This method reads the SQL file specified by `MASTER_REFERENCE_SQL_FILE_PATH`
        and executes it on the connected database to set up the required schema and tables.
        """
        sql_file_path = self.base_dir / FilePaths.MASTER_REFERENCE_SQL_FILE_PATH.value
        self.db.run_sql_file(sql_file_path=sql_file_path)

    def load_data(self):
        """Loads fund data and prepares data for report generation.

        This method loads fund positions data from the specified folder and prepares data
        for reporting by invoking `load_and_prepare_data` on each report generator.
        """
        self.loader.load_fund_positions(
            folder=self.base_dir / FilePaths.EXTERNAL_FUNDS_FOLDER_PATH.value
        )
        for generator in self.report_generators:
            generator.load_and_prepare_data()

    def generate_reports(self):
        """Generates reports using the prepared data.

        This method calls the `generate_report` method on each report generator to produce the necessary reports.
        """
        for generator in self.report_generators:
            generator.generate_report()

    def run(self):
        """Runs the entire data pipeline: sets up the database, loads data, and generates reports.

        This method is the entry point for running the entire pipeline. It sequentially
        calls `setup_database`, `load_data`, and `generate_reports` to complete the process.
        """
        self.setup_database()
        self.load_data()
        self.generate_reports()
