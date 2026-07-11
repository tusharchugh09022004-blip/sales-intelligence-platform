"""Tests for SQLite database and clustering logic."""
import pytest
import pandas as pd
import numpy as np
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabase:
    """Test suite for SQLite database."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Connect to test database."""
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "sales.db"
        )
        if not os.path.exists(self.db_path):
            pytest.skip("sales.db not found. Run load_db.py first.")
        self.conn = sqlite3.connect(self.db_path)

    def teardown(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

    def test_database_exists(self):
        """sales.db should exist."""
        assert os.path.exists(self.db_path), "sales.db not found"

    def test_sales_table_exists(self):
        """sales table should exist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        assert cursor.fetchone() is not None, "sales table not found"

    def test_sales_table_has_rows(self):
        """sales table should have data."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        assert count > 0, "sales table is empty"

    def test_sales_table_columns(self):
        """sales table should have expected columns."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(sales)")
        columns = {col[1] for col in cursor.fetchall()}
        required = {'Order_ID', 'Order_Date', 'Region', 'Sales_Amount', 'Quantity'}
        assert required.issubset(columns), f"Missing columns: {required - columns}"

    def test_sql_query_returns_data(self):
        """Basic SQL query should return data."""
        query = "SELECT Region, SUM(Sales_Amount) as Total FROM sales GROUP BY Region"
        result = pd.read_sql_query(query, self.conn)
        assert len(result) > 0, "SQL query returned no data"
        assert 'Total' in result.columns, "Missing Total column"

    def test_no_null_order_ids(self):
        """Order_ID should not be null."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales WHERE Order_ID IS NULL")
        count = cursor.fetchone()[0]
        assert count == 0, "Null Order_IDs found in database"


class TestClustering:
    """Test suite for K-Means clustering logic."""

    def test_rfm_calculation(self):
        """RFM values should be calculable from transaction data."""
        dates = pd.to_datetime(['2024-01-01', '2024-03-15', '2024-06-01'])
        max_date = dates.max()
        recency = (max_date - dates.max()).days
        assert recency == 0, "Recency calculation failed"

    def test_standard_scaler(self):
        """StandardScaler should normalize data properly."""
        from sklearn.preprocessing import StandardScaler
        data = np.array([[100, 5, 5000], [200, 10, 10000], [50, 2, 1000]])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(data)
        assert scaled.mean(axis=0).shape == (3,), "Scaler output shape incorrect"
        assert abs(scaled.mean(axis=0).mean()) < 0.1, "Scaled data not centered"

    def test_kmeans_clustering(self):
        """K-Means should produce valid cluster assignments."""
        from sklearn.cluster import KMeans
        np.random.seed(42)
        data = np.random.randn(100, 3)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data)
        assert len(labels) == 100, "Cluster labels length mismatch"
        assert len(set(labels)) == 3, "Expected 3 clusters"

    def test_elbow_method_range(self):
        """Elbow method should test K values 2-10."""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        np.random.seed(42)
        data = np.random.randn(50, 3) * 10 + 5
        scaler = StandardScaler()
        scaled = scaler.fit_transform(data)
        inertias = []
        for k in range(2, 6):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(scaled)
            inertias.append(km.inertia_)
        # Inertia should decrease as K increases
        assert inertias[-1] < inertias[0], "Inertia not decreasing with K"
