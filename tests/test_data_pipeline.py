"""Tests for data cleaning pipeline."""
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataCleaning:
    """Test suite for clean_sales_data.py"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load cleaned dataset for tests."""
        self.csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dataset", "cleaned_sales_dataset.csv"
        )
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            self.df['Order Date'] = pd.to_datetime(self.df['Order Date'], errors='coerce')
        else:
            pytest.skip("Cleaned dataset not found. Run clean_sales_data.py first.")

    def test_dataset_not_empty(self):
        """Cleaned dataset should have rows."""
        assert len(self.df) > 0, "Cleaned dataset is empty"

    def test_no_duplicate_order_ids(self):
        """No duplicate rows for same Order ID + Product Name (multi-product orders allowed)."""
        dupes = self.df.duplicated(subset=['Order ID', 'Product Name'], keep='first')
        assert not dupes.any(), f"Found {dupes.sum()} duplicate Order+Product rows"

    def test_no_critical_missing_values(self):
        """Critical columns should have no missing values."""
        critical_cols = ['Order ID', 'Order Date', 'Region', 'Sales Amount', 'Quantity']
        for col in critical_cols:
            assert self.df[col].isna().sum() == 0, f"Missing values in critical column: {col}"

    def test_sales_amount_positive(self):
        """Sales Amount should be positive."""
        assert (self.df['Sales Amount'] >= 0).all(), "Negative sales amounts found"

    def test_quantity_positive(self):
        """Quantity should be positive."""
        assert (self.df['Quantity'] > 0).all(), "Non-positive quantities found"

    def test_date_range_valid(self):
        """Order dates should be within expected range."""
        assert self.df['Order Date'].min().year >= 2021, "Dates before 2021 found"
        assert self.df['Order Date'].max().year <= 2024, "Dates after 2024 found"

    def test_month_year_columns_exist(self):
        """Month and Year columns should be present."""
        assert 'Month' in self.df.columns, "Month column missing"
        assert 'Year' in self.df.columns, "Year column missing"

    def test_month_values_valid(self):
        """Month values should be 1-12."""
        assert self.df['Month'].between(1, 12).all(), "Invalid month values"

    def test_has_expected_columns(self):
        """Dataset should have all expected columns."""
        expected = ['Order ID', 'Order Date', 'Customer Name', 'Region',
                    'Product Category', 'Product Name', 'Sales Amount',
                    'Quantity', 'Profit', 'Discount', 'Payment Mode',
                    'Month', 'Year']
        for col in expected:
            assert col in self.df.columns, f"Missing column: {col}"


class TestDataEnrichment:
    """Test suite for enrich_sales_data.py"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load enriched dataset for tests."""
        self.csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "dataset", "enriched_sales_dataset.csv"
        )
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
        else:
            pytest.skip("Enriched dataset not found. Run enrich_sales_data.py first.")

    def test_enriched_dataset_not_empty(self):
        """Enriched dataset should have rows."""
        assert len(self.df) > 0, "Enriched dataset is empty"

    def test_enrichment_columns_added(self):
        """Enrichment should add expected new columns."""
        expected_new = ['Quarter', 'Is_Weekend', 'Season', 'Day_of_Week',
                        'Unit_Price', 'Discount_Amount', 'Profit_Margin_Pct',
                        'AOV_Segment', 'Customer_LTV', 'Customer_Frequency',
                        'Is_Repeat_Customer', 'Customer_Tier']
        for col in expected_new:
            assert col in self.df.columns, f"Enrichment column missing: {col}"

    def test_profit_margin_range(self):
        """Profit margin should be reasonable (allowing for high-margin products)."""
        valid = self.df['Profit_Margin_Pct'].dropna()
        assert valid.min() >= -100, "Profit margin below -100%"
        assert valid.max() <= 500, "Profit margin unreasonably high"

    def test_customer_tier_values(self):
        """Customer tier should have valid categories."""
        valid_tiers = {'Bronze', 'Silver', 'Gold'}
        actual_tiers = set(self.df['Customer_Tier'].dropna().unique())
        assert actual_tiers.issubset(valid_tiers), f"Invalid tiers: {actual_tiers - valid_tiers}"

    def test_aov_segment_values(self):
        """AOV segment should have valid categories."""
        valid_segments = {'Low-Value', 'Medium-Value', 'High-Value'}
        actual = set(self.df['AOV_Segment'].dropna().unique())
        assert actual.issubset(valid_segments), f"Invalid segments: {actual - valid_segments}"

    def test_is_weekend_binary(self):
        """Is_Weekend should be 0 or 1."""
        assert self.df['Is_Weekend'].isin([0, 1]).all(), "Is_Weekend has non-binary values"

    def test_is_repeat_customer_binary(self):
        """Is_Repeat_Customer should be 0 or 1."""
        assert self.df['Is_Repeat_Customer'].isin([0, 1]).all(), "Is_Repeat_Customer has non-binary values"
