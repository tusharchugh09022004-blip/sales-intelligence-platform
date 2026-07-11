import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.style.use('default')
sns.set_palette("husl")

# Load data (prefer cleaned)
try:
    df = pd.read_csv('dataset/cleaned_sales_dataset.csv')
    print("Loaded cleaned dataset.")
except:
    df = pd.read_csv('dataset/sales_dataset_5500.csv')
    print("Loaded original dataset.")

print(f"Dataset shape: {df.shape}")
print(df.head())
print(df.info())
print(df.describe())

# Ensure datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

# 1. Total sales, total profit, average order value
total_sales = df['Sales Amount'].sum()
total_profit = df['Profit'].sum()
avg_order_value = df['Sales Amount'].mean()
print(f"\nTotal Sales: ${total_sales:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Average Order Value: ${avg_order_value:.2f}")

# 2. Sales trend over time
df_trend = df.copy()
df_trend['Year'] = df_trend['Order Date'].dt.year
df_trend['Month'] = df_trend['Order Date'].dt.month

monthly_sales = df_trend.groupby(['Year', 'Month'])['Sales Amount'].sum().reset_index()
monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(day=1))

plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['Date'], monthly_sales['Sales Amount'], marker='o')
plt.title('Sales Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Sales Amount')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sales_trend.png')
plt.show()

print("\nInsight: Sales trend shows... (check plot)")

# Profit trend similar
monthly_profit = df_trend.groupby(['Year', 'Month'])['Profit'].sum().reset_index()
monthly_profit['Date'] = pd.to_datetime(monthly_profit[['Year', 'Month']].assign(day=1))

plt.figure(figsize=(12, 6))
plt.plot(monthly_profit['Date'], monthly_profit['Profit'], marker='o', color='green')
plt.title('Profit Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Profit')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('profit_trend.png')
plt.show()

# 3. Top 10 products by sales
top_products = df.groupby('Product Name')['Sales Amount'].sum().nlargest(10).reset_index()
print("\nTop 10 Products by Sales:")
print(top_products)

plt.figure(figsize=(10, 6))
sns.barplot(data=top_products, x='Sales Amount', y='Product Name')
plt.title('Top 10 Products by Sales')
plt.tight_layout()
plt.savefig('top_products.png')
plt.show()

# 4. Sales by region
sales_region = df.groupby('Region')['Sales Amount'].sum().reset_index()
print("\nSales by Region:")
print(sales_region)

plt.figure(figsize=(8, 6))
plt.pie(sales_region['Sales Amount'], labels=sales_region['Region'], autopct='%1.1f%%')
plt.title('Sales by Region')
plt.savefig('sales_by_region.png')
plt.show()

plt.figure(figsize=(10, 6))
sns.barplot(data=sales_region, x='Region', y='Sales Amount')
plt.title('Sales by Region Bar')
plt.tight_layout()
plt.savefig('sales_region_bar.png')
plt.show()

# 5. Profit vs Discount analysis
print("\nProfit vs Discount correlation:", df['Profit'].corr(df['Discount']))

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Discount', y='Profit', alpha=0.6)
sns.regplot(data=df, x='Discount', y='Profit', scatter=False)
plt.title('Profit vs Discount')
plt.xlabel('Discount')
plt.ylabel('Profit')
plt.tight_layout()
plt.savefig('profit_vs_discount.png')
plt.show()

# Additional insights
print("\nProfitability by Category:")
cat_profit = df.groupby('Product Category')['Profit'].agg(['mean', 'sum']).round(2)
print(cat_profit)

print("\nEDA complete! Check PNG files for visualizations.")

