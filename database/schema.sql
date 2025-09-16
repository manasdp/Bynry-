-- Represents the client company using our SaaS platform
CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Warehouses belonging to a specific company
CREATE TABLE warehouses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    location_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Suppliers who provide products
CREATE TABLE suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50)
);

-- Categories or types for products, which can define rules like low stock thresholds
CREATE TABLE product_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    low_stock_threshold INT NOT NULL DEFAULT 10
);

-- Core product information
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    product_type_id INT,
    supplier_id INT,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (company_id, sku), -- SKU is unique *per company*
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (product_type_id) REFERENCES product_types(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Junction table to track stock levels of products in specific warehouses
CREATE TABLE inventory (
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE
);

-- Log table to track all inventory movements for auditing and analysis
CREATE TABLE inventory_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity_change INT NOT NULL, -- e.g., -5 for a sale, +50 for a restock
    new_quantity INT NOT NULL,
    reason VARCHAR(255), -- e.g., 'customer_sale', 'supplier_restock', 'manual_adjustment'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id, warehouse_id) REFERENCES inventory(product_id, warehouse_id)
);

-- Junction table to define product bundles
CREATE TABLE bundle_components (
    bundle_product_id INT NOT NULL,  -- The product that is the bundle
    component_product_id INT NOT NULL, -- The product inside the bundle
    quantity_in_bundle INT NOT NULL CHECK (quantity_in_bundle > 0),
    PRIMARY KEY (bundle_product_id, component_product_id),
    FOREIGN KEY (bundle_product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (component_product_id) REFERENCES products(id) ON DELETE CASCADE
);
