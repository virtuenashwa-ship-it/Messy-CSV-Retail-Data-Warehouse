import logging
import sqlite3
import pandas as pd
from config.settings import DB_PATH, SCHEMA_PATH

logger = logging.getLogger(__name__)


def load_warehouse(tables: dict[str, pd.DataFrame]) -> None:
    """Create schema if needed and upsert/append dimension and fact tables into SQLite."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)

        for _, row in tables["dim_customers"].iterrows():
            conn.execute(
                """
                INSERT INTO dim_customers (customer_id, customer_name, region)
                VALUES (?, ?, ?)
                ON CONFLICT(customer_id) DO UPDATE SET
                    customer_name = excluded.customer_name,
                    region = excluded.region
                """,
                (row["customer_id"], row["customer_name"], row["region"]),
            )

        for _, row in tables["dim_products"].iterrows():
            conn.execute(
                """
                INSERT INTO dim_products (sku, product_name, category, unit_price_zar)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(sku) DO UPDATE SET
                    product_name = excluded.product_name,
                    category = excluded.category,
                    unit_price_zar = excluded.unit_price_zar
                """,
                (row["sku"], row["product_name"], row["category"], float(row["unit_price_zar"])),
            )

        for _, row in tables["fact_sales"].iterrows():
            conn.execute(
                """
                INSERT INTO fact_sales (order_id, order_date, customer_id, sku, quantity, gross_revenue_zar)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    order_date = excluded.order_date,
                    customer_id = excluded.customer_id,
                    sku = excluded.sku,
                    quantity = excluded.quantity,
                    gross_revenue_zar = excluded.gross_revenue_zar
                """,
                (
                    row["order_id"],
                    row["order_date"],
                    row["customer_id"],
                    row["sku"],
                    int(row["quantity"]),
                    float(row["gross_revenue_zar"]),
                ),
            )

    logger.info("Loaded warehouse tables into %s", DB_PATH.name)
