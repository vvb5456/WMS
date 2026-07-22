-- WMS Database Initialization
-- Charset: utf8mb4

CREATE DATABASE IF NOT EXISTS wmsdatabase
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE wmsdatabase;

-- users
CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(32) NOT NULL DEFAULT 'viewer',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- product (编码)
CREATE TABLE IF NOT EXISTS product (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  sku_code VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(200) NOT NULL,
  spec VARCHAR(200) DEFAULT '',
  unit VARCHAR(16) NOT NULL DEFAULT '件',
  barcode VARCHAR(64) NULL,
  safe_stock DECIMAL(18,3) NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_product_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- warehouse
CREATE TABLE IF NOT EXISTS warehouse (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(32) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(255) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- location
CREATE TABLE IF NOT EXISTS location (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  code VARCHAR(32) NOT NULL,
  name VARCHAR(100) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_location_wh_code (warehouse_id, code),
  CONSTRAINT fk_location_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- inventory
CREATE TABLE IF NOT EXISTS inventory (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  product_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  quantity DECIMAL(18,3) NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_inv_product_wh_loc (product_id, warehouse_id, location_id),
  INDEX idx_inv_wh (warehouse_id),
  CONSTRAINT fk_inv_product FOREIGN KEY (product_id) REFERENCES product(id),
  CONSTRAINT fk_inv_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
  CONSTRAINT fk_inv_location FOREIGN KEY (location_id) REFERENCES location(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- inventory_transaction
CREATE TABLE IF NOT EXISTS inventory_transaction (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  product_id BIGINT UNSIGNED NOT NULL,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  delta_qty DECIMAL(18,3) NOT NULL,
  balance_after DECIMAL(18,3) NOT NULL,
  ref_type VARCHAR(32) NOT NULL,
  ref_id BIGINT UNSIGNED NOT NULL,
  operator_id BIGINT UNSIGNED NOT NULL,
  remark VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_tx_product_time (product_id, created_at),
  INDEX idx_tx_ref (ref_type, ref_id),
  CONSTRAINT fk_tx_product FOREIGN KEY (product_id) REFERENCES product(id),
  CONSTRAINT fk_tx_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
  CONSTRAINT fk_tx_location FOREIGN KEY (location_id) REFERENCES location(id),
  CONSTRAINT fk_tx_operator FOREIGN KEY (operator_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- inbound_order
CREATE TABLE IF NOT EXISTS inbound_order (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no VARCHAR(32) NOT NULL UNIQUE,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  supplier_name VARCHAR(200) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  remark VARCHAR(500) NULL,
  created_by BIGINT UNSIGNED NOT NULL,
  approved_by BIGINT UNSIGNED NULL,
  approved_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_inbound_status (status),
  CONSTRAINT fk_inbound_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
  CONSTRAINT fk_inbound_created_by FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- inbound_order_line
CREATE TABLE IF NOT EXISTS inbound_order_line (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  inbound_order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  planned_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  actual_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  CONSTRAINT fk_inbound_line_order FOREIGN KEY (inbound_order_id) REFERENCES inbound_order(id) ON DELETE CASCADE,
  CONSTRAINT fk_inbound_line_product FOREIGN KEY (product_id) REFERENCES product(id),
  CONSTRAINT fk_inbound_line_location FOREIGN KEY (location_id) REFERENCES location(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- outbound_order
CREATE TABLE IF NOT EXISTS outbound_order (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no VARCHAR(32) NOT NULL UNIQUE,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  customer_name VARCHAR(200) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  remark VARCHAR(500) NULL,
  created_by BIGINT UNSIGNED NOT NULL,
  approved_by BIGINT UNSIGNED NULL,
  approved_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_outbound_status (status),
  CONSTRAINT fk_outbound_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
  CONSTRAINT fk_outbound_created_by FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- outbound_order_line
CREATE TABLE IF NOT EXISTS outbound_order_line (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  outbound_order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  planned_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  actual_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  CONSTRAINT fk_outbound_line_order FOREIGN KEY (outbound_order_id) REFERENCES outbound_order(id) ON DELETE CASCADE,
  CONSTRAINT fk_outbound_line_product FOREIGN KEY (product_id) REFERENCES product(id),
  CONSTRAINT fk_outbound_line_location FOREIGN KEY (location_id) REFERENCES location(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- stocktake_order
CREATE TABLE IF NOT EXISTS stocktake_order (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no VARCHAR(32) NOT NULL UNIQUE,
  warehouse_id BIGINT UNSIGNED NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  remark VARCHAR(500) NULL,
  created_by BIGINT UNSIGNED NOT NULL,
  approved_by BIGINT UNSIGNED NULL,
  approved_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_stocktake_status (status),
  CONSTRAINT fk_stocktake_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
  CONSTRAINT fk_stocktake_created_by FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- stocktake_order_line
CREATE TABLE IF NOT EXISTS stocktake_order_line (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  stocktake_order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  location_id BIGINT UNSIGNED NOT NULL,
  book_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  counted_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  diff_qty DECIMAL(18,3) NOT NULL DEFAULT 0,
  CONSTRAINT fk_stocktake_line_order FOREIGN KEY (stocktake_order_id) REFERENCES stocktake_order(id) ON DELETE CASCADE,
  CONSTRAINT fk_stocktake_line_product FOREIGN KEY (product_id) REFERENCES product(id),
  CONSTRAINT fk_stocktake_line_location FOREIGN KEY (location_id) REFERENCES location(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- order_no sequence (daily)
CREATE TABLE IF NOT EXISTS order_no_seq (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  prefix VARCHAR(8) NOT NULL,
  seq_date DATE NOT NULL,
  last_seq INT NOT NULL DEFAULT 0,
  UNIQUE KEY uk_order_no_seq (prefix, seq_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 种子数据由 WmsServer/init_db.py 写入（密码哈希由应用生成）
