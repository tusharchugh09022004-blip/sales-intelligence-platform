import pandas as pd
import numpy as np

# Step 1: Load the dataset
print("Loading dataset...")
df = pd.read_csv('dataset/sales_dataset_5500.csv')
print(f"Original shape: {df.shape}")
print("\nOriginal info:")
print(df.info())
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Step 2: Remove true duplicates (same Order ID + same Product = accidental dupes)
print("\nRemoving duplicates...")
initial_rows = len(df)
df = df.drop_duplicates(subset=['Order ID', 'Product Name'], keep='first')
print(f"Removed {initial_rows - len(df)} duplicates. New shape: {df.shape}")

# Step 3: Handle missing values
# Critical columns: drop rows missing Order ID, Order Date, Region, Sales Amount, Quantity
critical_cols = ['Order ID', 'Order Date', 'Region', 'Sales Amount', 'Quantity']
df = df.dropna(subset=critical_cols)
print(f"After dropping critical missing: shape {df.shape}")

# Fill categorical missing with 'Unknown'
df['Customer Name'] = df['Customer Name'].fillna('Unknown')
df['Product Name'] = df['Product Name'].fillna('Unknown')

# Fill numeric missing 'Profit' with median (avoids bias from mean with negatives)
profit_median = df['Profit'].median()
df['Profit'] = df['Profit'].fillna(profit_median)
print(f"Filled 'Profit' NaNs with median: {profit_median}")

print("\nMissing values after handling:")
print(df.isnull().sum())

# Step 4: Convert 'Order Date' to datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])
print("\n'Order Date' converted to datetime.")

# Step 5: Create new columns Month and Year
df['Month'] = df['Order Date'].dt.month
df['Year'] = df['Order Date'].dt.year
print("Added 'Month' and 'Year' columns.")
print("\nSample after new columns:")
print(df[['Order Date', 'Month', 'Year']].head())

# Step 6: Save cleaned dataset
output_path = 'dataset/cleaned_sales_dataset.csv'
df.to_csv(output_path, index=False)
print(f"\nCleaned dataset saved to {output_path}")
print(f"Final shape: {df.shape}")
print("\nFinal info:")
print(df.info())
print("\nCleaning complete!")

