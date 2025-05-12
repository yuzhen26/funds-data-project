"""Module to analyze the performance of funds based on their market value and realized P&L across time."""

from pathlib import Path
from overrides import override

import pandas as pd

from constants.constants import (
    FundPositionsColumnNames,
    PerformanceColumnNames,
    TableNames,
    FilePaths,
)
from elt.data.db_manager import DbManager
from elt.base.report_generator import ReportGenerator
from utils.date_utils import DateUtils
from utils.file_utils import FileUtils


class PerformanceAnalyzer(ReportGenerator):
    """Class to analyze the performance of funds based on their market value and realized P&L.

    This class calculates the monthly return for each fund and generates a report of the top-performing funds.

    Attributes:
        db (DbManager): The database manager instance for querying data.
        fund_positions (pd.DataFrame): The dataframe containing the fund positions data.
    """

    def __init__(self, db: DbManager):
        """Initializes the PerformanceAnalyzer with a database manager.

        Args:
            db (DbManager): An instance of the database manager to interact with the database.
        """
        super().__init__(db)
        self.fund_positions = None

    @override
    def load_and_prepare_data(self):
        """Loads and prepares the fund positions data.

        This method retrieves the fund positions from the database and processes the data by parsing the datetime column
        and adding the month for each entry.

        Raises:
            RuntimeError: If the data cannot be loaded or prepared.
        """
        try:
            df = self.db.load_table(TableNames.FUND_POSITIONS.value)
            self.fund_positions = DateUtils.parse_datetime_column_and_add_month(
                df, FundPositionsColumnNames.DATETIME.value
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load and prepare fund positions: {e}")

    @override
    def generate_report(self) -> None:
        """Generates a report for the top-performing funds.

        This method calculates the monthly returns, identifies the top-performing funds, and exports the results to an Excel file.

        Raises:
            RuntimeError: If an error occurs during report generation.
        """
        try:
            returns_df = self.calculate_monthly_returns()
            top_funds = self.get_top_performing_funds(returns_df)
            FileUtils.export_to_excel(
                df=top_funds,
                output_path=Path(FilePaths.FUND_PERFORMANCE_REPORT_PATH.value),
            )
        except Exception as e:
            raise RuntimeError(f"Error during report generation: {e}")

    def calculate_monthly_returns(self) -> pd.DataFrame:
        """Calculates the monthly returns for each fund.

        This method aggregates data by month, calculates the market value at the start of the month, and computes the return
        for each fund.

        Returns:
            pd.DataFrame: The dataframe containing the monthly returns for each fund.

        Raises:
            KeyError: If a required column is missing from the fund positions data.
            RuntimeError: If the calculation of monthly returns fails.
        """
        try:
            monthly_agg = self._aggregate_monthly_data()
            monthly_agg = self._calculate_mv_start(monthly_agg)
            monthly_agg = self._compute_returns(monthly_agg)
            return monthly_agg
        except KeyError as e:
            raise KeyError(f"Missing expected column in fund positions: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to calculate monthly returns: {e}")

    def _aggregate_monthly_data(self) -> pd.DataFrame:
        return (
            self.fund_positions.groupby(
                [
                    FundPositionsColumnNames.FUND_NAME.value,
                    PerformanceColumnNames.MONTH.value,
                ]
            )
            .agg(
                MV_end=(FundPositionsColumnNames.MARKET_VALUE.value, "sum"),
                realized_pnl=(FundPositionsColumnNames.REALISED_PL.value, "sum"),
            )
            .reset_index()
        )

    @staticmethod
    def get_top_performing_funds(returns_df: pd.DataFrame) -> pd.DataFrame:
        """Retrieves the top-performing funds based on the highest return for each month.

        Args:
            returns_df (pd.DataFrame): The dataframe containing the returns for each fund.

        Returns:
            pd.DataFrame: The dataframe containing the top-performing funds for each month.
        """
        top_performers = (
            returns_df.sort_values(PerformanceColumnNames.RETURN.value, ascending=False)
            .groupby(PerformanceColumnNames.MONTH.value)
            .head(1)
        )
        output = top_performers.sort_values(
            PerformanceColumnNames.MONTH.value, ascending=True
        ).reset_index(drop=True)
        return output

    @staticmethod
    def _calculate_mv_start(df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(
            by=[
                FundPositionsColumnNames.FUND_NAME.value,
                PerformanceColumnNames.MONTH.value,
            ]
        )
        df[PerformanceColumnNames.MV_START.value] = df.groupby(
            FundPositionsColumnNames.FUND_NAME.value
        )["MV_end"].shift(1)
        return df.dropna(subset=[PerformanceColumnNames.MV_START.value])

    @staticmethod
    def _compute_returns(df: pd.DataFrame) -> pd.DataFrame:
        df[PerformanceColumnNames.RETURN.value] = (
            (
                df["MV_end"]
                - df[PerformanceColumnNames.MV_START.value]
                + df["realized_pnl"]
            )
            / df[PerformanceColumnNames.MV_START.value]
        ).round(4)
        return df
