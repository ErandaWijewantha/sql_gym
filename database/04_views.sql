-- ============================================================
-- 04_views.sql
--
-- Intentionally minimal.
--
-- This gym trains learners to derive business metrics (net
-- sales, active orders, valid returns, etc.) themselves from
-- raw fact/dimension tables. Pre-built "answer" views (e.g. a
-- view that already excludes cancelled orders, or one that
-- already nets out discounts) would defeat that purpose and
-- quietly resolve the ambiguity several Level 5 questions
-- deliberately leave open.
--
-- Only purely structural, non-judgmental convenience views
-- live here: denormalized read-only lookups that involve no
-- business-definition decisions.
-- ============================================================

USE sql_gym;

DROP VIEW IF EXISTS v_product_catalog;
DROP VIEW IF EXISTS v_store_directory;

CREATE VIEW v_product_catalog AS
SELECT
    p.product_id,
    p.product_name,
    c.category_name,
    b.brand_name,
    p.cost,
    p.selling_price,
    p.launch_date,
    p.status
FROM products p
JOIN categories c ON c.category_id = p.category_id
JOIN brands b      ON b.brand_id    = p.brand_id;

CREATE VIEW v_store_directory AS
SELECT
    store_id,
    store_name,
    city,
    region,
    store_type
FROM stores;
