import os
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Shopify API details
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL')
SHOPIFY_API_VERSION = "2024-10"

# Azure Blob Storage details
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = "product-data"
BLOB_FILE_NAME = "products.parquet"

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_FILE_NAME)

# Fetch all products from Shopify with pagination
def fetch_shopify_products():
    products = []
    url = f"{SHOPIFY_STORE_URL}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=50"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    while url:
        try:
            print(f"Fetching products from Shopify at: {url}")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                products.extend(data.get('products', []))
                print(f"Fetched {len(data.get('products', []))} products.")

                # Pagination: Check for 'next' link
                if 'Link' in response.headers:
                    links = response.headers['Link'].split(',')
                    next_link = [link for link in links if 'rel="next"' in link]
                    if next_link:
                        url = next_link[0].split(';')[0].strip('<> ').strip()
                    else:
                        url = None
                else:
                    url = None
            else:
                print(f"Error fetching data from Shopify: {response.status_code} - {response.text}")
                break
        except Exception as error:
            print(f"Error fetching Shopify products: {error}")
            break

    print(f"Total products fetched: {len(products)}")
    return products

# Save products to Azure Blob Storage as Parquet
def save_products_to_blob(products):
    if not products:
        print("No products to save.")
        return

    # Convert product data to a pandas DataFrame
    records = []
    for product in products:
        sku = product['variants'][0]['sku'] if product.get('variants') else None
        if sku:  # Only include products with an SKU
            records.append({
                "product_name": product.get('title', 'No Name'),
                "description": product.get('body_html', ''),
                "sku": sku,
                "price": float(product['variants'][0]['price']) if product.get('variants') else 0.0,
                "image_url": product['image']['src'] if product.get('image') else None,
                "categories": ', '.join(product.get('tags', [])),
                "last_updated": datetime.now()
            })

    df = pd.DataFrame(records)
    print(f"Saving {len(df)} products to Azure Blob Storage as Parquet...")

    # Convert DataFrame to Parquet format
    table = pa.Table.from_pandas(df)
    parquet_buffer = pa.BufferOutputStream()
    pq.write_table(table, parquet_buffer)

    # Upload to Blob Storage
    blob_client.upload_blob(parquet_buffer.getvalue(), overwrite=True)
    print(f"Products saved to Azure Blob Storage in {BLOB_FILE_NAME}.")

# Main function to sync products
def main():
    print("Fetching products from Shopify...")
    products = fetch_shopify_products()
    if products:
        save_products_to_blob(products)
        print("Products synced successfully.")
    else:
        print("No products to sync.")

if __name__ == '__main__':
    main()
