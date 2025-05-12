"""Tests for the database manager functionality in the reporting module."""

import pytest
import pandas as pd
from pathlib import Path
from elt.data.db_manager import DbManager


@pytest.fixture
def db_manager():
    """Provides a fresh in-memory DuckDB instance."""
    return DbManager()


def test_run_sql_file_creates_table(tmp_path: Path, db_manager: DbManager):
    """Tests that sql file is read and table is created in the database correctly."""
    sql_content = """
    CREATE TABLE test_table (id INTEGER, name VARCHAR);
    INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob');
    """
    sql_file = tmp_path / "test_script.sql"
    sql_file.write_text(sql_content)

    db_manager.run_sql_file(str(sql_file))
    df = db_manager.load_table("test_table")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]
    assert df.iloc[0]["name"] == "Alice"
    assert df.iloc[1]["id"] == 2


def test_load_table_invalid_table_raises_error(db_manager: DbManager):
    """Test that error is raised when there is no such table in the database."""
    with pytest.raises(Exception):
        db_manager.load_table("non_existent_table")
