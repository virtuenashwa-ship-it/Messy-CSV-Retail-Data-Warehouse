# Messy CSV / Retail Data Warehouse

An end-to-end ETL data warehouse pipeline that ingests raw, messy retail CSV exports, cleans inconsistent dates, currency strings, nulls, and duplicate records, and loads a relational star-style schema in **SQLite** using **Python** and **Pandas**.

## Architecture Overview

This pipeline separates raw CSV ingestion from data cleansing, dimensional modeling, and SQL reporting:

1. **Extract (`src/extract.py`):** Scans `data/raw/` for `.csv` files, reads columns as strings to preserve raw values, attaches `source_file` lineage metadata, and combines staging rows into a single DataFrame.
2. **Transform (`src/transform.py`):** Trims and normalizes text fields, parses mixed date formats into ISO `YYYY-MM-DD`, strips currency symbols/commas (`R`, `ZAR`, `,`) into numeric ZAR values, filters invalid quantities or prices, deduplicates by `order_id`, calculates `gross_revenue_zar`, and splits data into `dim_customers`, `dim_products`, and `fact_sales`.
3. **Load & Model (`src/load.py` & `sql/schema.sql`):** Initializes the relational schema in SQLite (`data/retail_warehouse.db`), upserts dimension and fact records (`ON CONFLICT ... DO UPDATE`) so re-runs stay idempotent, and exposes the `vw_daily_category_sales` reporting view.
4. **Orchestration (`src/pipeline.py`):** Executes extraction, transformation, SQLite loading, and summary reporting in sequence with console and file logging (`retail_warehouse.log`).

## Project Structure

```text
retail-data-warehouse/
├── config/
│   └── settings.py          # Directory paths and database/schema file locations
├── data/
│   └── raw/                 # Incoming messy retail CSV files (ignored via .gitignore)
├── sql/
│   └── schema.sql           # Dimension/fact DDL tables and vw_daily_category_sales view
├── src/
│   ├── extract.py           # Reads messy CSVs and attaches source_file metadata
│   ├── transform.py         # Cleans dates, ZAR currency, nulls, duplicates, and fact metrics
│   ├── load.py              # SQLite schema setup and idempotent dimension/fact upserts
│   └── pipeline.py          # End-to-end pipeline runner with logging and SQL view output
├── requirements.txt         # Project dependencies
├── .gitignore               # Excludes raw data, SQLite databases, logs, and cache files
└── README.md                # Project documentation
