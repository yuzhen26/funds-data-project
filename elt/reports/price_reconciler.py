"""Module to reconcile the prices of fund positions with reference prices for equities and bonds."""

from pathlib import Path

import pandas as pd

from pandas import Series
from overrides import override

from constants.constants import (
    AssetType,
    SecurityIdentifier,
    FundPositionsColumnNames,
    TableNames,
    FilePaths,
)
from elt.data.db_manager import DbManager
from elt.base.report_generator import ReportGenerator
from utils.date_utils import DateUtils
from utils.file_utils import FileUtils


class PriceReconciler(ReportGenerator):
    """A class to reconcile the prices of fund positions with reference prices for equities and bonds.

    This class loads the necessary fund positions and price data, reconciles the prices based on asset type (equity or bond),
    calculates price differences, and generates a report for the reconciliation.

    Attributes:
        db (DbManager): The database manager instance for querying data.
        bond_prices (pd.DataFrame): Dataframe containing bond prices.
        equity_prices (pd.DataFrame): Dataframe containing equity prices.
        fund_positions (pd.DataFrame): Dataframe containing the fund positions.
    """

    def __init__(self, db: DbManager):
        """Initializes the PriceReconciler with a database manager.

        Args:
            db (DbManager): An instance of the database manager to interact with the database.
        """
        super().__init__(db)
        self.bond_prices = None
        self.equity_prices = None
        self.fund_positions = None

    @override
    def load_and_prepare_data(self):
        """Loads and prepares the data for price reconciliation.

        This method loads the fund positions, equity prices, and bond prices from the database, and parses the datetime column.
        Additionally, it ensures that the ISIN for bond assets is correctly assigned.

        Raises:
            RuntimeError: If there is an issue loading or parsing the data.
        """
        try:
            self.fund_positions = DateUtils.parse_datetime_column(
                self.db.load_table(TableNames.FUND_POSITIONS.value),
                FundPositionsColumnNames.DATETIME.value,
            )
            self.equity_prices = DateUtils.parse_datetime_column(
                self.db.load_table(TableNames.EQUITY_PRICES.value),
                FundPositionsColumnNames.DATETIME.value,
            )
            self.bond_prices = DateUtils.parse_datetime_column(
                self.db.load_table(TableNames.BOND_PRICES.value),
                FundPositionsColumnNames.DATETIME.value,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to load and parse data tables: {e}")

        # Fix ISIN column in fund data for bonds
        bond_mask = (
            self.fund_positions[FundPositionsColumnNames.FINANCIAL_TYPE.value]
            == AssetType.BONDS.value
        )
        self.fund_positions.loc[bond_mask, FundPositionsColumnNames.ISIN.value] = (
            self.fund_positions.loc[bond_mask, FundPositionsColumnNames.SYMBOL.value]
        )

    @override
    def generate_report(self) -> None:
        """Generates the price reconciliation report.

        This method reconciles the fund positions with the reference prices for equities and bonds, calculates the price
        difference, and exports the results to an Excel file.

        Raises:
            RuntimeError: If an error occurs during the report generation.
        """
        reconciler_df = self.reconcile_prices()
        FileUtils.export_to_excel(
            df=reconciler_df,
            output_path=Path(FilePaths.PRICE_RECONCILIATION_REPORT_PATH.value),
            columns=[
                FundPositionsColumnNames.FUND_NAME.value,
                FundPositionsColumnNames.DATETIME.value,
                FundPositionsColumnNames.FINANCIAL_TYPE.value,
                FundPositionsColumnNames.SYMBOL.value,
                FundPositionsColumnNames.ISIN.value,
                FundPositionsColumnNames.PRICE.value,
                FundPositionsColumnNames.PRICE_REF.value,
                FundPositionsColumnNames.PRICE_DIFF.value,
            ],
        )

    def reconcile_prices(self) -> pd.DataFrame:
        """Reconciles the fund prices with reference prices for equities and bonds.

        This method filters the fund positions by asset type (equity or bond), merges them with the reference prices,
        and calculates the price difference.

        Returns:
            pd.DataFrame: The reconciled fund prices with the calculated price differences.
        """
        equity_report = self._reconcile_asset_type(
            fund_df=self._filter_by_asset_type(AssetType.EQUITY),
            reference_df=self.equity_prices,
            key=SecurityIdentifier.SYMBOL,
        )
        bonds_report = self._reconcile_asset_type(
            fund_df=self._filter_by_asset_type(AssetType.BONDS),
            reference_df=self.bond_prices,
            key=SecurityIdentifier.ISIN,
        )
        return pd.concat([equity_report, bonds_report], ignore_index=True)

    def _filter_by_asset_type(self, asset_type: AssetType):
        return self.fund_positions[
            self.fund_positions[FundPositionsColumnNames.FINANCIAL_TYPE.value]
            == asset_type.value
        ]

    def _reconcile_asset_type(
        self, fund_df: pd.DataFrame, reference_df: pd.DataFrame, key: SecurityIdentifier
    ) -> pd.DataFrame:
        all_rows: list[pd.DataFrame] = []

        for dt in fund_df[FundPositionsColumnNames.DATETIME.value].dropna().unique():
            subset = fund_df[
                fund_df[FundPositionsColumnNames.DATETIME.value] == dt
            ].copy()
            latest_prices = self.get_latest_price(
                reference_df, FundPositionsColumnNames.DATETIME.value, key.value, dt
            )
            merged = pd.merge(
                subset, latest_prices, on=key.value, how="left", suffixes=("", "_ref")
            )
            merged = self._calculate_price_diff(merged)
            all_rows.append(merged)

        return pd.concat(all_rows, ignore_index=True)

    @staticmethod
    def _calculate_price_diff(df: pd.DataFrame) -> pd.DataFrame:
        df[FundPositionsColumnNames.PRICE_DIFF.value] = (
            df[FundPositionsColumnNames.PRICE.value]
            - df[FundPositionsColumnNames.PRICE_REF.value]
        ).round(2)
        return df

    @staticmethod
    def get_latest_price(
        df: pd.DataFrame, date_col: str, key_col: str, date_value: pd.Timestamp
    ) -> Series:
        """Retrieves the latest price for a given asset based on the date.

        Args:
            df (pd.DataFrame): The dataframe containing the reference prices.
            date_col (str): The name of the date column.
            key_col (str): The name of the key column (either SYMBOL or ISIN).
            date_value (pd.Timestamp): The date to match the reference price against.

        Returns:
            Series: The latest price data for the given key and date.
        """
        return (
            df[df[date_col] <= date_value]
            .sort_values(by=[key_col, date_col], ascending=[True, False])
            .drop_duplicates(subset=[key_col])
        )
