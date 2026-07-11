import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import sqlite3
import os
import warnings

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="Sales & Customer Intelligence Platform", layout="wide", page_icon="📈")

# ============================================
# UNIFIED PLOTLY TEMPLATE
# ============================================
BRAND_COLORS = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
pio.templates["custom"] = go.layout.Template(
    layout=go.Layout(
        plot_bgcolor='#fafafa',
        paper_bgcolor='white',
        font=dict(family="sans-serif", size=13, color="#262730"),
        colorway=BRAND_COLORS,
        xaxis=dict(gridcolor='#e9ecef', zerolinecolor='#e9ecef'),
        yaxis=dict(gridcolor='#e9ecef', zerolinecolor='#e9ecef'),
    )
)
pio.templates.default = "custom"

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    /* Metric card styling */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #6c757d !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }

    /* Reduce top padding */
    .block-container { padding-top: 1.5rem; }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 1px solid #dee2e6;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h1 {
        font-size: 1.2rem !important;
        color: #2c3e50 !important;
    }

    /* Hide default Streamlit footer and menu */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* Header styling */
    h1 { color: #1a1a2e; letter-spacing: -0.5px; }
    h2, h3 { color: #2c3e50; }

    /* Tab styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }

    /* Expander styling */
    [data-testid="stExpander"] {
        border: 1px solid #e9ecef;
        border-radius: 8px;
    }

    /* DataFrame styling */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Success/Info/Warning boxes */
    .stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Main Header
st.title("Advanced Sales & Customer Intelligence Platform")
st.caption("Enterprise-grade analytics dashboard with customer segmentation, recommendation engines, time-series forecasting, and an interactive SQL query workspace.")
st.divider()

# Cohort Calculation Helper
def calculate_cohort_retention(df_cohort):
    try:
        df_cohort = df_cohort.copy()
        df_cohort['Order_Date'] = pd.to_datetime(df_cohort['Order Date'])
        df_cohort['OrderMonth'] = df_cohort['Order_Date'].dt.to_period('M')
        df_cohort['CohortMonth'] = df_cohort.groupby('Customer Name')['Order_Date'].transform('min').dt.to_period('M')
        
        cohort_grouped = df_cohort.groupby(['CohortMonth', 'OrderMonth']).agg(n_customers=('Customer Name', 'nunique')).reset_index()
        cohort_grouped['CohortIndex'] = (cohort_grouped['OrderMonth'] - cohort_grouped['CohortMonth']).apply(lambda attr: attr.n)
        
        cohort_pivot = cohort_grouped.pivot(index='CohortMonth', columns='CohortIndex', values='n_customers')
        cohort_size = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(cohort_size, axis=0) * 100
        retention.index = retention.index.astype(str)
        return retention
    except Exception as e:
        return None

# Executive PDF Report Generator Helper
def generate_pdf_report(filtered_df, min_y, max_y, insights):
    from fpdf import FPDF
    from datetime import datetime
    
    # Calculate stats
    total_sales = filtered_df['Sales Amount'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_orders = len(filtered_df)
    avg_order_value = filtered_df['Sales Amount'].mean()
    profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
    
    # Aggregations for tables
    region_sales = filtered_df.groupby('Region').agg(
        Sales_Amount=('Sales Amount', 'sum'),
        Order_Count=('Order ID', 'count')
    ).reset_index().sort_values('Sales_Amount', ascending=False)
    
    cat_sales = filtered_df.groupby('Product Category')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False)
    
    top_prods = filtered_df.groupby('Product Name')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False).head(5)
    
    # Initialize PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Banner Header
    pdf.set_fill_color(44, 62, 80) # Dark Blue
    pdf.rect(0, 0, 210, 42, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.set_font('helvetica', 'B', 18)
    pdf.cell(text="SALES & CUSTOMER INTELLIGENCE PLATFORM", ln=True, align='C')
    pdf.set_font('helvetica', 'I', 10)
    pdf.cell(text="Automated Executive Summary & Insights Report", ln=True, align='C')
    pdf.set_font('helvetica', size=8)
    pdf.cell(text=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target Years: {min_y} - {max_y}", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(48)
    
    # Section 1: Key Performance Indicators
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(text="1. Executive Key Performance Indicators (KPIs)", ln=True)
    pdf.ln(3)
    
    # KPI Table - Manual rendering
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    
    # Header row
    pdf.cell(47, 7, "Metric", 1, 0, 'C', True)
    pdf.cell(47, 7, "Value", 1, 0, 'C', True)
    pdf.cell(47, 7, "Metric", 1, 0, 'C', True)
    pdf.cell(47, 7, "Value", 1, 1, 'C', True)
    
    pdf.set_font('helvetica', size=10)
    pdf.set_fill_color(255, 255, 255)
    
    # Data rows
    pdf.cell(47, 7, "Total Sales", 1, 0, 'L', True)
    pdf.cell(47, 7, f"${total_sales:,.2f}", 1, 0, 'R', True)
    pdf.cell(47, 7, "Total Profit", 1, 0, 'L', True)
    pdf.cell(47, 7, f"${total_profit:,.2f}", 1, 1, 'R', True)
    
    pdf.cell(47, 7, "Total Orders", 1, 0, 'L', True)
    pdf.cell(47, 7, f"{total_orders:,}", 1, 0, 'R', True)
    pdf.cell(47, 7, "Avg Order Value", 1, 0, 'L', True)
    pdf.cell(47, 7, f"${avg_order_value:,.2f}", 1, 1, 'R', True)
    
    pdf.cell(47, 7, "Profit Margin", 1, 0, 'L', True)
    pdf.cell(47, 7, f"{profit_margin:.2f}%", 1, 0, 'R', True)
    pdf.cell(47, 7, "Reporting Period", 1, 0, 'L', True)
    pdf.cell(47, 7, f"{min_y} - {max_y}", 1, 1, 'R', True)
    
    pdf.ln(5)
    
    # Section 2: Regional & Category Performance Breakdown
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(text="2. Regional & Category Performance Breakdown", ln=True)
    pdf.ln(3)
    
    # Region Table
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(text="Sales by Region:", ln=True)
    pdf.ln(2)
    
    # Region table header
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(70, 6, "Region", 1, 0, 'C', True)
    pdf.cell(60, 6, "Sales Amount", 1, 0, 'C', True)
    pdf.cell(60, 6, "Order Count", 1, 1, 'C', True)
    
    # Region table data
    pdf.set_font('helvetica', size=9)
    pdf.set_fill_color(255, 255, 255)
    for _, row in region_sales.iterrows():
        pdf.cell(70, 6, str(row['Region']), 1, 0, 'L', True)
        pdf.cell(60, 6, f"${row['Sales_Amount']:,.2f}", 1, 0, 'R', True)
        pdf.cell(60, 6, f"{row['Order_Count']:,}", 1, 1, 'R', True)
    
    pdf.ln(5)
    
    # Category Table
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(text="Sales by Product Category:", ln=True)
    pdf.ln(2)
    
    # Category table header
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(95, 6, "Product Category", 1, 0, 'C', True)
    pdf.cell(95, 6, "Sales Amount", 1, 1, 'C', True)
    
    # Category table data
    pdf.set_font('helvetica', size=9)
    pdf.set_fill_color(255, 255, 255)
    for _, row in cat_sales.iterrows():
        pdf.cell(95, 6, str(row['Product Category']), 1, 0, 'L', True)
        pdf.cell(95, 6, f"${row['Sales Amount']:,.2f}", 1, 1, 'R', True)
    
    pdf.ln(5)
    
    # Section 3: Top Products
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(text="3. Top 5 Best-Selling Products", ln=True)
    pdf.ln(3)
    
    # Top products table header
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(140, 6, "Product Name", 1, 0, 'C', True)
    pdf.cell(50, 6, "Sales Amount", 1, 1, 'C', True)
    
    # Top products table data
    pdf.set_font('helvetica', size=9)
    pdf.set_fill_color(255, 255, 255)
    for _, row in top_prods.iterrows():
        pdf.cell(140, 6, str(row['Product Name']), 1, 0, 'L', True)
        pdf.cell(50, 6, f"${row['Sales Amount']:,.2f}", 1, 1, 'R', True)
    
    pdf.ln(5)
    
    # Section 4: Automated Insights
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(text="4. Automated Business Insights & Recommendations", ln=True)
    pdf.ln(3)
    
    pdf.set_font('helvetica', size=10)
    for insight in insights:
        clean_insight = insight.replace("⭐ ", "").replace("📊 ", "").replace("🔄 ", "").replace("💰 ", "").replace("**", "")
        pdf.cell(text=f"- {clean_insight}", ln=True)
        pdf.ln(2)
        
    return bytes(pdf.output())

# Data Source Selection
data_source = st.radio("Choose Data Source:", ["Local SQLite Database (sales.db)", "Upload Sales CSV"], horizontal=True)


df = None
if data_source == "Local SQLite Database (sales.db)":
    db_path = "sales.db"
    if not os.path.exists(db_path):
        st.warning("Database sales.db not found. Running load_db.py to create it...")
        try:
            import subprocess
            subprocess.run(["python", "load_db.py"], check=True)
        except Exception as e:
            st.error(f"Failed to automatically create database: {e}")
            
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            # Read and map column names back to spaces
            df = pd.read_sql_query("SELECT * FROM sales", conn)
            df.columns = [col.replace('_', ' ') for col in df.columns]
            conn.close()
            st.success(f"Loaded {len(df):,} rows from local SQLite database!")
        except Exception as e:
            st.error(f"Error connecting to database: {e}. Please ensure load_db.py ran successfully.")
    else:
        st.error("Could not find sales.db. Please run python load_db.py manually.")
else:
    uploaded_file = st.file_uploader("Upload sales CSV", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df):,} rows from uploaded CSV.")

# If data loaded successfully, show dashboard
if df is not None:
    # Auto-clean dates and drop blank sales rows
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df['Year'] = df['Order Date'].dt.year
        df['Month'] = df['Order Date'].dt.month
    df = df.dropna(subset=['Sales Amount'])
    
    # Sidebar Filters
    st.sidebar.markdown("### Sales Intelligence Platform")
    st.sidebar.caption("v2.0 | Advanced Analytics Dashboard")
    st.sidebar.divider()
    st.sidebar.header("Global Filters")
    region_options = sorted(df['Region'].dropna().unique())
    region_filter = st.sidebar.multiselect("Region", options=region_options, default=region_options)
    st.sidebar.divider()
    category_options = sorted(df['Product Category'].dropna().unique())
    category_filter = st.sidebar.multiselect("Category", options=category_options, default=category_options)
    st.sidebar.divider()
    
    year_filter = None
    if 'Year' in df.columns:
        min_y = int(df['Year'].min())
        max_y = int(df['Year'].max())
        if min_y == max_y:
            year_filter = (min_y, max_y)
        else:
            year_filter = st.sidebar.slider("Year Range", min_value=min_y, max_value=max_y, value=(min_y, max_y))
            
    # Apply Filters
    filtered_df = df[
        (df['Region'].isin(region_filter)) & 
        (df['Product Category'].isin(category_filter))
    ]
    if 'Year' in df.columns and year_filter is not None:
        filtered_df = filtered_df[(filtered_df['Year'] >= year_filter[0]) & (filtered_df['Year'] <= year_filter[1])]
        
    # Tab Layout Definition
    tab_dashboard, tab_forecasting, tab_customers, tab_basket, tab_churn, tab_simulator, tab_sql = st.tabs([
        "📊 Executive Dashboard", 
        "📈 Advanced Forecasting", 
        "👥 Customer Analytics", 
        "🛒 Market Basket Analysis",
        "⚠️ Churn Prediction",
        "🎛️ What-If Simulator", 
        "🗄️ SQL Workspace"
    ])
    
    # ==========================================
    # TAB 1: EXECUTIVE DASHBOARD
    # ==========================================
    with tab_dashboard:
        st.subheader("📊 Sales & Profit Overview")
        
        # KPI Row 1 – Core
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"${filtered_df['Sales Amount'].sum():,.0f}")
        with col2:
            st.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
        with col3:
            st.metric("Total Orders", f"{len(filtered_df):,}")
        with col4:
            st.metric("Avg Order Value", f"${filtered_df['Sales Amount'].mean():,.0f}")

        # KPI Row 2 – Enriched (shown only when enriched columns present)
        if 'Profit Margin Pct' in filtered_df.columns or 'Profit_Margin_Pct' in filtered_df.columns:
            margin_col = 'Profit Margin Pct' if 'Profit Margin Pct' in filtered_df.columns else 'Profit_Margin_Pct'
            ltv_col = 'Customer LTV' if 'Customer LTV' in filtered_df.columns else 'Customer_LTV'
            repeat_col = 'Is Repeat Customer' if 'Is Repeat Customer' in filtered_df.columns else 'Is_Repeat_Customer'
            weekend_col = 'Is Weekend' if 'Is Weekend' in filtered_df.columns else 'Is_Weekend'
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                st.metric("Avg Profit Margin %", f"{filtered_df[margin_col].mean():.1f}%")
            with e2:
                st.metric("Avg Customer LTV", f"${filtered_df[ltv_col].mean():,.0f}")
            with e3:
                repeat_pct = filtered_df[repeat_col].mean() * 100
                st.metric("Repeat Customer %", f"{repeat_pct:.1f}%")
            with e4:
                weekend_sales_pct = (filtered_df[filtered_df[weekend_col] == 1]['Sales Amount'].sum() / filtered_df['Sales Amount'].sum() * 100)
                st.metric("Weekend Sales Share", f"{weekend_sales_pct:.1f}%")
            
        st.divider()
        
        # Charts Row 1
        col_a, col_b = st.columns(2)
        with col_a:
            region_sales = filtered_df.groupby('Region')['Sales Amount'].sum().reset_index()
            fig_region = px.bar(region_sales, x='Region', y='Sales Amount', title="Sales by Region", color='Sales Amount', color_continuous_scale='Blues')
            st.plotly_chart(fig_region, use_container_width=True)
            
        with col_b:
            cat_sales = filtered_df.groupby('Product Category')['Sales Amount'].sum().reset_index()
            fig_cat = px.pie(cat_sales, values='Sales Amount', names='Product Category', title="Sales by Category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        # Charts Row 2
        col_c, col_d = st.columns(2)
        with col_c:
            monthly_sales = filtered_df.resample('ME', on='Order Date')['Sales Amount'].sum().reset_index()
            fig_trend = px.line(monthly_sales, x='Order Date', y='Sales Amount', title="Monthly Sales Trend", markers=True)
            fig_trend.update_traces(line_color='#2c3e50', line_width=2.5)
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with col_d:
            st.markdown("#### 🏆 Top 10 Products by Sales")
            top_prods = filtered_df.groupby('Product Name')['Sales Amount'].sum().reset_index().sort_values('Sales Amount', ascending=False).head(10)
            st.dataframe(top_prods.style.format({'Sales Amount': '${:,.0f}'}), use_container_width=True)
            
        st.divider()

        # Enriched Feature Charts (if enriched columns present)
        if 'Season' in filtered_df.columns or 'AOV Segment' in filtered_df.columns:
            st.subheader("📐 Enriched Analytics")
            season_col = 'Season' if 'Season' in filtered_df.columns else None
            aov_col = 'AOV Segment' if 'AOV Segment' in filtered_df.columns else ('AOV_Segment' if 'AOV_Segment' in filtered_df.columns else None)
            tier_col = 'Customer Tier' if 'Customer Tier' in filtered_df.columns else ('Customer_Tier' if 'Customer_Tier' in filtered_df.columns else None)

            ecol1, ecol2, ecol3 = st.columns(3)
            if season_col and season_col in filtered_df.columns:
                with ecol1:
                    season_sales = filtered_df.groupby(season_col)['Sales Amount'].sum().reset_index()
                    fig_season = px.bar(season_sales, x=season_col, y='Sales Amount',
                                       title='Sales by Season', color='Sales Amount',
                                       color_continuous_scale='Teal')
                    st.plotly_chart(fig_season, use_container_width=True)
            if aov_col and aov_col in filtered_df.columns:
                with ecol2:
                    aov_counts = filtered_df[aov_col].value_counts().reset_index()
                    aov_counts.columns = ['AOV Segment', 'Count']
                    fig_aov = px.pie(aov_counts, values='Count', names='AOV Segment',
                                     title='Order Value Segments', hole=0.4,
                                     color_discrete_sequence=px.colors.qualitative.Set2)
                    st.plotly_chart(fig_aov, use_container_width=True)
            if tier_col and tier_col in filtered_df.columns:
                with ecol3:
                    tier_sales = filtered_df.groupby(tier_col)['Sales Amount'].sum().reset_index()
                    tier_sales.columns = ['Customer Tier', 'Sales Amount']
                    color_map = {'Bronze': '#cd7f32', 'Silver': '#c0c0c0', 'Gold': '#ffd700'}
                    fig_tier = px.bar(tier_sales, x='Customer Tier', y='Sales Amount',
                                      title='Revenue by Customer Tier', color='Customer Tier',
                                      color_discrete_map=color_map)
                    st.plotly_chart(fig_tier, use_container_width=True)
            st.divider()

        # Automated Insights
        with st.expander("Automated Insights", expanded=True):
            insights = []
            
            if not filtered_df.empty:
                top_region_idx = filtered_df.groupby('Region')['Sales Amount'].sum().idxmax()
                top_region_sales = filtered_df[filtered_df['Region']==top_region_idx]['Sales Amount'].sum()
                insights.append(f"**Top Region**: {top_region_idx} (${top_region_sales:,.0f})")
                
                top_cat_idx = filtered_df.groupby('Product Category')['Sales Amount'].sum().idxmax()
                insights.append(f"**Top Category**: {top_cat_idx}")
                
                profit_margin = (filtered_df['Profit'].sum() / filtered_df['Sales Amount'].sum()) * 100
                insights.append(f"**Profit Margin**: {profit_margin:.1f}%")
                
                repeat_cust = len(filtered_df['Customer Name'].value_counts()[filtered_df['Customer Name'].value_counts() > 1])
                insights.append(f"**Repeat Customers**: {repeat_cust}")
                
                avg_discount = filtered_df['Discount'].mean() * 100
                insights.append(f"**Avg Discount**: {avg_discount:.1f}%")
                
                cols_ins = st.columns(len(insights))
                for idx, insight in enumerate(insights):
                    cols_ins[idx].info(insight)
            else:
                st.info("No data available for the selected filters.")
            
        # Download Buttons
        col_down1, col_down2 = st.columns(2)
        with col_down1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download Filtered Sales Data (CSV)", csv, "filtered_sales_data.csv", "text/csv", use_container_width=True)
            
        with col_down2:
            try:
                min_y_val = int(filtered_df['Year'].min()) if 'Year' in filtered_df.columns else int(df['Year'].min())
                max_y_val = int(filtered_df['Year'].max()) if 'Year' in filtered_df.columns else int(df['Year'].max())
                pdf_report_bytes = generate_pdf_report(filtered_df, min_y_val, max_y_val, insights)
                st.download_button("📄 Download Executive PDF Report", pdf_report_bytes, "executive_sales_report.pdf", "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Error generating PDF report: {e}")


    # ==========================================
    # TAB 2: ADVANCED FORECASTING
    # ==========================================
    with tab_forecasting:
        st.subheader("📈 Time Series Sales Forecasting")
        st.markdown("Compare **Prophet**, **Random Forest**, **XGBoost**, and **LightGBM** models with lag features and cross-validation.")
        
        # Aggregate monthly
        forecast_df = filtered_df.resample('ME', on='Order Date')['Sales Amount'].sum().reset_index()
        forecast_df = forecast_df.rename(columns={'Order Date': 'ds', 'Sales Amount': 'y'})
        forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
        forecast_df = forecast_df.sort_values('ds').reset_index(drop=True)
        
        min_points = 12
        if len(forecast_df) < min_points:
            st.warning(f"Not enough historical data for advanced forecasting. Need at least {min_points} monthly data points (Currently: {len(forecast_df)} months).")
        else:
            col_f1, col_f2 = st.columns([1, 3])
            with col_f1:
                st.markdown("#### Forecast Configuration")
                horizon = st.slider("Forecast Horizon (Months)", min_value=3, max_value=12, value=6)
                model_choice = st.selectbox("Select Model to Visualize", [
                    "Prophet", "Random Forest", "XGBoost", "LightGBM", "Compare All"
                ])
                
                val_size = 6 if len(forecast_df) > 18 else 3
                st.info(f"Train: first {len(forecast_df)-val_size} months | Validate: last {val_size} months")
                
                # Cross-validation folds
                n_folds = st.slider("Cross-Validation Folds", min_value=2, max_value=5, value=3)
                
            with col_f2:
                with st.spinner("Training forecasting models (Prophet, RF, XGBoost, LightGBM)..."):
                    # Prepare lag features for ML models
                    ml_full = forecast_df.copy()
                    ml_full['Lag_1'] = ml_full['y'].shift(1)
                    ml_full['Lag_2'] = ml_full['y'].shift(2)
                    ml_full['Month_Index'] = np.arange(len(ml_full))
                    ml_full = ml_full.dropna().reset_index(drop=True)
                    
                    # Validation Split
                    train_data = forecast_df.iloc[:-val_size].copy()
                    val_data = forecast_df.iloc[-val_size:].copy()
                    train_ml = ml_full.iloc[:-val_size].copy()
                    val_ml = ml_full.iloc[-val_size:].copy()
                    X_train = train_ml[['Month_Index', 'Lag_1', 'Lag_2']]
                    y_train = train_ml['y']
                    X_val = val_ml[['Month_Index', 'Lag_1', 'Lag_2']]
                    y_val = val_ml['y']
                    
                    from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
                    
                    # Helper: recursive ML forecast
                    def recursive_forecast(model, train_y, start_idx, steps, feature_names=None):
                        preds = []
                        lag1, lag2 = train_y[-1], train_y[-2]
                        idx = start_idx
                        for _ in range(steps):
                            if feature_names is not None:
                                X_pred = pd.DataFrame([[idx, lag1, lag2]], columns=feature_names)
                            else:
                                X_pred = np.array([[idx, lag1, lag2]])
                            p = model.predict(X_pred)[0]
                            preds.append(p)
                            lag2, lag1 = lag1, p
                            idx += 1
                        return preds
                    
                    # 1. Prophet
                    from prophet import Prophet
                    p_model = Prophet(interval_width=0.8, daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=True)
                    p_model.fit(train_data)
                    future_val = p_model.make_future_dataframe(periods=val_size, freq='ME')
                    forecast_val = p_model.predict(future_val)
                    val_pred_prophet = np.clip(forecast_val.iloc[-val_size:]['yhat'].values, 0, None)
                    
                    # 2. Random Forest
                    from sklearn.ensemble import RandomForestRegressor
                    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf_model.fit(X_train, y_train)
                    val_pred_rf = np.clip(recursive_forecast(rf_model, train_ml['y'].values, int(train_ml['Month_Index'].iloc[-1]) + 1, val_size), 0, None)
                    
                    # 3. XGBoost
                    from xgboost import XGBRegressor
                    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42, verbosity=0)
                    xgb_model.fit(X_train, y_train)
                    val_pred_xgb = np.clip(recursive_forecast(xgb_model, train_ml['y'].values, int(train_ml['Month_Index'].iloc[-1]) + 1, val_size), 0, None)
                    
                    # 4. LightGBM
                    from lightgbm import LGBMRegressor
                    lgbm_model = LGBMRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42, verbosity=-1)
                    lgbm_model.fit(X_train, y_train)
                    val_pred_lgbm = np.clip(recursive_forecast(lgbm_model, train_ml['y'].values, int(train_ml['Month_Index'].iloc[-1]) + 1, val_size, feature_names=['Month_Index', 'Lag_1', 'Lag_2']), 0, None)
                    
                    # Calculate metrics for all models
                    from sklearn.model_selection import TimeSeriesSplit
                    
                    def calc_metrics(y_true, y_pred):
                        mape = mean_absolute_percentage_error(y_true, y_pred) * 100
                        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                        return mape, rmse
                    
                    mape_p, rmse_p = calc_metrics(val_data['y'], val_pred_prophet)
                    mape_rf, rmse_rf = calc_metrics(val_data['y'], val_pred_rf)
                    mape_xgb, rmse_xgb = calc_metrics(val_data['y'], val_pred_xgb)
                    mape_lgbm, rmse_lgbm = calc_metrics(val_data['y'], val_pred_lgbm)
                    
                    # Cross-validation scores
                    tscv = TimeSeriesSplit(n_splits=n_folds)
                    cv_scores = {}
                    for name, model_cls, params in [
                        ("RF", RandomForestRegressor, {"n_estimators": 100, "random_state": 42}),
                        ("XGBoost", XGBRegressor, {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 4, "random_state": 42, "verbosity": 0}),
                        ("LightGBM", LGBMRegressor, {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 4, "random_state": 42, "verbosity": -1}),
                    ]:
                        fold_mapes = []
                        for train_idx, test_idx in tscv.split(ml_full):
                            Xtr = ml_full.iloc[train_idx][['Month_Index', 'Lag_1', 'Lag_2']]
                            ytr = ml_full.iloc[train_idx]['y']
                            Xte = ml_full.iloc[test_idx][['Month_Index', 'Lag_1', 'Lag_2']]
                            yte = ml_full.iloc[test_idx]['y']
                            m = model_cls(**params)
                            m.fit(Xtr, ytr)
                            preds = m.predict(Xte)
                            fold_mapes.append(mean_absolute_percentage_error(yte, preds) * 100)
                        cv_scores[name] = np.mean(fold_mapes)
                    
                    # Metrics table
                    st.markdown("#### Validation Metrics Comparison")
                    metrics_df = pd.DataFrame({
                        "Model": ["Prophet", "Random Forest", "XGBoost", "LightGBM"],
                        "MAPE (%)": [f"{mape_p:.2f}%", f"{mape_rf:.2f}%", f"{mape_xgb:.2f}%", f"{mape_lgbm:.2f}%"],
                        "RMSE ($)": [f"${rmse_p:,.2f}", f"${rmse_rf:,.2f}", f"${rmse_xgb:,.2f}", f"${rmse_lgbm:,.2f}"],
                        "CV MAPE (%)": ["—", f"{cv_scores['RF']:.2f}%", f"{cv_scores['XGBoost']:.2f}%", f"{cv_scores['LightGBM']:.2f}%"]
                    })
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    best_model = min(cv_scores, key=cv_scores.get)
                    st.success(f"Best CV model: **{best_model}** (MAPE: {cv_scores[best_model]:.2f}%)")
                
            # === Full Future Forecast ===
            # Prophet full fit
            p_full = Prophet(interval_width=0.8, daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=True)
            p_full.fit(forecast_df)
            future_full = p_full.make_future_dataframe(periods=horizon, freq='ME')
            forecast_full = p_full.predict(future_full)
            
            # ML full fit
            X_full = ml_full[['Month_Index', 'Lag_1', 'Lag_2']]
            y_full = ml_full['y']
            
            rf_full = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_full, y_full)
            xgb_full = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42, verbosity=0).fit(X_full, y_full)
            lgbm_full = LGBMRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42, verbosity=-1).fit(X_full, y_full)
            
            start_idx = int(ml_full['Month_Index'].iloc[-1]) + 1
            future_pred_rf = np.clip(recursive_forecast(rf_full, ml_full['y'].values, start_idx, horizon), 0, None)
            future_pred_xgb = np.clip(recursive_forecast(xgb_full, ml_full['y'].values, start_idx, horizon), 0, None)
            future_pred_lgbm = np.clip(recursive_forecast(lgbm_full, ml_full['y'].values, start_idx, horizon, feature_names=['Month_Index', 'Lag_1', 'Lag_2']), 0, None)
            
            future_dates = [forecast_df['ds'].max() + pd.DateOffset(months=i) for i in range(1, horizon+1)]
            
            # Plot
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['y'], mode='lines+markers', name='Actual', line=dict(color='#2c3e50', width=2.5)))
            
            if model_choice in ["Prophet", "Compare All"]:
                future_p_df = forecast_full.iloc[-horizon:]
                fig_fc.add_trace(go.Scatter(x=future_p_df['ds'], y=future_p_df['yhat'], mode='lines+markers', name='Prophet', line=dict(color='#e67e22', dash='dash')))
                fig_fc.add_trace(go.Scatter(
                    x=list(future_p_df['ds']) + list(future_p_df['ds'])[::-1],
                    y=list(future_p_df['yhat_upper']) + list(future_p_df['yhat_lower'])[::-1],
                    fill='toself', fillcolor='rgba(230, 126, 34, 0.15)',
                    line=dict(color='rgba(230, 126, 34, 0)'), name='Prophet CI (80%)'
                ))
            if model_choice in ["Random Forest", "Compare All"]:
                fig_fc.add_trace(go.Scatter(x=future_dates, y=future_pred_rf, mode='lines+markers', name='Random Forest', line=dict(color='#27ae60', dash='dot')))
            if model_choice in ["XGBoost", "Compare All"]:
                fig_fc.add_trace(go.Scatter(x=future_dates, y=future_pred_xgb, mode='lines+markers', name='XGBoost', line=dict(color='#8e44ad', dash='dashdot')))
            if model_choice in ["LightGBM", "Compare All"]:
                fig_fc.add_trace(go.Scatter(x=future_dates, y=future_pred_lgbm, mode='lines+markers', name='LightGBM', line=dict(color='#e74c3c', dash='longdash')))
                
            fig_fc.update_layout(
                title="Historical Sales & Future Forecasts",
                xaxis_title="Date", yaxis_title="Sales Amount ($)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                height=500
            )
            st.plotly_chart(fig_fc, use_container_width=True)

    # ==========================================
    # TAB 3: CUSTOMER ANALYTICS
    # ==========================================
    with tab_customers:
        st.subheader("👥 Customer Intelligence & Cohort Analysis")
        
        tab_rfm, tab_cohort = st.tabs(["🎯 RFM Clustering", "📅 Cohort Retention Heatmap"])
        
        with tab_rfm:
            st.markdown("#### RFM (Recency, Frequency, Monetary) Customer Segmentation")
            st.markdown("Customers are grouped using **K-Means Clustering** based on their shopping recency, frequency of purchases, and total spend.")
            
            # Calculate RFM
            max_date = filtered_df['Order Date'].max()
            rfm = filtered_df.groupby('Customer Name').agg({
                'Order Date': lambda x: (max_date - x.max()).days,
                'Order ID': 'nunique',
                'Sales Amount': 'sum'
            }).reset_index()
            rfm.columns = ['Customer Name', 'Recency', 'Frequency', 'Monetary']
            
            num_unique_cust = len(rfm)
            if num_unique_cust < 3:
                st.warning("Not enough unique customers to run clustering.")
            else:
                # Normalize and prepare scaled data
                from sklearn.preprocessing import StandardScaler
                from sklearn.cluster import KMeans
                from sklearn.metrics import silhouette_score
                
                rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].copy()
                rfm_log['Recency'] = np.log1p(rfm_log['Recency'])
                rfm_log['Frequency'] = np.log1p(rfm_log['Frequency'])
                rfm_log['Monetary'] = np.log1p(rfm_log['Monetary'])
                
                scaler = StandardScaler()
                rfm_scaled = scaler.fit_transform(rfm_log)
                
                # Elbow Method & Silhouette Analysis
                st.markdown("#### Optimal K Selection")
                elbow_col1, elbow_col2 = st.columns(2)
                
                max_k = min(10, num_unique_cust - 1)
                k_range = range(2, max_k + 1)
                inertias = []
                silhouette_scores = []
                
                for k in k_range:
                    km = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = km.fit_predict(rfm_scaled)
                    inertias.append(km.inertia_)
                    silhouette_scores.append(silhouette_score(rfm_scaled, labels))
                
                with elbow_col1:
                    fig_elbow = px.line(x=list(k_range), y=inertias, markers=True,
                                       title='Elbow Method (Inertia vs K)',
                                       labels={'x': 'Number of Clusters (K)', 'y': 'Inertia'})
                    fig_elbow.update_traces(line=dict(color='#3498db', width=3))
                    fig_elbow.update_layout(height=300)
                    st.plotly_chart(fig_elbow, use_container_width=True)
                
                with elbow_col2:
                    fig_sil = px.line(x=list(k_range), y=silhouette_scores, markers=True,
                                     title='Silhouette Score vs K',
                                     labels={'x': 'Number of Clusters (K)', 'y': 'Silhouette Score'})
                    fig_sil.update_traces(line=dict(color='#e74c3c', width=3))
                    fig_sil.update_layout(height=300)
                    st.plotly_chart(fig_sil, use_container_width=True)
                
                best_k = list(k_range)[np.argmax(silhouette_scores)]
                st.info(f"Optimal K by silhouette score: **{best_k}** (score: {max(silhouette_scores):.3f})")
                
                col_c1, col_c2 = st.columns([1, 2])
                with col_c1:
                    num_clusters = st.slider("Select Number of Clusters (K)", min_value=2, max_value=max_k, value=best_k)
                    
                    # Fit final model
                    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
                    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
                    
                    final_silhouette = silhouette_score(rfm_scaled, rfm['Cluster'])
                    st.metric("Silhouette Score", f"{final_silhouette:.3f}")
                    
                    # Group Stats
                    cluster_stats = rfm.groupby('Cluster').agg({
                        'Recency': 'mean',
                        'Frequency': 'mean',
                        'Monetary': ['mean', 'count']
                    }).reset_index()
                    cluster_stats.columns = ['Cluster', 'Avg Recency (Days)', 'Avg Frequency (Orders)', 'Avg Monetary ($)', 'Customer Count']
                    cluster_stats['Avg Monetary ($)'] = cluster_stats['Avg Monetary ($)'].round(0)
                    cluster_stats['Avg Recency (Days)'] = cluster_stats['Avg Recency (Days)'].round(0)
                    cluster_stats['Avg Frequency (Orders)'] = cluster_stats['Avg Frequency (Orders)'].round(1)
                    
                    st.markdown("##### Cluster Profiling Table")
                    st.dataframe(cluster_stats, use_container_width=True)
                    
                with col_c2:
                    fig_3d = px.scatter_3d(
                        rfm, 
                        x='Recency', 
                        y='Frequency', 
                        z='Monetary', 
                        color='Cluster', 
                        log_y=True, 
                        log_z=True, 
                        color_continuous_scale='Turbo',
                        title='3D Customer Segments (RFM Visualizer)',
                        hover_name='Customer Name',
                        opacity=0.8
                    )
                    fig_3d.update_layout(height=500)
                    st.plotly_chart(fig_3d, use_container_width=True)
                    
                st.markdown("##### Segmented Customers List")
                st.dataframe(rfm.sort_values('Monetary', ascending=False), use_container_width=True)
                
        with tab_cohort:
            st.markdown("#### Customer Retention Cohorts")
            st.markdown("Tracks the monthly retention rate of customer cohorts based on their first purchase month.")
            
            retention_matrix = calculate_cohort_retention(filtered_df)
            if retention_matrix is not None:
                fig_heat = px.imshow(
                    retention_matrix, 
                    text_auto=".1f", 
                    color_continuous_scale='Blues',
                    labels=dict(x="Months Active", y="Acquisition Cohort", color="Retention %"),
                    title="Cohort Retention Grid (in %)"
                )
                fig_heat.update_xaxes(side="top")
                fig_heat.update_layout(height=500)
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.warning("Not enough data to calculate monthly customer retention cohorts.")

    # ==========================================
    # TAB 4: MARKET BASKET ANALYSIS
    # ==========================================
    with tab_basket:
        st.subheader("🛒 Market Basket Analysis & Product Cross-Sells")
        st.markdown("Identify products that are frequently purchased together using the **Apriori Association Rule Mining** algorithm.")
        
        num_transactions = filtered_df['Order ID'].nunique()
        if num_transactions < 10:
            st.warning("Not enough transaction data to compute association rules.")
        else:
            group_choice = st.radio(
                "Choose Association Analysis Level:",
                ["Customer-level (Purchase History) - RECOMMENDED", "Order-level (Single Order)"],
                index=0,
                horizontal=True
            )
            group_by_col = 'Customer Name' if "Customer-level" in group_choice else 'Order ID'
            
            @st.cache_data
            def get_association_rules(df_input, group_by_col):
                top_prods_list = df_input['Product Name'].value_counts()
                top_prods_list = top_prods_list[top_prods_list >= 3].index
                df_dense = df_input[df_input['Product Name'].isin(top_prods_list)]
                
                if df_dense[group_by_col].nunique() < 5:
                    return pd.DataFrame()
                    
                basket = (df_dense.groupby([group_by_col, 'Product Name'])['Quantity']
                          .sum().unstack().reset_index().fillna(0)
                          .set_index(group_by_col))
                
                basket_sets = basket.apply(lambda x: x.map(lambda v: v > 0))
                
                from mlxtend.frequent_patterns import apriori, association_rules
                min_sup = 0.008 if group_by_col == 'Customer Name' else 0.003
                frequent_itemsets = apriori(basket_sets, min_support=min_sup, use_colnames=True)
                if len(frequent_itemsets) == 0:
                    return pd.DataFrame()
                    
                rules_df = association_rules(frequent_itemsets, metric="lift", min_threshold=0.8)
                return rules_df

            rules = get_association_rules(filtered_df, group_by_col)
            
            if rules.empty:
                if group_by_col == 'Order ID':
                    st.info("ℹ️ Note: Order-level association rules are empty because each order in this dataset contains exactly one product. Switch to Customer-level to find products bought by the same customer over time.")
                else:
                    st.info("No strong association rules found. Try clearing filters to increase data volume.")
            else:
                rules['antecedent_names'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
                rules['consequent_names'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
                
                col_b1, col_b2 = st.columns([1, 2])
                with col_b1:
                    st.markdown("#### Recommend Cross-Sells")
                    all_antecedents = sorted(list(set([name for sublist in rules['antecedents'] for name in sublist])))
                    selected_product = st.selectbox("Select a Product:", all_antecedents)
                    
                    product_rules = rules[rules['antecedents'].apply(lambda x: selected_product in x)]
                    product_rules = product_rules.sort_values('lift', ascending=False).head(5)
                    
                    if product_rules.empty:
                        st.info("No recommendations found for this product.")
                    else:
                        st.markdown(f"**Recommended products to place near *{selected_product}*:**")
                        for idx, row in product_rules.iterrows():
                            st.success(f"🛒 **{row['consequent_names']}** (Lift: {row['lift']:.2f}, Confidence: {row['confidence']:.1%})")
                            
                with col_b2:
                    st.markdown("#### All Association Rules")
                    st.markdown("Sorted by **Lift** (the ratio of the probability of buying product B when product A is bought, to the probability of buying B independently).")
                    display_rules = rules[['antecedent_names', 'consequent_names', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False)
                    st.dataframe(display_rules.style.format({'support': '{:.3f}', 'confidence': '{:.2%}', 'lift': '{:.2f}'}), use_container_width=True)


    # ==========================================
    # TAB 5: CHURN PREDICTION
    # ==========================================
    with tab_churn:
        st.subheader("⚠️ Customer Churn Prediction")
        st.markdown("Predict which customers are likely to stop purchasing using **XGBoost** and **Random Forest** classifiers with feature importance analysis.")
        
        # Build customer-level features
        max_date = filtered_df['Order Date'].max()
        churn_df = filtered_df.groupby('Customer Name').agg(
            Last_Purchase=('Order Date', 'max'),
            Total_Orders=('Order ID', 'nunique'),
            Total_Spend=('Sales Amount', 'sum'),
            Avg_Order_Value=('Sales Amount', 'mean'),
            Total_Quantity=('Quantity', 'sum'),
            Avg_Discount=('Discount', 'mean'),
            Unique_Products=('Product Name', 'nunique'),
            Days_Active=('Order Date', lambda x: (x.max() - x.min()).days),
        ).reset_index()
        
        churn_df['Recency_Days'] = (max_date - churn_df['Last_Purchase']).dt.days
        churn_df['Avg_Profit'] = filtered_df.groupby('Customer Name')['Profit'].mean().values
        churn_df['Order_Frequency'] = churn_df['Total_Orders'] / (churn_df['Days_Active'].clip(lower=1) / 30)
        
        # Define churn: customers with no purchase in last 90 days
        churn_threshold = 90
        churn_df['Is_Churned'] = (churn_df['Recency_Days'] > churn_threshold).astype(int)
        
        churn_rate = churn_df['Is_Churned'].mean() * 100
        st.metric("Overall Churn Rate", f"{churn_rate:.1f}%", help=f"Customers with no purchase in last {churn_threshold} days")
        
        col_ch1, col_ch2 = st.columns([1, 2])
        
        with col_ch1:
            st.markdown("#### Model Configuration")
            churn_model_choice = st.selectbox("Select Model", ["XGBoost", "Random Forest", "Both"])
            test_size = st.slider("Test Size (%)", min_value=15, max_value=35, value=25)
            
            st.markdown("#### Churn Definition")
            st.info(f"Customers with no purchase in the last **{churn_threshold}** days are labeled as churned.")
            st.metric("Total Customers", f"{len(churn_df):,}")
            st.metric("Churned", f"{churn_df['Is_Churned'].sum():,}")
            st.metric("Active", f"{(churn_df['Is_Churned'] == 0).sum():,}")
        
        with col_ch2:
            if len(churn_df) < 20:
                st.warning("Not enough customers for churn prediction.")
            else:
                with st.spinner("Training churn prediction models (XGBoost, Random Forest)..."):
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
                    from sklearn.preprocessing import StandardScaler
                    
                    feature_cols = ['Recency_Days', 'Total_Orders', 'Total_Spend', 'Avg_Order_Value',
                                    'Total_Quantity', 'Avg_Discount', 'Unique_Products', 'Days_Active',
                                    'Avg_Profit', 'Order_Frequency']
                    
                    X = churn_df[feature_cols].fillna(0)
                    y = churn_df['Is_Churned']
                    
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size/100, random_state=42, stratify=y if y.nunique() > 1 else None)
                    
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    results = {}
                    
                    if churn_model_choice in ["XGBoost", "Both"]:
                        from xgboost import XGBClassifier
                        xgb_churn = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42, eval_metric='logloss', verbosity=0)
                        xgb_churn.fit(X_train_scaled, y_train)
                        xgb_pred = xgb_churn.predict(X_test_scaled)
                        xgb_prob = xgb_churn.predict_proba(X_test_scaled)[:, 1]
                        results['XGBoost'] = {'model': xgb_churn, 'pred': xgb_pred, 'prob': xgb_prob, 'importances': xgb_churn.feature_importances_}
                    
                    if churn_model_choice in ["Random Forest", "Both"]:
                        from sklearn.ensemble import RandomForestClassifier
                        rf_churn = RandomForestClassifier(n_estimators=100, random_state=42)
                        rf_churn.fit(X_train_scaled, y_train)
                        rf_pred = rf_churn.predict(X_test_scaled)
                        rf_prob = rf_churn.predict_proba(X_test_scaled)[:, 1]
                        results['Random Forest'] = {'model': rf_churn, 'pred': rf_pred, 'prob': rf_prob, 'importances': rf_churn.feature_importances_}
                
                # Display results (outside spinner)
                
                # Display results
                for model_name, res in results.items():
                    st.markdown(f"#### {model_name} Results")
                    auc = roc_auc_score(y_test, res['prob']) if len(set(y_test)) > 1 else 0
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("AUC-ROC", f"{auc:.3f}")
                        report = classification_report(y_test, res['pred'], output_dict=True)
                        st.metric("Accuracy", f"{report['accuracy']:.1%}")
                        st.metric("Precision (Churned)", f"{report.get('1', {}).get('precision', 0):.1%}")
                    with c2:
                        st.metric("Recall (Churned)", f"{report.get('1', {}).get('recall', 0):.1%}")
                        st.metric("F1-Score (Churned)", f"{report.get('1', {}).get('f1-score', 0):.1%}")
                    
                    # Feature importance chart
                    feat_imp = pd.DataFrame({
                        'Feature': feature_cols,
                        'Importance': res['importances']
                    }).sort_values('Importance', ascending=True)
                    
                    fig_imp = px.bar(feat_imp, x='Importance', y='Feature', orientation='h',
                                    title=f'{model_name} Feature Importance',
                                    color='Importance', color_continuous_scale='Blues')
                    fig_imp.update_layout(height=350)
                    st.plotly_chart(fig_imp, use_container_width=True)
                
                # Confusion matrix for best model
                if results:
                    best_name = list(results.keys())[0]
                    cm = confusion_matrix(y_test, results[best_name]['pred'])
                    fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                                       labels=dict(x="Predicted", y="Actual", color="Count"),
                                       title=f"Confusion Matrix ({best_name})")
                    fig_cm.update_layout(height=300)
                    st.plotly_chart(fig_cm, use_container_width=True)
                    
                    # Risk scores
                    st.markdown("#### Customer Risk Scores")
                    churn_df['Churn_Risk'] = results[best_name]['model'].predict_proba(scaler.transform(churn_df[feature_cols].fillna(0)))[:, 1]
                    risk_df = churn_df[['Customer Name', 'Total_Spend', 'Total_Orders', 'Recency_Days', 'Churn_Risk']].copy()
                    risk_df['Risk_Level'] = pd.cut(risk_df['Churn_Risk'], bins=[0, 0.3, 0.6, 1.0], labels=['Low', 'Medium', 'High'])
                    risk_df = risk_df.sort_values('Churn_Risk', ascending=False)
                    
                    def color_risk(val):
                        if val == 'High': return 'background-color: #ffcccc'
                        elif val == 'Medium': return 'background-color: #fff3cd'
                        return 'background-color: #d4edda'
                    
                    st.dataframe(risk_df.style.format({'Total_Spend': '${:,.0f}', 'Churn_Risk': '{:.1%}'}).map(color_risk, subset=['Risk_Level']), use_container_width=True)


    # ==========================================
    # TAB 6: WHAT-IF SIMULATOR
    # ==========================================
    with tab_simulator:
        st.subheader("🎛️ Strategic What-If Simulator")
        st.markdown("Simulate how adjustments to **Sales Price**, **Order Volume**, and **Discounts** affect overall revenue, costs, and profit using managerial accounting metrics.")
        
        base_sales = filtered_df['Sales Amount'].sum()
        base_profit = filtered_df['Profit'].sum()
        base_cost = base_sales - base_profit
        
        # Managerial cost structures: 30% fixed, 70% variable
        base_fixed_cost = base_cost * 0.30
        base_var_cost = base_cost * 0.70
        base_avg_discount = filtered_df['Discount'].mean()
        
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.markdown("#### Simulation Controls")
            price_change = st.slider("Price Adjustment % (Price markup/markdown)", min_value=-20.0, max_value=20.0, value=0.0, step=0.5)
            volume_change = st.slider("Volume (Quantity) Change %", min_value=-30.0, max_value=50.0, value=0.0, step=1.0)
            discount_change = st.slider("Average Discount Adjustment % (Absolute change)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5)
            
            # Simulated Outcomes
            p_factor = 1.0 + (price_change / 100.0)
            v_factor = 1.0 + (volume_change / 100.0)
            
            denom = (1.0 - base_avg_discount)
            if denom == 0:
                denom = 0.001
            disc_factor = (1.0 - (base_avg_discount + (discount_change / 100.0))) / denom
            disc_factor = max(0.0, disc_factor)
            
            sim_sales = base_sales * p_factor * v_factor * disc_factor
            sim_var_cost = base_var_cost * v_factor
            sim_fixed_cost = base_fixed_cost
            sim_cost = sim_var_cost + sim_fixed_cost
            sim_profit = sim_sales - sim_cost
            
            sales_diff = sim_sales - base_sales
            profit_diff = sim_profit - base_profit
            cost_diff = sim_cost - base_cost
            
        with col_s2:
            st.markdown("#### Simulation Results")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Simulated Revenue", f"${sim_sales:,.0f}", f"${sales_diff:+,.0f}", delta_color="normal")
            m2.metric("Simulated Cost", f"${sim_cost:,.0f}", f"${cost_diff:+,.0f}", delta_color="inverse")
            m3.metric("Simulated Profit", f"${sim_profit:,.0f}", f"${profit_diff:+,.0f}", delta_color="normal")
            
            st.divider()
            
            # Plot comparisons
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                name='Actual Baseline',
                x=['Revenue', 'Cost', 'Profit'],
                y=[base_sales, base_cost, base_profit],
                marker_color='#34495e'
            ))
            fig_sim.add_trace(go.Bar(
                name='Simulated Scenario',
                x=['Revenue', 'Cost', 'Profit'],
                y=[sim_sales, sim_cost, sim_profit],
                marker_color='#2980b9'
            ))
            fig_sim.update_layout(
                barmode='group',
                title="Scenario Comparison: Baseline vs Simulated",
                yaxis_title="Amount ($)",
                height=350
            )
            st.plotly_chart(fig_sim, use_container_width=True)

    # ==========================================
    # TAB 7: SQL WORKSPACE
    # ==========================================
    with tab_sql:
        st.subheader("🗄️ SQL Analytics Workspace")
        st.markdown("Write and run raw SQL queries directly against the local SQLite database containing all sales records.")
        
        if not os.path.exists('sales.db'):
            st.error("SQLite database 'sales.db' not found. Please load the Local SQLite database at the top.")
        else:
            col_sql1, col_sql2 = st.columns([2, 1])
            
            with col_sql2:
                with st.expander("Table Schema Helper", expanded=False):
                    st.markdown("**Table Name**: `sales`")
                    st.markdown("""
                    *   `Order_ID` (TEXT)
                    *   `Order_Date` (TEXT)
                    *   `Customer_Name` (TEXT)
                    *   `Region` (TEXT)
                    *   `Product_Category` (TEXT)
                    *   `Product_Name` (TEXT)
                    *   `Sales_Amount` (REAL)
                    *   `Quantity` (INTEGER)
                    *   `Profit` (REAL)
                    *   `Discount` (REAL)
                    *   `Payment_Mode` (TEXT)
                    *   `Month` (INTEGER)
                    *   `Year` (INTEGER)
                    """)
                    st.divider()
                    st.info("Write standard SQLite queries. Column names use underscores (e.g., `Sales_Amount` not `Sales Amount`).")
                
            with col_sql1:
                st.markdown("##### 📝 Query Editor")
                
                query_templates = {
                    "Sales by Region": "SELECT Region, ROUND(SUM(Sales_Amount), 2) AS Total_Sales, COUNT(*) AS Order_Count FROM sales GROUP BY Region ORDER BY Total_Sales DESC;",
                    "Top 5 Customers": "SELECT Customer_Name, ROUND(SUM(Sales_Amount), 2) AS Total_Revenue, COUNT(DISTINCT Order_ID) AS Orders FROM sales GROUP BY Customer_Name ORDER BY Total_Revenue DESC LIMIT 5;",
                    "Monthly Sales": "SELECT Year, Month, ROUND(SUM(Sales_Amount), 2) AS Monthly_Sales FROM sales GROUP BY Year, Month ORDER BY Year DESC, Month DESC;",
                    "Most Profitable Items": "SELECT Product_Name, Product_Category, ROUND(SUM(Profit), 2) AS Total_Profit FROM sales GROUP BY Product_Name ORDER BY Total_Profit DESC LIMIT 10;"
                }
                
                if 'sql_query_input' not in st.session_state:
                    st.session_state['sql_query_input'] = query_templates["Sales by Region"]
                    
                st.markdown("**Templates (Click to load):**")
                cols_tmp = st.columns(len(query_templates))
                for idx, (name, query) in enumerate(query_templates.items()):
                    if cols_tmp[idx].button(name):
                        st.session_state['sql_query_input'] = query
                        
                query_input = st.text_area("Write SQL Query:", key="sql_query_input", height=180)
                
                if st.button("🚀 Run Query", type="primary"):
                    try:
                        conn = sqlite3.connect('sales.db')
                        query_result = pd.read_sql_query(query_input, conn)
                        conn.close()
                        
                        st.success("Executed successfully!")
                        st.metric("Rows Returned", len(query_result))
                        st.dataframe(query_result, use_container_width=True)
                        
                        csv_results = query_result.to_csv(index=False).encode('utf-8')
                        st.download_button("💾 Download Query Results (CSV)", csv_results, "sql_results.csv", "text/csv")
                    except Exception as e:
                        st.error(f"SQL Error: {e}")

else:
    st.info("👆 Please ensure a data source is selected above to load the analytical views.")

# Footer
st.divider()
st.caption("Built with Streamlit + Plotly + Scikit-Learn | Run: `streamlit run app.py`")
