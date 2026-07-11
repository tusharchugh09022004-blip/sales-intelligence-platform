-- SQL Queries for Sales Dataset Analysis
-- Assume table 'sales' with columns from cleaned_sales_dataset.csv:
-- Order ID, Order Date (datetime), Customer Name, Region, Product Category, Product Name, Sales Amount, Quantity, Profit, Discount, Payment Mode, Month, Year
-- Load CSV into SQLite/DB first for execution.

-- 1. Total Sales per Region (SUM Sales Amount grouped by Region)
SELECT 
    Region,
    ROUND(SUM("Sales Amount"), 2) AS total_sales,
    COUNT(*) AS order_count
FROM sales 
GROUP BY Region 
ORDER BY total_sales DESC;

-- Explanation: Aggregates total revenue by region to identify top markets.

-- 2. Top 5 Customers by Revenue
SELECT 
    "Customer Name",
    ROUND(SUM("Sales Amount"), 2) AS total_revenue,
    COUNT(DISTINCT "Order ID") AS orders
FROM sales 
GROUP BY "Customer Name" 
ORDER BY total_revenue DESC 
LIMIT 5;

-- Explanation: Identifies high-value customers for loyalty programs.

-- 3. Monthly Sales Trend (GROUP by Year, Month)
SELECT 
    Year,
    Month,
    ROUND(SUM("Sales Amount"), 2) AS monthly_sales,
    ROUND(AVG("Sales Amount"), 2) AS avg_order_value
FROM sales 
GROUP BY Year, Month 
ORDER BY Year DESC, Month DESC;

-- Explanation: Shows sales seasonality for inventory planning.

-- 4. Products with Highest Profit (Top 10 by total profit)
SELECT 
    "Product Name",
    "Product Category",
    ROUND(SUM(Profit), 2) AS total_profit,
    AVG(Profit) AS avg_profit,
    COUNT(*) AS sales_count
FROM sales 
GROUP BY "Product Name" 
ORDER BY total_profit DESC 
LIMIT 10;

-- Explanation: Highlights top profitable items to promote/stock more.

-- 5. Customers with Repeated Purchases (2+ orders)
SELECT 
    "Customer Name",
    COUNT(DISTINCT "Order ID") AS repeat_orders,
    ROUND(SUM("Sales Amount"), 2) AS total_spent,
    MIN("Order Date") AS first_order,
    MAX("Order Date") AS last_order
FROM sales 
GROUP BY "Customer Name" 
HAVING repeat_orders >= 2 
ORDER BY repeat_orders DESC, total_spent DESC;

-- Explanation: Finds loyal customers for targeted retention campaigns.

-- Usage: 
-- sqlite3 sales.db
-- .mode csv
-- .import dataset/cleaned_sales_dataset.csv sales
-- Run queries above.

