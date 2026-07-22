-- =============================================
-- Stored Queries for E-Commerce Business Intelligence
-- Reusable SQL snippets for common analytical tasks
-- =============================================

-- Sales by Category and Month
-- Parameters: @start_date, @end_date (in format 'YYYY-MM-DD')
SELECT
    d.year,
    d.month,
    d.month_name,
    p.product_category_name_english,
    SUM(fs.total_price) AS revenue,
    SUM(fs.profit) AS profit,
    SUM(fs.quantity) AS quantity_sold
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
JOIN dim_products p ON fs.product_id = p.product_id
WHERE d.date BETWEEN @start_date AND @end_date
GROUP BY d.year, d.month, d.month_name, p.product_category_name_english
ORDER BY d.year, d.month, revenue DESC;

-- Top 10 Products by Revenue (Last 30 Days)
-- Parameter: @days_ago (default 30)
SELECT
    p.product_id,
    p.product_category_name_english,
    SUM(fs.total_price) AS revenue,
    SUM(fs.quantity) AS quantity_sold
FROM fact_sales fs
JOIN dim_date d ON fs.date_id = d.date_id
JOIN dim_products p ON fs.product_id = p.product_id
WHERE d.date >= DATE('now', '-@days_ago days')
GROUP BY p.product_id, p.product_category_name_english
ORDER BY revenue DESC
LIMIT 10;

-- Customer Segmentation by RFM Score
-- Uses Recency, Frequency, Monetary to assign scores
WITH rfm AS (
    SELECT
        c.customer_id,
        c.customer_unique_id,
        -- Recency: days since last purchase (lower is better)
        CAST((julianday('now') - julianday(MAX(d.date))) AS INTEGER) AS recency,
        -- Frequency: number of orders
        COUNT(DISTINCT fs.order_id) AS frequency,
        -- Monetary: total spent
        SUM(fs.total_price) AS monetary
    FROM dim_customers c
    LEFT JOIN fact_sales fs ON c.customer_id = fs.customer_id
    LEFT JOIN dim_date d ON fs.date_id = d.date_id
    GROUP BY c.customer_id, c.customer_unique_id
),
rfm_scored AS (
    SELECT
        customer_id,
        customer_unique_id,
        recency,
        frequency,
        monetary,
        -- Score each dimension 1-5 (5 is best)
        NTILE(5) OVER (ORDER BY recency DESC) AS recency_score,  -- higher recency = worse
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM rfm
)
SELECT
    customer_id,
    customer_unique_id,
    recency,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    (recency_score + frequency_score + monetary_score) AS rfm_score,
    CASE
        WHEN (recency_score + frequency_score + monetary_score) >= 13 THEN 'Champions'
        WHEN (recency_score + frequency_score + monetary_score) >= 10 THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'At Risk'
        WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Lost'
        WHEN frequency_score = 1 AND monetary_score = 1 THEN 'New Customers'
        WHEN monetary_score >= 4 THEN 'Big Spenders'
        ELSE 'Need Attention'
    END AS rfm_segment
FROM rfm_scored
ORDER BY rfm_score DESC;

-- Month-over-Month Growth
SELECT
    current_month.year AS year,
    current_month.month AS month,
    current_month.monthly_revenue,
    previous_month.monthly_revenue AS prev_month_revenue,
    ROUND(((current_month.monthly_revenue - previous_month.monthly_revenue) / previous_month.monthly_revenue) * 100, 2) AS mom_growth_percent
FROM v_monthly_sales current_month
LEFT JOIN v_monthly_sales previous_month
    ON current_month.year = previous_month.year
    AND current_month.month = previous_month.month - 1
WHERE previous_month.monthly_revenue IS NOT NULL
ORDER BY current_month.year, current_month.month;

-- Year-over-Year Growth
SELECT
    current_year.year,
    current_year.yearly_revenue,
    previous_year.yearly_revenue AS prev_year_revenue,
    ROUND(((current_year.yearly_revenue - previous_year.yearly_revenue) / previous_year.yearly_revenue) * 100, 2) AS yoy_growth_percent
FROM v_yearly_sales current_year
LEFT JOIN v_yearly_sales previous_year
    ON current_year.year = previous_year.year + 1
WHERE previous_year.yearly_revenue IS NOT NULL
ORDER BY current_year.year;

-- Cohort Analysis: Monthly Cohort Retention
-- Groups customers by first purchase month and tracks their subsequent purchases
WITH first_purchase AS (
    SELECT
        fs.customer_id,
        MIN(d.date) AS first_purchase_date
    FROM fact_sales fs
    JOIN dim_date d ON fs.date_id = d.date_id
    GROUP BY fs.customer_id
),
cohort AS (
    SELECT
        fp.customer_id,
        strftime('%Y-%m', fp.first_purchase_date) AS cohort_month,
        d.date AS purchase_date,
        (strftime('%Y', d.date) || '-' || strftime('%m', d.date)) AS purchase_month
    FROM first_purchase fp
    JOIN fact_sales fs ON fp.customer_id = fs.customer_id
    JOIN dim_date d ON fs.date_id = d.date_id
),
cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_customers
    FROM cohort
    GROUP BY cohort_month
),
cohort_retention AS (
    SELECT
        c.cohort_month,
        c.purchase_month,
        COUNT(DISTINCT c.customer_id) AS active_customers
    FROM cohort c
    GROUP BY c.cohort_month, c.purchase_month
)
SELECT
    cr.cohort_month,
    cr.purchase_month,
    cr.active_customers,
    cs.total_customers,
    ROUND((cr.active_customers * 100.0) / cs.total_customers, 2) AS retention_percentage
FROM cohort_retention cr
JOIN cohort_size cs ON cr.cohort_month = cs.cohort_month
ORDER BY cr.cohort_month, cr.purchase_month;