-- ============================================================
-- 03_indexes.sql
-- Additional composite indexes supporting common analytical
-- access patterns (beyond the single-column indexes already
-- declared inline in 02_schema.sql).
-- ============================================================

USE sql_gym;

-- Customer purchase history / recency queries
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- Store performance over time
CREATE INDEX idx_orders_store_date ON orders (store_id, order_date);

-- Product sales lookups joined from order_items
CREATE INDEX idx_order_items_product_order ON order_items (product_id, order_id);

-- Payment reconciliation by order + status
CREATE INDEX idx_payments_order_status ON payments (order_id, payment_status);

-- Return-rate analysis by product over time
CREATE INDEX idx_returns_product_date ON returns (product_id, return_date);

-- Support ticket recency per customer
CREATE INDEX idx_tickets_customer_created ON support_tickets (customer_id, created_at);

-- Campaign funnel analysis
CREATE INDEX idx_cc_campaign_type ON customer_campaigns (campaign_id, interaction_type);
