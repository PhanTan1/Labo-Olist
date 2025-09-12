CREATE VIEW vw_dim_product AS
SELECT
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM products;

CREATE VIEW vw_dim_customer AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM customers;

CREATE VIEW vw_dim_seller AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM sellers;

CREATE VIEW vw_dim_payment AS
SELECT DISTINCT
    payment_type
FROM order_payments;

CREATE VIEW vw_dim_order_status AS
SELECT DISTINCT
    order_status
FROM orders;

CREATE VIEW vw_dim_product_category_translation AS
SELECT
    product_category_name,
    product_category_name_english
FROM product_category_name_translation;

CREATE VIEW vw_dim_geolocation AS
SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
FROM geolocation;

CREATE VIEW vw_dim_date AS
SELECT DISTINCT
    CAST(order_purchase_timestamp AS DATE) AS full_date,
    EXTRACT(YEAR FROM order_purchase_timestamp) AS year,
    EXTRACT(MONTH FROM order_purchase_timestamp) AS month,
    EXTRACT(DAY FROM order_purchase_timestamp) AS day,
    EXTRACT(WEEK FROM order_purchase_timestamp) AS week_of_year
FROM orders;
