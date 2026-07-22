# E-Commerce Business Intelligence Platform Data Dictionary

This document provides detailed descriptions of all tables, columns, and data types in the e-commerce data warehouse.

## Overview
The data warehouse follows a star schema design with one central fact table (`fact_sales`) surrounded by dimension tables. This design optimizes query performance for analytical workloads and simplifies relationships between business entities.

## Tables

### Fact Table: fact_sales
Stores individual sales transactions with measures and foreign keys to dimension tables.

| Column Name | Data Type | Description | Foreign Key To |
|-------------|-----------|-------------|----------------|
| sales_id | INTEGER (PK) | Unique identifier for each sales record |  |
| date_id | INTEGER | Date of the transaction | dim_date(date_id) |
| customer_id | INTEGER | Customer who made the purchase | dim_customers(customer_id) |
| product_id | INTEGER | Product purchased | dim_products(product_id) |
| order_id | INTEGER | Associated order | dim_orders(order_id) |
| payment_id | INTEGER | Payment method used | dim_payments(payment_id) |
| quantity | INTEGER | Number of units purchased |  |
| unit_price | DECIMAL(10,2) | Price per unit |  |
| total_price | DECIMAL(10,2) | Total amount for line item (quantity * unit_price) |  |
| profit | DECIMAL(10,2) | Profit from the transaction (estimated) |  |
| freight_value | DECIMAL(10,2) | Shipping cost for the item |  |
| return_id | INTEGER | Reference if item was returned | dim_returns(return_id) |
| marketing_id | INTEGER | Marketing campaign attributed to sale | dim_marketing(marketing_id) |

### Dimension Table: dim_date
Contains date-related attributes for time-based analysis.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| date_id | INTEGER (PK) | Unique identifier for each date |
| date | DATE | Actual date (YYYY-MM-DD) |
| day | INTEGER | Day of month (1-31) |
| month | INTEGER | Month of year (1-12) |
| quarter | INTEGER | Quarter of year (1-4) |
| year | INTEGER | Year (e.g., 2023) |
| day_of_week | INTEGER | Day of week (0=Sunday, 6=Saturday) |
| day_name | VARCHAR(10) | Name of day (Sunday, Monday, etc.) |
| month_name | VARCHAR(10) | Name of month (January, February, etc.) |
| is_weekend | BOOLEAN | True if date is Saturday or Sunday |
| is_holiday | BOOLEAN | True if date is a public holiday |
| holiday (Monday, Tuesday, etc.) season | VARCHAR(20) | Season of year (Winter, Spring, Summer, Fall) |

### Dimension Table: dim_customers
Contains customer profile information.

| Column Name | Data Type | Description | |-----------|-------------
| customer_id | INTEGER (Unique identifier for each customer | 
|cust_uid |er50)) |Alternathelps if differenty | 
|customer_idzip_code_prefix  | INTEGER |  |First three of customer’s 
|customer_ |VARCHAR(50) |City | the
|customer_state | VARCHAR_STATE | Ab2|- |
|customer_lifetime_value|DECIMAL| (12,2)|  |T|o|t |a|l|a|m|o|u|n|t|  of|m|o|n|e|y|  the|c|u|s|t|o|m|e|r|  h|a|s|  s|p|e|n|t|  o|v|e|r|  their|l|i|f|e|t|i|m|e|  (updated|  periodically) | 
|customer_segment | 
VARCHAR(20) | |  Customer segment based on RFM analysis (Champions, Loyal, At Risk, Lost, New, Big Spenders, Need Attention) | 
|acquisition_date |  |
DATE |  | f Date datee whenof the customer’s madeir firstrst purchase | 
|is_active |  |B |OO |B |O |O |L |E |A |N |D | Is=T|h|e|  c|u|s|t|o|m|e|r|  c|u|rr|e|n|t|l|y|  a|c|t|i|v|e|  (m|a|d|e|  a| pu|r|c|h|a|s|e|  i|n|  t|h|e|  l|a|s|t|  1|2|  m|o|n|t|h|s?|)  |  |### Dimension Table: dim_products
Contains product details and classification information.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| product_id | INTEGER (PK) | Unique identifier for each product |
| product_category_name | VARCHAR(50) | Product category in original language (Portuguese for Brazilian dataset) |
| product_category_name_english | VARCHAR(50) | Product category translated to English |
| product_name_lenght | INTEGER | Length of the product name in characters |
| product_description_lenght | INTEGER | Length of the product description in characters |
| product_photos_qty | INTEGER | Number of photos available for the product |
| product_weight_g | INTEGER | Weight of the product in grams |
| product_length_cm | INTEGER | Length of the product in centimeters |
| product_height_cm | INTEGER | Height of the product in centimeters |
| product_width_cm | INTEGER | Width of the product in centimeters |
| product_volume_liters | DECIMAL(8,2) | Volume of the product in liters |
| product_category | VARCHAR(50) | High-level product category grouping |
| product_brand | VARCHAR(50) | Brand name of the product |
| product_price | DECIMAL(10,2) | Standard price of the product |
| product_status | VARCHAR(20) | Status of the product (active, discontinued, out of stock) |

### Dimension Table: dim_orders
Contains order status and fulfillment information.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| order_id | INTEGER (PK) | Unique identifier for each order |
| order_status | VARCHAR(20) | Current status of the order (pending, processing, shipped, delivered, cancelled) |
| order_purchase_timestamp | TIMESTAMP | Date and time when the order was placed |
| order_approved_at | TIMESTAMP | Date and time when the order was payment-approved |
| order_delivered_carrier_date | TIMESTAMP | Date and time when the order was handed to the delivery carrier |
| order_delivered_customer_date | TIMESTAMP | Date and time when the order was delivered to the customer |
| order_idelivery | TIMESTAMP |
|order_estimated_delivery_date | TIMESTAMP | Expected delivery date promised at time of purchase |
|order_status_category | VARCHAR(20) | Simplified status category for reporting |

### Dimension Table: dim_payments
Contains payment method and transaction details.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| payment_id | INTEGER (PK) | Unique identifier for each payment record |
| payment_sequential | INTEGER | Sequence number for multiple payments on same order |
| payment_type | VARCHAR(20) | Type of payment (credit_card, boleto, voucher, debit_card) |
| payment_installments | INTEGER | Number of installments for the payment |
| payment_value | DECIMAL(10,2) | Value of the payment transaction |

### Dimension Table: dim_returns
Contains information about product returns and refunds.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| return_id | INTEGER (PK) | Unique identifier for each return |
| return_reason | VARCHAR(100) | Reason provided by customer for return |
| return_origin | VARCHAR(50) | Origin of the return (domestic, international) |
| return_condition | VARCHAR(20) | Condition of returned item (new, used, defective) |
| return_shipping_cost | DECIMAL(10,2) | Cost of shipping for the return |
| return_refund_amount | DECIMAL(10,2) | Amount refunded to the customer |

### Dimension Table: dim_marketing
Contains marketing campaign and channel performance data.

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| marketing_id | INTEGER (PK) | Unique identifier for each marketing record |
| campaign_name | VARCHAR(100) | Name of the marketing campaign |
| channel | VARCHAR(20) | Marketing channel (email, social, search, display, affiliate) |
| start_date | DATE | Campaign start date |
| end_date | DATE | Campaign end date |
| budget | DECIMAL(10,2) | Total budget allocated to the campaign |
| impressions | INTEGER | Number of times the ad was displayed |
| clicks | INTEGER | Number of times the ad was clicked |
| conversions | INTEGER | Number of desired actions (purchases, sign-ups) completed |
| revenue_attributed | DECIMAL(10,2) | Revenue directly attributed to this marketing effort |

## Relationships

### Fact to Dimension Relationships
- `fact_sales.date_id` → `dim_date.date_id`
- `fact_sales.customer_id` → `dim_customers.customer_id`
- `fact_sales.product_id` → `dim_products.product_id`
- `fact_sales.order_id` → `dim_orders.order_id`
- `fact_sales.payment_id` → `dim_payments.payment_id`
- `fact_sales.return_id` → `dim_returns.return_id`
- `fact_sales.marketing_id` → `dim_marketing.marketing_id`

### Important Notes
1. **Nullable Foreign Keys**: Some foreign keys in the fact table can be NULL to handle missing or unknown dimension values (e.g., marketing_id may be NULL for organic traffic).
2. **Data Types**: 
   - INTEGER: Whole numbers for IDs and counts
   - DECIMAL(p,s): Fixed-point numbers for monetary values (p=total digits, s=decimal places)
   - VARCHAR(n): Variable-length text with maximum length n
   - DATE: Calendar date only
   - TIMESTAMP: Date and time together
   - BOOLEAN: True/false values
3. **Indexes**: Primary keys are automatically indexed. Foreign keys and frequently filtered columns should have additional indexes for query performance.
4. **Historical Tracking**: This warehouse design does not currently implement slowly changing dimensions (SCD). For production systems requiring historical tracking, SCD Type 2 would be implemented.

## Sample Queries

### Daily Sales Summary
```sql
SELECT 
    d.date,
    SUM(s.total_price) AS daily_revenue,
    SUM(s.profit) AS daily_profit,
    COUNT(DISTINCT s.order_id) AS daily_orders,
    COUNT(DISTINCT s.customer_id) AS daily_customers
FROM fact_sales s
JOIN dim_date d ON s.date_id = d.date_id
GROUP BY d.date
ORDER BY d.date;
```

### Product Performance
```sql
SELECT 
    p.product_category_name_english,
    SUM(s.total_price) AS total_revenue,
    SUM(s.profit) AS total_profit,
    SUM(s.quantity) AS total_quantity_sold
FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY total_revenue DESC;
```

### Customer Segmentation Distribution
```sql
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    COUNT(DISTINCT s.order_id) AS order_count,
    SUM(s.total_price) AS total_revenue
FROM fact_sales s
JOIN dim_customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY customer_count DESC;
```