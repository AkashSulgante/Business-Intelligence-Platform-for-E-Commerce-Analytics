-- =============================================
-- E-Commerce Business Intelligence Data Warehouse Schema
-- Contains CREATE TABLE statements for all dimensions and fact table
-- =============================================

-- Drop tables if they exist (for development purposes)
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_orders;
DROP TABLE IF EXISTS dim_payments;
DROP TABLE IF EXISTS dim_returns;
DROP TABLE IF EXISTS dim_inventory;
DROP TABLE IF EXISTS dim_marketing;
DROP TABLE IF EXISTS dim_date;

-- Dimension: Date
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    season VARCHAR(20)
);

-- Dimension: Customers
CREATE TABLE dim_customers (
    customer_id INTEGER PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(50),
    customer_state VARCHAR(2),
    customer_lifetime_value DECIMAL(10,2),
    customer_segment VARCHAR(20),
    acquisition_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Dimension: Products
CREATE TABLE dim_products (
    product_id INTEGER PRIMARY KEY,
    product_category_name VARCHAR(50),
    product_category_name_english VARCHAR(50),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER,
    product_volume_liters DECIMAL(8,2),
    product_category VARCHAR(50),
    product_brand VARCHAR(50),
    product_price DECIMAL(10,2),
    product_status VARCHAR(20) DEFAULT 'active'
);

-- Dimension: Orders
CREATE TABLE dim_orders (
    order_id INTEGER PRIMARY KEY,
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    order_status_category VARCHAR(20)
);

-- Dimension: Payments
CREATE TABLE dim_payments (
    payment_id INTEGER PRIMARY KEY,
    payment_sequential INTEGER,
    payment_type VARCHAR(20),
    payment_installments INTEGER,
    payment_value DECIMAL(10,2)
);

-- Dimension: Returns
CREATE TABLE dim_returns (
    return_id INTEGER PRIMARY KEY,
    return_reason VARCHAR(100),
    return_origin VARCHAR(50),
    return_condition VARCHAR(20),
    return_shipping_cost DECIMAL(10,2),
    return_refund_amount DECIMAL(10,2)
);

-- Dimension: Inventory
CREATE TABLE dim_inventory (
    inventory_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    warehouse_id INTEGER,
    stock_quantity INTEGER,
    reorder_level INTEGER,
    last_restock_date DATE,
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

-- Dimension: Marketing
CREATE TABLE dim_marketing (
    marketing_id INTEGER PRIMARY KEY,
    campaign_name VARCHAR(100),
    channel VARCHAR(20),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    revenue_attributed DECIMAL(10,2)
);

-- Fact Table: Sales
CREATE TABLE fact_sales (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    payment_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    profit DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    return_id INTEGER,
    marketing_id INTEGER,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (order_id) REFERENCES dim_orders(order_id),
    FOREIGN KEY (payment_id) REFERENCES dim_payments(payment_id),
    FOREIGN KEY (return_id) REFERENCES dim_returns(return_id),
    FOREIGN KEY (marketing_id) REFERENCES dim_marketing(marketing_id)
);