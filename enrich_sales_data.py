import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("Sales Data Enrichment Pipeline")
print("=" * 50)

# Step 1: Load cleaned data
df = pd.read_csv('dataset/cleaned_sales_dataset.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
print(f"Loaded {len(df)} rows from cleaned dataset.")
print(f"Columns before enrichment: {list(df.columns)}")

# ==============================================
# TEMPORAL & SEASONAL FEATURES
# ==============================================

# Quarter
df['Quarter'] = df['Order Date'].dt.quarter.map({1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})

# Is_Weekend
df['Is_Weekend'] = df['Order Date'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)

# Season (based on month)
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

df['Season'] = df['Order Date'].dt.month.apply(get_season)

# Day of Week name
df['Day_of_Week'] = df['Order Date'].dt.day_name()

print("Added temporal features: Quarter, Is_Weekend, Season, Day_of_Week")

# ==============================================
# PRICING & PROFITABILITY FEATURES
# ==============================================

# Unit Price (price per item, before discount)
df['Unit_Price'] = (df['Sales Amount'] / df['Quantity'].replace(0, np.nan)).round(2)

# Discount Amount (absolute dollar amount discounted)
df['Discount_Amount'] = (df['Sales Amount'] * df['Discount']).round(2)

# Profit Margin % per transaction
df['Profit_Margin_Pct'] = (
    df['Profit'] / df['Sales Amount'].replace(0, np.nan) * 100
).round(2)

# Revenue Category: classify each transaction by its revenue quartile
quantile_33 = df['Sales Amount'].quantile(0.33)
quantile_66 = df['Sales Amount'].quantile(0.66)

def classify_aov(val):
    if val <= quantile_33:
        return 'Low-Value'
    elif val <= quantile_66:
        return 'Medium-Value'
    else:
        return 'High-Value'

df['AOV_Segment'] = df['Sales Amount'].apply(classify_aov)

print("Added pricing features: Unit_Price, Discount_Amount, Profit_Margin_Pct, AOV_Segment")

# ==============================================
# CUSTOMER LIFETIME BEHAVIORAL FEATURES
# ==============================================

# Total lifetime spend per customer
customer_ltv = df.groupby('Customer Name')['Sales Amount'].sum().rename('Customer_LTV')
df = df.merge(customer_ltv, on='Customer Name', how='left')
df['Customer_LTV'] = df['Customer_LTV'].round(2)

# Total orders placed by each customer
customer_freq = df.groupby('Customer Name')['Order ID'].nunique().rename('Customer_Frequency')
df = df.merge(customer_freq, on='Customer Name', how='left')

# Is Repeat Customer flag
df['Is_Repeat_Customer'] = df['Customer_Frequency'].apply(lambda x: 1 if x >= 2 else 0)

# Customer Value Tier based on LTV
ltv_33 = df['Customer_LTV'].quantile(0.33)
ltv_66 = df['Customer_LTV'].quantile(0.66)

def classify_customer_tier(val):
    if val <= ltv_33:
        return 'Bronze'
    elif val <= ltv_66:
        return 'Silver'
    else:
        return 'Gold'

df['Customer_Tier'] = df['Customer_LTV'].apply(classify_customer_tier)

print("Added customer features: Customer_LTV, Customer_Frequency, Is_Repeat_Customer, Customer_Tier")

# ==============================================
# PRODUCT-LEVEL FEATURES
# ==============================================

# Product average profit margin across all sales
prod_margin = df.groupby('Product Name')['Profit_Margin_Pct'].mean().rename('Avg_Product_Margin_Pct').round(2)
df = df.merge(prod_margin, on='Product Name', how='left')

# Product total revenue rank (1 = top seller)
prod_rank = df.groupby('Product Name')['Sales Amount'].sum().rank(ascending=False, method='dense').astype(int)
df['Product_Revenue_Rank'] = df['Product Name'].map(prod_rank)

print("Added product features: Avg_Product_Margin_Pct, Product_Revenue_Rank")

# ==============================================
# FINAL SAVE
# ==============================================

output_path = 'dataset/enriched_sales_dataset.csv'
df.to_csv(output_path, index=False)
print(f"\nEnriched dataset saved to: {output_path}")
print(f"Total rows: {len(df)}")
print(f"\nNew columns added ({len(df.columns)} total):")
print(list(df.columns))
print("\nSample of enriched data:")
print(df[['Customer Name', 'Product Name', 'Sales Amount', 'Quarter', 'Is_Weekend', 'Season',
          'Unit_Price', 'Discount_Amount', 'Profit_Margin_Pct', 'AOV_Segment',
          'Customer_LTV', 'Customer_Frequency', 'Is_Repeat_Customer', 'Customer_Tier',
          'Avg_Product_Margin_Pct', 'Product_Revenue_Rank']].head(3).to_string())
print("\nEnrichment complete!")
