"""This module contains various enumerations (Enums) used throughout the application.

These include:
- File paths
- Table names
- Asset types
- Security identifiers
- Fund position column names
- Performance column names
"""

from enum import Enum


class FilePaths(Enum):
    """Enumeration for file paths used in the application.

    Attributes:
        MASTER_REFERENCE_SQL_FILE_PATH (str): Path to the master reference SQL file.
        EXTERNAL_FUNDS_FOLDER_PATH (str): Path to the external funds folder.
        PRICE_RECONCILIATION_REPORT_PATH (str): Path to the price reconciliation report.
        FUND_PERFORMANCE_REPORT_PATH (str): Path to the fund performance report.
    """

    MASTER_REFERENCE_SQL_FILE_PATH = "data/master-reference-sql.sql"
    EXTERNAL_FUNDS_FOLDER_PATH = "data/external_funds"
    PRICE_RECONCILIATION_REPORT_PATH = "reports/price_reconciliation_report.xlsx"
    FUND_PERFORMANCE_REPORT_PATH = "reports/fund_performance_report.xlsx"


class TableNames(Enum):
    """Enumeration for table names used in the database.

    Attributes:
        FUND_POSITIONS (str): Table name for fund positions.
        EQUITY_PRICES (str): Table name for equity prices.
        BOND_PRICES (str): Table name for bond prices.
    """

    FUND_POSITIONS = "fund_positions"
    EQUITY_PRICES = "equity_prices"
    BOND_PRICES = "bond_prices"


class AssetType(Enum):
    """Enumeration for asset types.

    Attributes:
        EQUITY (str): Represents equities.
        BONDS (str): Represents government bonds.
    """

    EQUITY = "Equities"
    BONDS = "Government Bond"


class SecurityIdentifier(Enum):
    """Enumeration for security identifiers used to reference assets.

    Attributes:
        SYMBOL (str): The symbol identifier for the asset.
        ISIN (str): The ISIN (International Securities Identification Number) identifier.
    """

    SYMBOL = "SYMBOL"
    ISIN = "ISIN"


class FundPositionsColumnNames(Enum):
    """Enumeration for column names in the fund positions table.

    Attributes:
        DATETIME (str): The datetime of the record.
        FINANCIAL_TYPE (str): The financial type of the asset (e.g., equity or bond).
        FUND_NAME (str): The name of the fund.
        SYMBOL (str): The symbol of the asset.
        ISIN (str): The ISIN of the asset.
        PRICE (str): The price of the asset.
        PRICE_REF (str): The reference price of the asset.
        PRICE_DIFF (str): The difference between the price and reference price.
        MARKET_VALUE (str): The market value of the asset.
        REALISED_PL (str): The realised profit or loss of the asset.
    """

    DATETIME = "DATETIME"
    FINANCIAL_TYPE = "FINANCIAL TYPE"
    FUND_NAME = "FUND NAME"
    SYMBOL = "SYMBOL"
    ISIN = "ISIN"
    PRICE = "PRICE"
    PRICE_REF = "PRICE_ref"
    PRICE_DIFF = "price_diff"
    MARKET_VALUE = "MARKET VALUE"
    REALISED_PL = "REALISED P/L"


class PerformanceColumnNames(Enum):
    """Enumeration for column names related to fund performance metrics.

    Attributes:
        MONTH (str): The month of the record.
        MV_START (str): The starting market value for the best rate of return calculation.
        RETURN (str): The rate of return for the asset.
    """

    MONTH = "month"
    MV_START = "MV_start"
    RETURN = "rate_of_return"
