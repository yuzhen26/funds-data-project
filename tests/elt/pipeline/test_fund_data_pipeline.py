"""Tests for the fund pipeline functionality in the reporting module."""

import pytest
from unittest.mock import MagicMock
from pathlib import Path
from elt.data.db_manager import DbManager
from elt.data.data_loader import DataLoader
from elt.reports.performance_analyzer import PerformanceAnalyzer
from elt.reports.price_reconciler import PriceReconciler
from elt.pipeline.fund_data_pipeline import FundDataPipeline
from constants.constants import FilePaths


@pytest.fixture
def mock_db_manager():
    """Fixture to mock DbManager."""
    return MagicMock(DbManager)


@pytest.fixture
def mock_data_loader():
    """Fixture to mock DataLoader."""
    return MagicMock(DataLoader)


@pytest.fixture
def mock_performance_analyzer():
    """Fixture to mock PerformanceAnalyzer."""
    return MagicMock(PerformanceAnalyzer)


@pytest.fixture
def mock_price_reconciler():
    """Fixture to mock PriceReconciler."""
    return MagicMock(PriceReconciler)


@pytest.fixture
def fund_data_pipeline(
    mock_db_manager, mock_data_loader, mock_performance_analyzer, mock_price_reconciler
):
    """Fixture to create an instance of FundDataPipeline with mocked dependencies."""
    pipeline = FundDataPipeline(base_dir=Path("/mock/directory"))
    pipeline.db = mock_db_manager
    pipeline.loader = mock_data_loader
    pipeline.report_generators = [mock_price_reconciler, mock_performance_analyzer]
    return pipeline


def test_setup_database(fund_data_pipeline, mock_db_manager):
    """Test the setup_database method."""
    # Arrange
    sql_file_path = (
        Path("/mock/directory") / FilePaths.MASTER_REFERENCE_SQL_FILE_PATH.value
    )

    # Act
    fund_data_pipeline.setup_database()

    # Assert
    mock_db_manager.run_sql_file.assert_called_once_with(sql_file_path=sql_file_path)


def test_load_data(
    fund_data_pipeline,
    mock_data_loader,
    mock_performance_analyzer,
    mock_price_reconciler,
):
    """Test the load_data method."""
    # Act
    fund_data_pipeline.load_data()

    # Assert that load_fund_positions is called once
    mock_data_loader.load_fund_positions.assert_called_once()

    # Assert that load_and_prepare_data is called for each report generator
    mock_performance_analyzer.load_and_prepare_data.assert_called_once()
    mock_price_reconciler.load_and_prepare_data.assert_called_once()


def test_generate_reports(
    fund_data_pipeline, mock_performance_analyzer, mock_price_reconciler
):
    """Test the generate_reports method."""
    # Act
    fund_data_pipeline.generate_reports()

    # Assert that generate_report is called for both report generators
    mock_performance_analyzer.generate_report.assert_called_once()
    mock_price_reconciler.generate_report.assert_called_once()


def test_run_pipeline(
    fund_data_pipeline,
    mock_db_manager,
    mock_data_loader,
    mock_performance_analyzer,
    mock_price_reconciler,
):
    """Test the full pipeline run method."""
    # Act
    fund_data_pipeline.run()

    # Assert that setup_database, load_data, and generate_reports were all called
    mock_db_manager.run_sql_file.assert_called_once()
    mock_data_loader.load_fund_positions.assert_called_once()
    mock_performance_analyzer.load_and_prepare_data.assert_called_once()
    mock_price_reconciler.load_and_prepare_data.assert_called_once()
    mock_performance_analyzer.generate_report.assert_called_once()
    mock_price_reconciler.generate_report.assert_called_once()
