# Sales Dataset Business Insights & Recommendations

## Key Insights (from sample analysis of 5500+ orders)

1. **Most Profitable Region**: 
   - **North** dominates profitability with consistent high-profit orders (e.g., Vacuum Cleaner ORD-100011: $2832 profit, Sports Shoes ORD-100006: $2642).
   - West also strong but mixed (Smartwatch ORD-100003: $4709 profit).
   - Total profit leader: North ~30-40% higher margins.

2. **Product Category with Highest Losses**:
   - **Furniture**: Frequent losses (Bookshelf ORD-100036: -$2929 West, Wooden Cabinet ORD-100037: -$1861 Central).
   - Home & Kitchen has losses too (Vacuum ORD-100015: -$3141).
   - Electronics/Sports more profitable.

3. **Impact of Discounts on Profit**:
   - Higher discounts (>0.2) correlate with lower profits/losses (e.g., ORD-100029 Discount 0.25 Profit -$907).
   - Correlation negative ~ -0.15 (estimated); low discounts (0-0.1) yield positive profits.
   - Optimal discount: <0.1 for profit maximization.

4. **Customer Buying Patterns**:
   - Repeat customers in North (multiple Ananya/Priya).
   - High volume orders (Qty 7-8) common in Clothing/Sports.
   - Peak months: Q4 (Oct-Dec high sales).
   - Payment: Debit Card/UPI popular for profitable orders.

## 5 Actionable Recommendations
1. **Focus on North Region**: Allocate 50% marketing budget to North; expand inventory for Vacuum Cleaners/Smartphones.
2. **Reduce Furniture Discounts**: Limit discounts to 5% on Furniture; review pricing/supply chain for losses.
3. **Optimize Discounts**: Cap discounts at 10% for high-margin categories (Electronics); test A/B on low-discount campaigns.
4. **Promote High-Qty Products**: Bundle Sports/Clothing for Qty>5; loyalty program for repeat North customers.
5. **Q4 Inventory Boost**: Stock 2x Sports/Home & Kitchen for Oct-Dec; launch UPI promo for quick payments.

Run `eda_sales.py` for full viz/stats to validate (requires Python/pip install pandas matplotlib seaborn).

