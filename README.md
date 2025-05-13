# Fund Data Pipeline

An automated ETL pipeline for loading, processing, and analyzing fund position data.  
The pipeline ingests CSVs, populates a DuckDB database, reconciles fund prices with reference data, and generates Excel reports.

---

## Project Structure
```plaintext
.
├── constants/ # Enum definitions for paths, columns, etc.
├── elt/
│ ├── base/ # Abstract report generator class
│ ├── data/ # Data loading and DB access
│ ├── pipeline/ # Main pipeline orchestration
│ └── reports/ # Price reconciliation & performance reports
├── utils/ # Utility functions (date, file handling)
├── tests/ # Unit tests
├── data/ # Input CSVs and SQL files
├── reports/ # Output Excel reports
├── pyproject.toml # Poetry configuration
├── main.py # Entry point
└── README.md 
```

---

## Features

- ✅ Load fund positions from structured CSVs
- ✅ Populate DuckDB with typed, validated tables
- ✅ Reconcile prices against equity and bond reference data
- ✅ Calculate monthly fund performance (returns)
- ✅ Generate Excel reports with key metrics
- ✅ Clean, testable, and modular Python code
- ✅ Integrated with Poetry, pytest, Ruff, and docstring linting

---

## Installation
1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/fund-data-pipeline.git
cd fund-data-pipeline
```

2. **Install dependencies using Poetry**:
```bash
poetry install
```

3. **Activate the virtual environment**:
```bash
poetry shell
```

## Usage
1. **Run the ELT pipeline**:
```bash
poetry run python main.py
```

## Testing
1. **Run all tests using pytest**:
```bash
poetry run pytest
```

2. **Lint and docstring check with Ruff**:
```bash
poetry run ruff check
```

---

## Enhancements for Production Readiness
1. **Validate schema and column types on file ingested.**
2. **Add logging instead of print statements.**
3. **Parametrize input/output paths via config files.**
4. **Add data quality checks and alerting.**
5. **Automate with job scheduling (e.g., cron, Airflow)**
6. **Add Dockerfile and CI/CD pipeline (e.g., GitHub Actions)**