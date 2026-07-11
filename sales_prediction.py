import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("Sales Prediction Model")
print("=" * 50)

# Step 1: Load cleaned data
df = pd.read_csv('dataset/cleaned_sales_dataset.csv')
print(f"Loaded {len(df)} rows")
print("\nData preview:")
print(df[['Order Date', 'Sales Amount', 'Month', 'Year']].head())

# Step 2: Aggregate monthly sales
df['Order Date'] = pd.to_datetime(df['Order Date'])
monthly_sales = df.groupby(['Year', 'Month'])['Sales Amount'].sum().reset_index()
monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(day=1))
monthly_sales = monthly_sales.sort_values('Date').reset_index(drop=True)
monthly_sales['Month_Num'] = np.arange(len(monthly_sales))  # Numeric time index

print("\nMonthly sales aggregated:")
print(monthly_sales.head())

# Step 3: Prepare data for Linear Regression (train on all historical)
X = monthly_sales[['Month_Num']]
y = monthly_sales['Sales Amount']
model = LinearRegression()
model.fit(X, y)

# Predict on historical
monthly_sales['Predicted'] = model.predict(X)

# Metrics
rmse = np.sqrt(mean_squared_error(y, monthly_sales['Predicted']))
r2 = r2_score(y, monthly_sales['Predicted'])
print(f"\nModel Metrics:")
print(f"R² Score: {r2:.3f}")
print(f"RMSE: {rmse:,.0f}")

print("\nActual vs Predicted (last 6 months):")
print(monthly_sales[['Date', 'Sales Amount', 'Predicted']].tail(6).round(0))

# Step 4: Predict next 3 months
last_month = monthly_sales['Month_Num'].max()
future_months = np.array([[last_month + 1], [last_month + 2], [last_month + 3]])
future_dates = [monthly_sales['Date'].max() + pd.DateOffset(months=i) for i in range(1, 4)]
future_sales = model.predict(future_months)

print("\nNext 3 Months Predictions:")
for date, sales in zip(future_dates, future_sales):
    print(f"{date.strftime('%Y-%m')}: {sales:,.0f}")

# Step 5: Plot
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['Date'], monthly_sales['Sales Amount'], 'o-', label='Actual Sales', color='blue')
plt.plot(monthly_sales['Date'], monthly_sales['Predicted'], 's--', label='Fitted', color='green')
plt.plot(future_dates, future_sales, 'ro-', label='Predicted Next 3M', markersize=10, linewidth=3)
plt.title('Monthly Sales Trend & Linear Regression Forecast', fontsize=16)
plt.xlabel('Date')
plt.ylabel('Sales Amount')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sales_forecast.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nPlot saved as 'sales_forecast.png'")
print("Model complete! Linear regression assumes linear trend; consider ARIMA/LSTM for advanced.")
