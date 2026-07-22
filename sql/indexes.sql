-- =============================================
-- Indexes for E-Commerce Business Intelligence Data Warehouse
-- Created to optimize query performance on fact and dimension tables
-- =============================================

-- Drop existing indexes if they exist (for development)
DROP INDEX IF EXISTS idx_dim_date_date;
DROP INDEX IF EXISTS idx_dim_date_ymd;
DROP INDEX IF EXISTS idx_dim_date_year;
DROP INDEX IF EXISTS idx_dim_customers_state;
DROP INDEX IF EXISTS idx_dim_customers_segment;
DROP INDEX IF EXISTS idx_dim_customers_ltv;
DROP INDEX IF EXISTS idx_dim_products_category;
DROP INDEX IF EXISTS idx_dim_products_brand;
DROP INDEX IF EXISTS idx_dim_products_price;
DROP INDEX IF EXISTS idx_dim_orders_status;
DROP INDEX IF EXISTS idx_dim_orders_date;
DROP INDEX IF EXISTS idx_dim_payments_type;
DROP INDEX IF EXISTS idx_fact_sales_date;
DROP INDEX IF EXISTS idx_fact_sales_customer;
DROP INDEX IF EXISTS idx_fact_sales_product;
DROP INDEX IF EXISTS idx_fact_sales_order;
DROP INDEX IF EXISTS idx_fact_sales_payment;
DROP INDEX IF EXISTS idx_fact_sales_return;
DROP INDEX IF EXISTS idx_fact_sales_marketing;
DROP INDEX IF EXISTS idx_fact_sales_date_product;
DROP INDEX IF EXISTS idx_fact_sales_date_customer;
DROP INDEX IF EXISTS idx_fact_sales_customer_product;

-- Date Dimension Indexes
CREATE INDEX idx_dim_date_date ON dim_date(date);
CREATE INDEX idx_dim_date_ymd ON dim_date(year, month, day);
CREATE INDEX idx_dim_date_year ON dim_date(year);

-- Customer Dimension Indexes
CREATE INDEX idx_dim_customers_state ON dim_customers(customer_state);
CREATE INDEX idx_dim_customers_segment ON dim_customers(customer_segment);
CREATE INDEX idx_dim_customers_ltv ON dim_customers(customer_lifetime_value);

-- Product Dimension Indexes
CREATE INDEX idx_dim_products_category ON dim_products(product_category);
CREATE INDEX idx_dim_products_brand ON dim_products(product_brand);
CREATE INDEX idx_dim_products_price ON dim_products(product_price);

-- Order Dimension Indexes
CREATE INDEX idx_dim_orders_status ON dim_orders(order_status);
CREATE INDEX idx_dim_orders_date ON dim_orders(order_purchase_timestamp);

-- Payment Dimension Indexes
CREATE INDEX idx_dim_payments_type ON dim_payments(payment_type);

-- Fact Table Indexes (Most Important for Performance)
CREATE INDEX idx_fact_sales_date ON fact_sales(date_id);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_order ON fact_sales(order_id);
CREATE INDEX idx_fact_sales_payment ON fact_sales(payment_id);
CREATE INDEX idx_fact_sales_return ON fact_sales(return_id);
CREATE INDEX idx_fact_sales_marketing ON fact_sales(marketing_id);

-- Composite Indexes for Common Query Patterns
CREATE INDEX idx_fact_sales_date_product ON fact_sales(date_id, product_id);
CREATE INDEX idx_fact_sales_date_customer ON fact_sales(date_id, customer_id);
CREATE INDEX idx_fact_sales_customer_product ON fact_sales(customer_id, product_id);

-- Additional indexes for specific queries
CREATE INDEX idx_fact_sales_profit ON fact_sales(profit);
CREATE INDEX idx_fact_sales_total_price ON fact_sales(total_price);
CREATE INDEX idx_fact_sales_quantity ON fact_sales(quantity);

-- Indexes for dimension tables used in GROUP BY
CREATE INDEX idx_dim_products_category_brand ON dim_products(product_category, product_brand);
CREATE INDEX idx_dim_customers_state_segment ON dim_customers(customer_state, customer_segment);