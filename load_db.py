import sqlite3
import pandas as pd
import os

print("SQLite Database Loader")
print("=" * 50)

csv_path = 'dataset/enriched_sales_dataset.csv'
db_path = 'sales.db'

# Ensure the CSV exists
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found. Running data enrichment first...")
    import enrich_sales_data
    # Recheck
    if not os.path.exists(csv_path):
        print("Failed to generate enriched dataset. Exiting.")
        exit(1)

# Read the CSV
print(f"Reading cleaned sales data from {csv_path}...")
df = pd.read_csv(csv_path)

# Connect to SQLite DB
print(f"Connecting to SQLite database at {db_path}...")
conn = sqlite3.connect(db_path)

# Write to SQLite
print("Loading sales data into 'sales' table...")
# SQLite column names cannot have spaces for ease of SQL queries, but pandas can handle spaces.
# To make it recruiter-friendly, we'll replace spaces in column names with underscores.
df.columns = [col.replace(' ', '_') for col in df.columns]

df.to_sql('sales', conn, if_exists='replace', index=False)
print("Data loaded successfully!")

# Verify table info
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sales")
row_count = cursor.fetchone()[0]
print(f"Verified row count in database table 'sales': {row_count}")

# Print columns
cursor.execute("PRAGMA table_info(sales)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Table columns: {', '.join(columns)}")

conn.close()
print("=" * 50)
print("Database setup complete!")

# Also load enriched dataset if it exists
enriched_path = 'dataset/enriched_sales_dataset.csv'
if os.path.exists(enriched_path):
    print("\nLoading enriched sales dataset into 'sales_enriched' table...")
    df_enriched = pd.read_csv(enriched_path)
    df_enriched.columns = [col.replace(' ', '_') for col in df_enriched.columns]
    conn2 = sqlite3.connect(db_path)
    df_enriched.to_sql('sales_enriched', conn2, if_exists='replace', index=False)
    conn2.close()
    print(f"Enriched table loaded: {len(df_enriched)} rows, {len(df_enriched.columns)} columns.")
    print(f"New columns: {[c for c in df_enriched.columns if c not in ['Order_ID','Order_Date','Customer_Name','Region','Product_Category','Product_Name','Sales_Amount','Quantity','Profit','Discount','Payment_Mode','Month','Year']]}")
else:
    print("\nNo enriched dataset found. Run enrich_sales_data.py first to generate it.")
