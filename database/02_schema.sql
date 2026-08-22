-- ============================================================
-- 02_schema.sql
-- Core schema for the SQL Analytical Thinking Gym.
--
-- Business domain: synthetic retail / e-commerce company selling
-- through physical stores and online, with customers, campaigns,
-- returns, inventory and support tickets.
--
-- Design notes:
--   - Some attributes are intentionally NULLable (e.g. customer
--     demographics) to create realistic analytical edge cases.
--   - Surrogate PKs are used on fact tables even where the spec
--     only lists natural keys, so that grain is unambiguous.
-- ============================================================

USE sql_gym;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS customer_campaigns;
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS customers;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- Dimension: customers
-- ------------------------------------------------------------
CREATE TABLE customers (
    customer_id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_name        VARCHAR(150)    NOT NULL,
    gender               ENUM('M', 'F', 'Other') NULL,
    date_of_birth        DATE            NULL,
    registration_date    DATE            NOT NULL,
    city                 VARCHAR(100)    NULL,
    region               VARCHAR(100)    NULL,
    customer_segment     VARCHAR(50)     NULL,
    acquisition_channel  VARCHAR(50)     NULL,
    INDEX idx_customers_region (region),
    INDEX idx_customers_segment (customer_segment),
    INDEX idx_customers_registration_date (registration_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Dimension: categories / brands / products
-- ------------------------------------------------------------
CREATE TABLE categories (
    category_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE brands (
    brand_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    brand_name  VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE products (
    product_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_name    VARCHAR(200)    NOT NULL,
    category_id     INT UNSIGNED    NOT NULL,
    brand_id        INT UNSIGNED    NOT NULL,
    cost            DECIMAL(10,2)   NOT NULL,
    selling_price   DECIMAL(10,2)   NOT NULL,
    launch_date     DATE            NOT NULL,
    status          ENUM('active', 'discontinued') NOT NULL DEFAULT 'active',
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(category_id),
    CONSTRAINT fk_products_brand    FOREIGN KEY (brand_id)    REFERENCES brands(brand_id),
    INDEX idx_products_category (category_id),
    INDEX idx_products_brand (brand_id),
    INDEX idx_products_status (status)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Dimension: stores / employees
-- ------------------------------------------------------------
CREATE TABLE stores (
    store_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    store_name  VARCHAR(150) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    region      VARCHAR(100) NOT NULL,
    store_type  ENUM('flagship', 'standard', 'outlet', 'online') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE employees (
    employee_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    store_id        INT UNSIGNED NOT NULL,
    employee_role   VARCHAR(50)  NOT NULL,
    hire_date       DATE         NOT NULL,
    CONSTRAINT fk_employees_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
    INDEX idx_employees_store (store_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Fact: orders / order_items / payments / returns
-- ------------------------------------------------------------
CREATE TABLE orders (
    order_id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT UNSIGNED NOT NULL,
    store_id        INT UNSIGNED NOT NULL,
    order_date      DATETIME     NOT NULL,
    order_status    ENUM('completed', 'cancelled', 'pending', 'refunded') NOT NULL,
    sales_channel   ENUM('online', 'in_store') NOT NULL,
    payment_method  VARCHAR(50)  NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_orders_store    FOREIGN KEY (store_id)    REFERENCES stores(store_id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_store (store_id),
    INDEX idx_orders_date (order_date),
    INDEX idx_orders_status (order_status)
) ENGINE=InnoDB;

CREATE TABLE order_items (
    order_item_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id        INT UNSIGNED    NOT NULL,
    product_id      INT UNSIGNED    NOT NULL,
    quantity        INT UNSIGNED    NOT NULL,
    unit_price      DECIMAL(10,2)   NOT NULL,
    discount_amount DECIMAL(10,2)   NOT NULL DEFAULT 0,
    CONSTRAINT fk_order_items_order   FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id)
) ENGINE=InnoDB;

CREATE TABLE payments (
    payment_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id        INT UNSIGNED    NOT NULL,
    payment_date    DATETIME        NOT NULL,
    amount          DECIMAL(10,2)   NOT NULL,
    payment_status  ENUM('success', 'failed', 'refunded', 'pending') NOT NULL,
    payment_method  VARCHAR(50)     NOT NULL,
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    INDEX idx_payments_order (order_id),
    INDEX idx_payments_status (payment_status),
    INDEX idx_payments_date (payment_date)
) ENGINE=InnoDB;

CREATE TABLE returns (
    return_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id        INT UNSIGNED NOT NULL,
    product_id      INT UNSIGNED NOT NULL,
    return_date     DATE         NOT NULL,
    quantity        INT UNSIGNED NOT NULL,
    return_reason   VARCHAR(100) NULL,
    CONSTRAINT fk_returns_order   FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_returns_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_returns_order (order_id),
    INDEX idx_returns_product (product_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Fact: inventory (store-product-day grain)
-- ------------------------------------------------------------
CREATE TABLE inventory (
    store_id            INT UNSIGNED NOT NULL,
    product_id          INT UNSIGNED NOT NULL,
    inventory_date      DATE         NOT NULL,
    opening_stock       INT          NOT NULL,
    received_quantity   INT          NOT NULL,
    sold_quantity       INT          NOT NULL,
    closing_stock       INT          NOT NULL,
    PRIMARY KEY (store_id, product_id, inventory_date),
    CONSTRAINT fk_inventory_store   FOREIGN KEY (store_id)   REFERENCES stores(store_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_inventory_date (inventory_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Fact: campaigns / customer_campaigns
-- ------------------------------------------------------------
CREATE TABLE campaigns (
    campaign_id     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    campaign_name   VARCHAR(150)    NOT NULL,
    channel         VARCHAR(50)     NOT NULL,
    start_date      DATE            NOT NULL,
    end_date        DATE            NOT NULL,
    budget          DECIMAL(12,2)   NOT NULL
) ENGINE=InnoDB;

CREATE TABLE customer_campaigns (
    interaction_id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id         INT UNSIGNED NOT NULL,
    campaign_id         INT UNSIGNED NOT NULL,
    interaction_date    DATE         NOT NULL,
    interaction_type    ENUM('impression', 'click', 'conversion') NOT NULL,
    CONSTRAINT fk_cc_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_cc_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    INDEX idx_cc_customer (customer_id),
    INDEX idx_cc_campaign (campaign_id),
    INDEX idx_cc_date (interaction_date)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Fact: support_tickets
-- ------------------------------------------------------------
CREATE TABLE support_tickets (
    ticket_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT UNSIGNED NOT NULL,
    created_at      DATETIME     NOT NULL,
    resolved_at     DATETIME     NULL,
    issue_type      VARCHAR(100) NOT NULL,
    priority        ENUM('low', 'medium', 'high', 'urgent') NOT NULL,
    status          ENUM('open', 'resolved', 'closed', 'pending') NOT NULL,
    CONSTRAINT fk_tickets_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_tickets_customer (customer_id),
    INDEX idx_tickets_status (status)
) ENGINE=InnoDB;
