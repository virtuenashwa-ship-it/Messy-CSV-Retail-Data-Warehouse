import logging
import pandas as pd

logger = logging.getLogger(__name__)


def _clean_currency(series: pd.Series) -> pd.Series:
    cleaned = (
        series.fillna("")
        .str.replace("ZAR", "", regex=False)
        .str.replace("R", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def transform_retail_data(raw_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Clean messy retail CSV columns and split into dimension and fact tables."""
    df = raw_df.copy()

    # Normalize strings and drop exact duplicate orders
    df["order_id"] = df["order_id"].str.strip()
    df["customer_id"] = df["customer_id"].str.strip().str.upper()
    df["customer_name"] = df["customer_name"].fillna("Unknown Customer").str.strip().str.title()
    df["region"] = df["region"].fillna("Unspecified").str.strip().str.title()
    df["sku"] = df["sku"].str.strip().str.upper()
    df["product_name"] = df["product_name"].fillna("Unnamed Item").str.strip().str.title()
    df["category"] = df["category"].fillna("General").str.strip().str.title()

    # Parse mixed date formats into ISO YYYY-MM-DD
    parsed_dates = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
    df["order_date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    # Clean numeric fields
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price_zar"] = _clean_currency(df["unit_price_zar"])

    # Drop invalid/incomplete rows
    valid_mask = (
        df["order_id"].notna()
        & (df["order_id"] != "")
        & df["order_date"].notna()
        & (df["quantity"] > 0)
        & df["unit_price_zar"].notna()
        & (df["unit_price_zar"] >= 0)
    )
    df = df[valid_mask].drop_duplicates(subset=["order_id"], keep="last").copy()
    df["gross_revenue_zar"] = (df["quantity"] * df["unit_price_zar"]).round(2)

    dim_customers = (
        df[["customer_id", "customer_name", "region"]]
        .drop_duplicates(subset=["customer_id"], keep="last")
        .reset_index(drop=True)
    )

    dim_products = (
        df[["sku", "product_name", "category", "unit_price_zar"]]
        .drop_duplicates(subset=["sku"], keep="last")
        .reset_index(drop=True)
    )

    fact_sales = (
        df[["order_id", "order_date", "customer_id", "sku", "quantity", "gross_revenue_zar"]]
        .reset_index(drop=True)
    )

    logger.info(
        "Transformed into %d customers, %d products, and %d fact sales rows",
        len(dim_customers),
        len(dim_products),
        len(fact_sales),
    )

    return {
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "fact_sales": fact_sales,
    }
