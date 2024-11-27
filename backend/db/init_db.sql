-- Create the products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50),
    product_name VARCHAR(255),
    price DECIMAL(10, 2),
    description TEXT,
    image_url TEXT,
    categories VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);