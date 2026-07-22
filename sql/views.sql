-- =============================================
-- Views for E-Commerce Business Intelligence Data Warehouse
-- Pre-defined queries for common analytical needs
-- =============================================

-- Daily Sales Summary
CREATE VIEW IF NOT EXISTS v_daily_sales AS
SELECT
    d.date,
    SUM(fs.total_price) AS daily_revenue,
    SUM(fs.profit) AS daily_profit,
    COUNT(DISTINCT fs.order_id) AS daily_orders,
    COUNT(DISTINCT fs.customer_id) AS daily_customers,
    AVG(fs.total_price) AS avg_order_value
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
GROUP BY d.date
ORDER BY d.date;

-- Monthly Sales Summary
CREATE VIEW IF NOT EXISTS v_monthly_sales AS
SELECT
    d.year,
    d.month,
    SUM(fs.total_price) AS monthly_revenue,
    SUM(fs.profit) AS monthly_profit,
    COUNT(DISTINCT fs.order_id) AS monthly_orders,
    COUNT(DISTINCT fs.customer_id) AS monthly_customers
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- Quarterly Sales Summary
CREATE VIEW IF NOT EXISTS v_quarterly_sales AS
SELECT
    d.year,
    d.quarter,
    SUM(fs.total_price) AS quarterly_revenue,
    SUM(fs.profit) AS quarterly_profit,
    COUNT(DISTINCT fs.order_id) AS quarterly_orders,
    COUNT(DISTINCT fs.customer_id) AS quarterly_customers
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;

-- Yearly Sales Summary
CREATE VIEW IF NOT EXISTS v_yearly_sales AS
SELECT
    d.year,
    SUM(fs.total_price) AS yearly_revenue,
    SUM(fs.profit) AS yearly_profit,
    COUNT(DISTINCT fs.order_id) AS yearly_orders,
    COUNT(DISTINCT fs.customer_id) AS yearly_customers
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
GROUP BY d.year
ORDER BY d.year;

-- Product Performance
CREATE VIEW IF NOT EXISTS v_product_performance AS
SELECT
    p.product_id,
    p.product_category_name_english,
    SUM(fs.total_price) AS total_revenue,
    SUM(fs.profit) AS total_profit,
    SUM(fs.quantity) AS total_quantity_sold,
    COUNT(DISTINCT fs.order_id) AS order_count,
    AVG(fs.total_price) AS avg_order_value
FROM fact_sales fs
JOIN dim_products p ON fs.product_id = p.product_id
GROUP BY p.product_id, p.product_category_name_english
ORDER BY total_revenue DESC;

-- Customer Lifetime Value
CREATE VIEW IF NOT EXISTS v_customer_ltv AS
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(fs.order_id) AS total_orders,
    SUM(fs.total_price) AS total_spent,
    AVG(fs.total_price) AS avg_order_value,
    MAX(d.date) AS last_purchase_date,
    (julianday('now') - julianday(MAX(d.date))) AS days_since_last_purchase
FROM dim_customers c
LEFT JOIN fact_sales fs ON c.customer_id = fs.customer_id
LEFT JOIN dim_date d ON fs.date_id = d.date_id
GROUP BY c.customer_id, c.customer_unique_id, c.customer_city, c.customer_state
ORDER BY total_spent DESC;

-- Return Analysis
CREATE VIEW IF NOT EXISTS v_return_analysis AS
SELECT
    r.return_reason,
    COUNT(*) AS return_count,
    SUM(fs.total_price) AS returned_value,
    AVG(fs.total_price) AS avg_return_value
FROM fact_sales fs
JOIN dim_returns r ON fs.return_id = r.return_id
GROUP BY r.return_reason
ORDER BY return_count DESC;

-- Marketing ROI
CREATE VIEW IF NOT EXISTS v_marketing_roi AS
SELECT
    m.channel,
    m.campaign_name,
    SUM(m.budget) AS total_budget,
    SUM(m.revenue_attributed) AS attributed_revenue,
    (SUM(m.revenue_attributed) - SUM(m.budget)) AS net_profit,
    CASE
        WHEN SUM(m.budget) > 0
        THEN (SUM(m.revenue_attributed) - SUM(m.budget)) / SUM(m.budget) * 100
        ELSE 0
    END AS roi_percentage
FROM dim_marketing m
GROUP BY m.channel, m.campaign_name
ORDER BY roi_percentage DESC;

-- Inventory Turnover (placeholder - requires inventory fact table)
CREATE VIEW IF NOT EXISTS v_inventory_turnover AS
SELECT
    i.product_id,
    p.product_category_name_english,
    i.stock_quantity,
    COALESCE(SUM(fs.quantity), 0) AS units_sold_period,
    CASE
        WHEN i.stock_quantity > 0
        THEN CAST(COALESCE(SUM(fs.quantity), 0) AS REAL) / i.stock_quantity
        ELSE 0
    END AS turnover_ratio
FROM dim_inventory i
JOIN dim_products p ON i.product_id = p.product_id
LEFT JOIN fact_sales fs ON i.product_id = fs.product_id
GROUP BY i.product_id, p.product_category_name_english, i.stock_quantity;