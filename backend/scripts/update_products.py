import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Get environment variables
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_API_PASSWORD = os.getenv('SHOPIFY_API_PASSWORD')
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

# Connect to PostgreSQL
def connect_to_postgres():
    try:
        connection = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return connection
    except Exception as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None

# Fetch product data from Shopify API
def fetch_shopify_products():
    try:
        url = f"{SHOPIFY_STORE_URL}/admin/api/2023-01/products.json"
        response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_API_PASSWORD))

        if response.status_code == 200:
            return response.json()['products']
        else:
            print(f"Error fetching data from Shopify: {response.status_code}")
            return []
    except Exception as error:
        print(f"Error fetching Shopify products: {error}")
        return []

# Insert or update product data in PostgreSQL
def update_products_in_postgres(products):
    connection = connect_to_postgres()
    if connection is None:
        return

    cursor = connection.cursor()

    for product in products:
        product_name = product['title']
        description = product['body_html']
        sku = product['variants'][0]['sku'] if product['variants'] else None
        price = float(product['variants'][0]['price']) if product['variants'] else 0
        image_url = product['image']['src'] if product['image'] else None
        categories = ', '.join(product['tags']) if product['tags'] else ''

        cursor.execute("""
            INSERT INTO products (product_name, description, image_url, categories, sku, price, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO UPDATE
            SET product_name = EXCLUDED.product_name,
                description = EXCLUDED.description,
                image_url = EXCLUDED.image_url,
                categories = EXCLUDED.categories,
                price = EXCLUDED.price,
                last_updated = EXCLUDED.last_updated;
        """, (product_name, description, image_url, categories, sku, price, datetime.now()))

    connection.commit()
    cursor.close()
    connection.close()

# Main function to sync products
def main():
    print("Fetching products from Shopify...")
    products = fetch_shopify_products()
    
    if products:
        print(f"Fetched {len(products)} products.")
        print("Updating products in PostgreSQL...")
        update_products_in_postgres(products)
        print("Products updated successfully.")
    else:
        print("No products to update.")

if __name__ == '__main__':
    main()
