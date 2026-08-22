-- ============================================================
-- 05_validation.sql
--
-- Structural data-quality checks. Every query should return
-- ZERO rows (violations) unless stated otherwise. Run this
-- after data generation via scripts/reset_db.sh or manually:
--
--   mysql -h 127.0.0.1 -P 3306 -u gym_user -p sql_gym < database/05_validation.sql
--
-- Row-count queries at the end are informational, not pass/fail.
-- ============================================================

USE sql_gym;

-- ------------------------------------------------------------
-- 1. Primary key uniqueness (guaranteed by AUTO_INCREMENT PKs,
--    but inventory has a composite natural key worth checking)
-- ------------------------------------------------------------
SELECT 'inventory_duplicate_grain' AS check_name, store_id, product_id, inventory_date, COUNT(*) AS n
FROM inventory
GROUP BY store_id, product_id, inventory_date
HAVING COUNT(*) > 1;

-- ------------------------------------------------------------
-- 2. Orphaned foreign keys (should be impossible given FK
--    constraints, but confirms the generator never disabled
--    checks incorrectly)
-- ------------------------------------------------------------
SELECT 'orphan_orders_customer' AS check_name, o.order_id
FROM orders o
LEFT JOIN customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;

SELECT 'orphan_order_items_order' AS check_name, oi.order_item_id
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL;

SELECT 'orphan_payments_order' AS check_name, p.payment_id
FROM payments p
LEFT JOIN orders o ON o.order_id = p.order_id
WHERE o.order_id IS NULL;

SELECT 'orphan_returns_order' AS check_name, r.return_id
FROM returns r
LEFT JOIN orders o ON o.order_id = r.order_id
WHERE o.order_id IS NULL;

-- ------------------------------------------------------------
-- 3. Business-logic consistency
-- ------------------------------------------------------------

-- Orders with no order_items at all (excluding legitimately
-- cancelled-before-fulfillment orders is a judgment call left
-- to the learner; here we just surface the count)
SELECT 'orders_without_items' AS check_name, COUNT(*) AS n
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
WHERE oi.order_id IS NULL;

-- Returns whose returned quantity exceeds the quantity purchased
-- on that order/product combination
SELECT 'returns_exceeding_purchased_qty' AS check_name, r.return_id, r.order_id, r.product_id
FROM returns r
JOIN (
    SELECT order_id, product_id, SUM(quantity) AS purchased_qty
    FROM order_items
    GROUP BY order_id, product_id
) oi ON oi.order_id = r.order_id AND oi.product_id = r.product_id
WHERE r.quantity > oi.purchased_qty;

-- Payments whose amount deviates from the order's item total by
-- more than a small rounding tolerance (informational: partial /
-- failed payments are expected to differ, so this is not a hard
-- failure, just a review query)
SELECT 'payment_amount_mismatch' AS check_name, p.payment_id, p.order_id, p.amount, ot.order_total
FROM payments p
JOIN (
    SELECT order_id, SUM(quantity * unit_price - discount_amount) AS order_total
    FROM order_items
    GROUP BY order_id
) ot ON ot.order_id = p.order_id
WHERE p.payment_status = 'success'
  AND ABS(p.amount - ot.order_total) > 0.01;

-- Inventory ledger arithmetic: opening + received - sold should
-- equal closing
SELECT 'inventory_arithmetic_mismatch' AS check_name, store_id, product_id, inventory_date
FROM inventory
WHERE opening_stock + received_quantity - sold_quantity <> closing_stock;

-- Negative stock
SELECT 'inventory_negative_closing' AS check_name, store_id, product_id, inventory_date, closing_stock
FROM inventory
WHERE closing_stock < 0;

-- ------------------------------------------------------------
-- 4. Row counts (informational — compare against the minimum
--    target volumes in CLAUDE.md section 6)
-- ------------------------------------------------------------
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'categories', COUNT(*) FROM categories
UNION ALL SELECT 'brands', COUNT(*) FROM brands
UNION ALL SELECT 'stores', COUNT(*) FROM stores
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'returns', COUNT(*) FROM returns
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL SELECT 'customer_campaigns', COUNT(*) FROM customer_campaigns
UNION ALL SELECT 'support_tickets', COUNT(*) FROM support_tickets;

-- ------------------------------------------------------------
-- 5. NULL pattern spot-check (informational)
-- ------------------------------------------------------------
SELECT
    COUNT(*) AS total_customers,
    SUM(gender IS NULL) AS null_gender,
    SUM(date_of_birth IS NULL) AS null_dob,
    SUM(city IS NULL) AS null_city,
    SUM(region IS NULL) AS null_region,
    SUM(customer_segment IS NULL) AS null_segment,
    SUM(acquisition_channel IS NULL) AS null_channel
FROM customers;

-- Duplicate business keys: two customers with the exact same
-- name + date_of_birth (allowed to exist in small numbers as a
-- realistic edge case, but worth surfacing)
SELECT 'possible_duplicate_customers' AS check_name, customer_name, date_of_birth, COUNT(*) AS n
FROM customers
WHERE date_of_birth IS NOT NULL
GROUP BY customer_name, date_of_birth
HAVING COUNT(*) > 1;
