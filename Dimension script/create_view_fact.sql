CREATE VIEW vw_fact_order AS
SELECT
    oi.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    EXTRACT(DAY FROM o.order_delivered_customer_date - o.order_estimated_delivery_date) AS delivery_delay_days,
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN TRUE
        ELSE FALSE
    END AS is_delivered_late,
    oi.price,
    oi.freight_value,
    p.product_category_name,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    pay.payment_type,
    pay.payment_installments,
    pay.payment_value
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_payments pay ON o.order_id = pay.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN sellers s ON oi.seller_id = s.seller_id;
