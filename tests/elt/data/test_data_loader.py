"""Tests for the data loader functionality in the reporting module."""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from elt.data.db_manager import DbManager
from elt.data.data_loader import DataLoader
from constants.constants import FundPositionsColumnNames, TableNames

sample_csv_content = """SYMBOL,ISIN,FINANCIAL TYPE,MARKET VALUE,REALISED P/L,PRICE,PRICE_ref,price_diff
AAPL,US0378331005,Equities,100000,5000,150,148,2
"""


@pytest.fixture
def temp_csv_file():
    """Creates fixture of csv file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "FundA_2023-12.csv"
        with open(file_path, "w") as f:
            f.write(sample_csv_content)
        yield file_path


@pytest.fixture
def db_manager():
    """Creates fixture of db manager."""
    return DbManager()


def test_run_sql_file_and_load_table(tmp_path):
    """Tests that sql file is read and table is created in the database correctly."""
    db = DbManager()
    test_sql_file = tmp_path / "create_test.sql"
    test_sql_file.write_text(
        "CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);"
    )
    db.run_sql_file(str(test_sql_file))
    df = db.load_table("test")
    assert not df.empty
    assert df.iloc[0]["id"] == 1


@patch("elt.data.data_loader.FileUtils.list_csv_files")
@patch("elt.data.data_loader.FileUtils.extract_fund_names", return_value="FundA")
@patch(
    "elt.data.data_loader.FileUtils.extract_date_from_file_name", return_value="2023-12"
)
def test_data_loader_loads_data(
    mock_date, mock_fund, mock_list_csv, temp_csv_file, db_manager
):
    """Tests that the data loader loads the fund_positions data correctly."""
    mock_list_csv.return_value = [temp_csv_file]
    loader = DataLoader(db=db_manager)
    loader.load_fund_positions(folder=str(temp_csv_file.parent))
    df = db_manager.load_table(TableNames.FUND_POSITIONS.value)
    assert not df.empty
    assert FundPositionsColumnNames.FUND_NAME.value in df.columns
