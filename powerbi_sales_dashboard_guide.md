# Step-by-Step Guide: Advanced Power BI Sales Dashboard

## Prerequisites
1. Download Power BI Desktop (free): https://powerbi.microsoft.com/desktop/
2. Use `dataset/cleaned_sales_dataset.csv` (run `python clean_sales_data.py` first).
3. Ensure columns: Order Date (Date), Sales Amount, Profit, Region, Product Category, Product Name, Month, Year, etc.

## Step 1: Import Data
1. Open Power BI Desktop.
2. Get Data > Text/CSV > Select `cleaned_sales_dataset.csv`.
3. Load (or Transform Data for quick fixes).
4. Confirm data types: Sales Amount/Profit (Decimal), Order Date (Date), Region/Category (Text).

## Step 2: Create Measures (DAX)
In Data view > New Measure:
```
Total Sales = SUM(sales[Sales Amount])
Total Profit = SUM(sales[Profit])
Total Orders = COUNT(sales[Order ID])
Avg Order Value = DIVIDE([Total Sales], [Total Orders])
Profit Margin % = DIVIDE([Total Profit], [Total Sales]) * 100
Top Products Sales = TOPN(10, SUMMARIZE(sales, sales[Product Name], "Sales", SUM(sales[Sales Amount])), [Sales], DESC)
```

## Step 3: Build Visuals (Insert > Visualizations)
Create new Report page: "Sales Dashboard".

**1. KPI Cards (Top row)**:
   - Card visual x3: [Total Sales], [Total Profit], [Total Orders].
   - Format: Large font, currency (₹/$), conditional formatting (green for profit).

**2. Line Chart: Sales over Time**:
   - X: Order Date (hierarchy Year>Month).
   - Y: [Total Sales].
   - Legend: Region (multi-line).

**3. Bar Chart: Sales by Region**:
   - X: Region.
   - Y: [Total Sales].
   - Stacked by: Product Category.

**4. Pie/Donut Chart: Category Distribution**:
   - Legend: Product Category.
   - Values: [Total Sales] or COUNT rows.

**5. Table: Top Products**:
   - Fields: Product Name, Product Category, [Sales Amount], Profit.
   - Top N filter: Top 10 by Sales Amount.
   - Conditional formatting: Profit (red/green).

**6. Filters (Right/Slicer pane)**:
   - Slicer (Region): Dropdown/List.
   - Slicer (Product Category): List.
   - Slicer (Date): Relative (Last 1Y) or Between.
   - Sync slicers across pages.

## Step 4: Professional Layout Design
**Canvas Layout (16:9)**:
```
[Title: "Sales Analytics Dashboard" - Bold, center]

Row 1 (KPIs):          | KPI Sales | KPI Profit | KPI Orders |
                       [Large cards, icons]

Row 2:                 [Line: Sales Trend] (full width)
                       X:Time Y:Sales Legend:Region

Row 3 (1/3 split):     [Bar: Region] | [Pie: Category] | [Filters Column]
                       Sales stacked  Distribution     Region/Category/Date

Row 4:                 [Table: Top Products] (full width)
```

- **Theme**: Corporate Blue/Green (File > Options > Themes).
- **Background**: Subtle gradient or company logo.
- **Interactivity**: Cross-filter/highlight enabled.
- **Bookmarks**: Toggle views (e.g., YTD vs All Time).

## Step 5: Advanced Features
1. **Bookmarks**: Create "Overview" / "Deep Dive".
2. **Drill-through**: Region page with details.
3. **Tooltips**: Custom (Sales, Profit, Count).
4. **Publish**: Save .pbix; Publish to Power BI Service for sharing.

## Step 6: Test & Refresh
- Refresh data.
- Apply filters, check interactions.
- Export PDF/PowerPoint.

Dashboard ready for stakeholders! Questions? Ask.

