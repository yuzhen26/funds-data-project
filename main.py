"""Entry point for running the fund data processing pipeline."""

from pathlib import Path
from elt.pipeline.fund_data_pipeline import FundDataPipeline


def main():
    """Initializes and runs the fund data pipeline."""
    pipeline = FundDataPipeline(base_dir=Path(__file__).resolve().parent)
    pipeline.run()


if __name__ == "__main__":
    main()
