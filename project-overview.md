# Sales & Customer Intelligence Platform Overview 📈

This document provides a technical overview of the advanced sales analytics platform, outlining its pipeline, modeling decisions, and structural design.

## 1. Data Pipeline & ETL Architecture

The data pipeline transitions from unstructured inputs to a relational database to ensure high-speed dashboard analytics and recruiter SQL testing:

```
[Raw sales_dataset_5500.csv] 
           │ 
           ▼ (clean_sales_data.py)
   - Removes duplicate Order IDs
   - Drops rows with missing critical cells (Sales, Quantity, Date)
   - Fills null categorical records with 'Unknown'
   - Imputes null Profits with median values
           │ 
           ▼ [cleaned_sales_dataset.csv]
           │ 
           ▼ (load_db.py)
   - Renames spacing in columns to underscored names for SQLite ease
   - Writes rows into 'sales' table inside sales.db
           │ 
           ▼ [sales.db] (Local SQLite relational database)
```

---

## 2. Advanced Mathematical & Analytics Engine

### A. Customer Analytics (RFM & K-Means)
- **Recency**: Calculates $days = \text{max}(\text{Order Date}) - \text{Order Date}_{customer}$.
- **Frequency**: Computes unique orders count per customer.
- **Monetary**: Sums transaction amounts per customer.
- **Scaling**: Natural log transform is applied to RFM vectors to compress the right-skewed distribution, followed by standard scale normalization ($\mu=0, \sigma=1$).
- **Clustering**: K-Means clustering aggregates segments dynamically.

### B. Market Basket Analysis (Apriori)
- Group orders into transaction-product binary matrices.
- Applies the **Apriori Algorithm** to determine item support:
  $$\text{Support}(A \rightarrow B) = P(A \cap B)$$
- Renders cross-sell recommendations sorted by **Lift**:
  $$\text{Lift}(A \rightarrow B) = \frac{P(A \cap B)}{P(A) \times P(B)}$$

### C. Multi-Model Time Series Forecasting
- Aggregates filtered historical revenue monthly.
- **Statistical Model**: Fits **Prophet** (seasonality-based forecast with uncertainty intervals).
- **Machine Learning Model**: Creates trend index features with 1-month and 2-month autoregressive lags ($Y_{t-1}, Y_{t-2}$) and trains a **Random Forest Regressor**.
- **Recursive Forecasting**: Lags are updated iteratively to forecast future steps.
- **Train-Test Validation**: Splitting historical data computes MAPE and RMSE validation scores on a test holdout.

### D. Strategic What-If Simulator
- Leverages managerial accounting definitions:
  $$\text{Profit} = \text{Revenue} - (\text{Fixed Cost} + \text{Variable Cost})$$
- Splits costs ($\text{Cost} = \text{Revenue} - \text{Profit}$) into 30% fixed (volume-invariant) and 70% variable (volume-scaling) components.
- Simulates price, volume, and discount adjustments dynamically.

---

## 3. SQL Analytics Workspace
Recruiters can query the SQLite relational tables. Five templates are preloaded:
- Sales by Region
- Top 5 Customers by Revenue
- Monthly Sales Trend
- Most Profitable Products
- Customer Repeat Purchases
