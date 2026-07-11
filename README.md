# Sales & Customer Intelligence Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-26%20passed-brightgreen.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade analytics dashboard with **Machine Learning**, **Time-Series Forecasting**, **Customer Segmentation**, **Churn Prediction**, **Market Basket Analysis**, and **Interactive SQL**.

> **Live Demo**: Deploy to [Streamlit Cloud](#deployment) and get a shareable link for your resume.

---

## Features

| Module | What It Does | Tech |
|--------|-------------|------|
| **Executive Dashboard** | KPIs, regional breakdown, trends, top products, PDF export | Plotly, Streamlit, FPDF2 |
| **Time-Series Forecasting** | 4 models with cross-validation: Prophet, Random Forest, XGBoost, LightGBM | scikit-learn, Prophet, XGBoost, LightGBM |
| **Customer Intelligence** | RFM clustering with elbow method + silhouette score, cohort retention heatmap | K-Means, Plotly |
| **Market Basket Analysis** | Apriori association rules, cross-sell recommendations (customer-level + order-level) | mlxtend |
| **Churn Prediction** | XGBoost + Random Forest classifiers with AUC-ROC, feature importance, risk scores | XGBoost, scikit-learn |
| **What-If Simulator** | Pricing/volume/discount scenario planning with fixed/variable cost modeling | Custom logic |
| **SQL Workspace** | Raw SQL queries against SQLite database with template queries | SQLite |

---

## Quick Start

### Option 1: One-Click Setup (Windows)

Double-click `setup.bat` — it handles everything automatically.

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/sales-intelligence-platform.git
cd sales-intelligence-platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Generate realistic dataset
python generate_dataset.py

# Run data pipeline
python clean_sales_data.py
python enrich_sales_data.py
python load_db.py

# Launch dashboard
streamlit run app.py
```

### Option 3: Docker

```bash
docker-compose up --build
```

Open **http://localhost:8501**

---

## Project Structure

```
sales-intelligence-platform/
├── app.py                    # Main Streamlit dashboard (1,100+ lines, 7 tabs)
├── clean_sales_data.py       # Data cleaning pipeline
├── enrich_sales_data.py      # Feature engineering (14 new features)
├── load_db.py                # SQLite database loader
├── generate_dataset.py       # Realistic multi-product dataset generator
├── requirements.txt          # Pinned dependencies (13 packages)
├── pyproject.toml            # Modern Python project config
├── Dockerfile                # Container definition (full pipeline)
├── docker-compose.yml        # Multi-container orchestration
├── Makefile                  # Convenience commands (run, test, lint, etc.)
├── setup.bat                 # Windows one-click setup
├── LICENSE                   # MIT License
├── .gitignore                # Git exclusions
├── .streamlit/               # Streamlit deployment config
│   └── config.toml
├── .github/workflows/        # GitHub Actions CI
│   └── ci.yml
├── tests/                    # pytest test suite (26 tests)
│   ├── test_data_pipeline.py
│   └── test_database_and_ml.py
├── dataset/                  # Generated data files
│   └── sales_dataset_5500.csv
└── sales.db                  # SQLite database
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

**Test Coverage**: Data pipeline validation, database integrity, ML model correctness.

---

## Tech Stack

- **Frontend**: Streamlit 1.56, Plotly 6.7
- **ML/AI**: scikit-learn 1.8 (K-Means, RandomForest, XGBoost, LightGBM), Prophet 1.3
- **Association Mining**: mlxtend 0.25 (Apriori)
- **Database**: SQLite3
- **Data**: Pandas 3.0, NumPy 2.4
- **Infrastructure**: Docker, Docker Compose, GitHub Actions

---

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" → select your repo, `app.py` as main file
5. Click "Deploy"

Your live URL will look like: `https://yourname-sales-platform.streamlit.app`

Add this URL to your resume and LinkedIn.

---

## Dataset

This project generates a **realistic multi-product retail sales dataset** with:

- **2,500 orders** with **5,400+ line items** (avg 2.2 products per order)
- **5 product categories**: Electronics, Furniture, Clothing, Sports, Home & Kitchen
- **4 regions**: East, West, Central, South
- **2,000+ customers** with realistic names
- **2021-2024** date range with seasonal patterns
- **14 engineered features**: profit margin, customer LTV, season, AOV segments, etc.

The `generate_dataset.py` script creates deterministic, reproducible data with realistic distributions and intentional missing values (~2%) for testing data cleaning pipelines.

---

## Key Algorithms

### K-Means RFM Clustering
Customers are segmented by Recency, Frequency, and Monetary value using log-transformed, standardized features. Includes elbow method and silhouette score for optimal K selection.

### Time-Series Forecasting (4 Models)
- **Prophet**: Statistical additive seasonality with confidence intervals
- **Random Forest**: ML-based recursive autoregression with lag features
- **XGBoost**: Gradient boosting with cross-validation
- **LightGBM**: Light gradient boosting with cross-validation

### Churn Prediction
XGBoost and Random Forest classifiers predict customer churn risk with AUC-ROC scoring, feature importance analysis, and customer risk level segmentation.

### Apriori Association Rules
Market basket analysis using support, confidence, and lift metrics to identify cross-sell opportunities at both customer-level and order-level.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
