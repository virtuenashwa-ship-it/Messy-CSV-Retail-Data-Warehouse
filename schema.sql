CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_products (
    sku TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price_zar REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    gross_revenue_zar REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers (customer_id),
    FOREIGN KEY (sku) REFERENCES dim_products (sku)
);

CREATE VIEW IF NOT EXISTS vw_daily_category_sales AS
SELECT
    f.order_date,
    p.category,
    d.region,
    COUNT(f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units,
    ROUND(SUM(f.gross_revenue_zar), 2) AS total_revenue_zar
FROM fact_sales f
JOIN dim_products p ON f.sku = p.sku
JOIN dim_customers d ON f.customer_id = d.customer_id
GROUP BY f.order_date, p.category, d.region
ORDER BY f.order_date DESC, total_revenue_zar DESC;
