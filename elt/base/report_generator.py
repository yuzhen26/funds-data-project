"""This module contains the base class for report generation.

It includes functionality for loading data from the database,
processing it, and generating reports.
"""

from abc import ABC, abstractmethod

from elt.data.db_manager import DbManager


class ReportGenerator(ABC):
    """A base class for generating reports.

    This class handles loading data from the database, processing the data,
    and providing the structure for generating reports in subclasses.
    """

    def __init__(self, db: DbManager):
        """Initializes the DbManager object."""
        self.db = db

    @abstractmethod
    def load_and_prepare_data(self):
        """Load and prepare data for report generation."""
        pass

    @abstractmethod
    def generate_report(self):
        """Generate the report."""
        pass
