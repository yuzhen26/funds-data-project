"""Tests for the performance analyzer functionality in the reporting module."""

import pandas as pd
from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path

from elt.reports.performance_analyzer import PerformanceAnalyzer
from constants.constants import (
    FundPositionsColumnNames,
    PerformanceColumnNames,
    FilePaths,
)


@pytest.fixture
def mock_db():
    """Creates a mock database for testing."""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_fund_positions():
    """Creates sample fund positions data."""
    return pd.DataFrame(
        {
            FundPositionsColumnNames.FUND_NAME.value: [
                "FundA",
                "FundA",
                "FundB",
                "FundB",
            ],
            FundPositionsColumnNames.DATETIME.value: pd.to_datetime(
                ["2023-01-01", "2023-02-01", "2023-01-01", "2023-02-01"]
            ),
            PerformanceColumnNames.MONTH.value: [
                "2023-01",
                "2023-02",
                "2023-01",
                "2023-02",
            ],
            FundPositionsColumnNames.MARKET_VALUE.value: [100, 110, 200, 220],
            FundPositionsColumnNames.REALISED_PL.value: [10, 15, 20, 25],
        }
    )


def test_calculate_monthly_returns(mock_db, sample_fund_positions):
    """Tests that monthly returns are calculated correctly for each fund."""
    analyzer = PerformanceAnalyzer(db=mock_db)
    analyzer.fund_positions = sample_fund_positions

    monthly_returns = analyzer.calculate_monthly_returns()
    assert not monthly_returns.empty
    assert PerformanceColumnNames.RETURN.value in monthly_returns.columns


def test_get_top_performing_funds(mock_db, sample_fund_positions):
    """Tests that best funds are computed correctly based on rate of return formula."""
    analyzer = PerformanceAnalyzer(db=mock_db)
    analyzer.fund_positions = sample_fund_positions
    returns_df = analyzer._compute_returns(
        analyzer._calculate_mv_start(analyzer._aggregate_monthly_data())
    )
    top_funds = analyzer.get_top_performing_funds(returns_df)
    assert not top_funds.empty
    assert len(top_funds[PerformanceColumnNames.MONTH.value].unique()) == len(top_funds)


@patch("elt.reports.performance_analyzer.FileUtils.export_to_excel")
def test_generate_report(mock_export, mock_db, sample_fund_positions):
    """Tests that generate report and export to excel are being called."""
    mock_db.load_table.return_value = sample_fund_positions
    analyzer = PerformanceAnalyzer(db=mock_db)
    analyzer.load_and_prepare_data()
    analyzer.generate_report()

    mock_export.assert_called_once()
    args, kwargs = mock_export.call_args
    assert isinstance(kwargs["df"], pd.DataFrame)
    assert kwargs["output_path"] == Path(FilePaths.FUND_PERFORMANCE_REPORT_PATH.value)


def test_calculate_monthly_returns_raises_if_no_data():
    """Tests that ValueError is raised if there is no data."""
    db_mock = MagicMock()
    analyzer = PerformanceAnalyzer(db=db_mock)
    analyzer.fund_positions = pd.DataFrame()  # empty DataFrame

    with pytest.raises(ValueError, match="Funds Position Data is not loaded."):
        analyzer.calculate_monthly_returns()


def test_calculate_monthly_returns_handles_single_month_data():
    """Tests that output should be empty if there is no month to compare."""
    db_mock = MagicMock()
    analyzer = PerformanceAnalyzer(db=db_mock)
    analyzer.fund_positions = pd.DataFrame(
        {
            FundPositionsColumnNames.FUND_NAME.value: ["FundA"],
            PerformanceColumnNames.MONTH.value: ["2023-01"],
            FundPositionsColumnNames.MARKET_VALUE.value: [100],
            FundPositionsColumnNames.REALISED_PL.value: [10],
        }
    )

    monthly_returns = analyzer.calculate_monthly_returns()
    # Since there's only one month, MV_START will be NaN, so it should be empty after dropna
    assert monthly_returns.empty


def test_compute_returns_zero_division_handling():
    """Tests zero division handling is done correctly."""
    df = pd.DataFrame(
        {
            "MV_end": [100],
            PerformanceColumnNames.MV_START.value: [0],  # zero start value
            "realized_pnl": [10],
        }
    )

    result = PerformanceAnalyzer._compute_returns(df.copy())
    assert pd.isna(result.loc[0, PerformanceColumnNames.RETURN.value]) or result.loc[
        0, PerformanceColumnNames.RETURN.value
    ] == float("inf")


def test_get_top_performing_funds_ties_are_handled():
    """Tests that only one fund will be returned in a case of a tie."""
    df = pd.DataFrame(
        {
            PerformanceColumnNames.MONTH.value: ["2023-01", "2023-01"],
            PerformanceColumnNames.RETURN.value: [0.1, 0.1],  # tie
            FundPositionsColumnNames.FUND_NAME.value: ["FundA", "FundB"],
        }
    )

    top_funds = PerformanceAnalyzer.get_top_performing_funds(df)
    # In case of tie, .head(1) will just return one of them
    assert len(top_funds) == 1
    assert top_funds.iloc[0][PerformanceColumnNames.MONTH.value] == "2023-01"
