"""Tests for the price reconciliation functionality in the reporting module."""

import pandas as pd
import pytest
from unittest.mock import patch


from elt.reports.price_reconciler import PriceReconciler
from elt.data.db_manager import DbManager
from constants.constants import FundPositionsColumnNames, AssetType, SecurityIdentifier


@pytest.fixture
def mock_db():
    """Creates a DbManager instance."""
    db = DbManager()
    return db


@pytest.fixture
def sample_fund_data():
    """Sets up the fund data."""
    return pd.DataFrame(
        {
            FundPositionsColumnNames.FINANCIAL_TYPE.value: ["Equities", "Bonds"],
            FundPositionsColumnNames.SYMBOL.value: ["AAPL", "BOND123"],
            FundPositionsColumnNames.ISIN.value: [None, "ISIN123"],
            FundPositionsColumnNames.DATETIME.value: [
                pd.Timestamp("2023-12-01"),
                pd.Timestamp("2023-12-01"),
            ],
            FundPositionsColumnNames.PRICE.value: [150, 101],
        }
    )


@pytest.fixture
def sample_price_data():
    """Sets up the price data."""
    return pd.DataFrame(
        {
            FundPositionsColumnNames.SYMBOL.value: ["AAPL"],
            FundPositionsColumnNames.ISIN.value: ["ISIN123"],
            FundPositionsColumnNames.DATETIME.value: [pd.Timestamp("2023-11-30")],
            FundPositionsColumnNames.PRICE_REF.value: [148],
        }
    )


@patch("elt.reports.price_reconciler.FileUtils.export_to_excel")
def test_generate_report(mock_export, mock_db, sample_fund_data, sample_price_data):
    """Tests that generate report and export are being called once."""
    # Patch internal data loading and processing
    reconciler = PriceReconciler(mock_db)
    reconciler.fund_positions = sample_fund_data
    reconciler.equity_prices = sample_price_data.rename(
        columns={
            FundPositionsColumnNames.PRICE_REF.value: FundPositionsColumnNames.PRICE.value
        }
    )
    reconciler.bond_prices = sample_price_data.rename(
        columns={
            FundPositionsColumnNames.PRICE_REF.value: FundPositionsColumnNames.PRICE.value
        }
    )

    # Patch internal methods
    with patch.object(reconciler, "reconcile_prices", return_value=sample_fund_data):
        reconciler.generate_report()
        mock_export.assert_called_once()


def test_filter_by_asset_type_equity(mock_db, sample_fund_data):
    """Tests if the data is filtered correctly based on the asset type."""
    reconciler = PriceReconciler(mock_db)
    reconciler.fund_positions = sample_fund_data
    equities = reconciler._filter_by_asset_type(AssetType.EQUITY)
    equity_types = equities[FundPositionsColumnNames.FINANCIAL_TYPE.value]
    assert equity_types.eq(AssetType.EQUITY.value).all()


def test_calculate_price_diff():
    """Test the calculation of the price difference is done correctly."""
    df = pd.DataFrame(
        {
            FundPositionsColumnNames.PRICE.value: [150],
            FundPositionsColumnNames.PRICE_REF.value: [148],
        }
    )
    result = PriceReconciler._calculate_price_diff(df)
    assert result[FundPositionsColumnNames.PRICE_DIFF.value].iloc[0] == 2.00


def test_get_latest_price():
    """Tests if the latest price for a given asset is retrieved correctly based on the date."""
    price_df = pd.DataFrame(
        {
            FundPositionsColumnNames.DATETIME.value: [
                pd.Timestamp("2023-11-30"),
                pd.Timestamp("2023-11-15"),
            ],
            FundPositionsColumnNames.SYMBOL.value: ["AAPL", "AAPL"],
            FundPositionsColumnNames.PRICE_REF.value: [148, 147],
        }
    )
    latest = PriceReconciler.get_latest_price(
        price_df,
        FundPositionsColumnNames.DATETIME.value,
        SecurityIdentifier.SYMBOL.value,
        pd.Timestamp("2023-12-01"),
    )
    assert latest.iloc[0][FundPositionsColumnNames.PRICE_REF.value] == 148
