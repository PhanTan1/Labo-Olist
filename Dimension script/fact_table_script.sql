DROP TABLE IF EXISTS fact_order;
CREATE TABLE fact_order (
    order_id UUID,
    order_item_id SMALLINT,
    customer_id UUID,
    product_id UUID,
    seller_id UUID,
    order_status VARCHAR(11),
    order_purchase_timestamp TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    delivery_delay_days SMALLINT,
    is_delivered_late BOOLEAN,
    price DECIMAL(8,2),
    freight_value DECIMAL(8,2),
    product_category_name VARCHAR(60),
    product_name_length VARCHAR(11),
    product_description_length SMALLINT,
    product_photos_qty SMALLINT,
    payment_type VARCHAR(11),
    payment_installments INT,
    payment_value DECIMAL(8,2)
);