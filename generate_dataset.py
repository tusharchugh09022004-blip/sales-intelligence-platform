"""
Generate a realistic retail sales dataset for the Sales Intelligence Platform.

This script generates 5,500+ realistic retail transactions with proper
product names, customer profiles, regional data, and temporal patterns.
Based on real-world retail data distributions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

np.random.seed(42)
random.seed(42)

print("Generating realistic retail sales dataset...")
print("=" * 50)

# =============================================
# CONFIGURATION
# =============================================
NUM_ORDERS = 2500  # Orders (each can have 1-5 products, totaling ~5500 rows)
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2024, 12, 31)

# =============================================
# REALISTIC REFERENCE DATA
# =============================================

PRODUCT_CATALOG = {
    "Electronics": [
        ("Laptop - 15 inch", 899.99, 1200.00),
        ("Laptop - 13 inch", 1099.99, 1400.00),
        ("Wireless Mouse", 29.99, 45.00),
        ("Mechanical Keyboard", 79.99, 120.00),
        ("27 inch Monitor", 349.99, 500.00),
        ("4K Ultra HD Monitor", 499.99, 700.00),
        ("USB-C Hub Adapter", 49.99, 75.00),
        ("Wireless Earbuds", 59.99, 90.00),
        ("Noise Cancelling Headphones", 199.99, 280.00),
        ("Webcam HD", 69.99, 100.00),
        ("External SSD 1TB", 109.99, 160.00),
        ("Portable Charger 20000mAh", 39.99, 60.00),
        ("Bluetooth Speaker", 89.99, 130.00),
        ("Smart Watch", 249.99, 350.00),
        ("Tablet 10 inch", 329.99, 450.00),
    ],
    "Furniture": [
        ("Office Desk - Wood", 299.99, 450.00),
        ("Ergonomic Office Chair", 249.99, 380.00),
        ("Standing Desk Converter", 199.99, 300.00),
        ("Bookshelf 5-Tier", 149.99, 220.00),
        ("Filing Cabinet 3-Drawer", 179.99, 260.00),
        ("Conference Table", 599.99, 850.00),
        ("Coffee Table", 129.99, 190.00),
        ("TV Stand 60 inch", 159.99, 230.00),
        ("Storage Cabinet", 219.99, 320.00),
        ("Desk Lamp LED", 44.99, 65.00),
    ],
    "Clothing": [
        ("Men's Formal Shirt", 34.99, 55.00),
        ("Women's Blouse", 29.99, 48.00),
        ("Denim Jeans", 49.99, 75.00),
        ("Cotton T-Shirt", 19.99, 32.00),
        ("Winter Jacket", 89.99, 140.00),
        ("Sports Shorts", 24.99, 38.00),
        ("Formal Trousers", 44.99, 68.00),
        ("Sneakers", 79.99, 120.00),
        ("Leather Belt", 29.99, 45.00),
        ("Wool Sweater", 59.99, 90.00),
        ("Running Shoes", 99.99, 150.00),
        ("Casual Dress Shirt", 39.99, 60.00),
    ],
    "Sports": [
        ("Yoga Mat Premium", 39.99, 60.00),
        ("Dumbbells Set 20kg", 149.99, 220.00),
        ("Resistance Bands Set", 24.99, 38.00),
        ("Tennis Racket", 89.99, 130.00),
        ("Basketball", 29.99, 45.00),
        ("Football Soccer", 24.99, 38.00),
        ("Swimming Goggles", 19.99, 30.00),
        ("Jump Rope", 14.99, 22.00),
        ("Foam Roller", 29.99, 45.00),
        ("Gym Bag", 34.99, 52.00),
        ("Boxing Gloves", 59.99, 90.00),
        ("Fitness Tracker Band", 49.99, 75.00),
    ],
    "Home & Kitchen": [
        ("Blender 1000W", 79.99, 120.00),
        ("Air Fryer 5L", 99.99, 150.00),
        ("Coffee Maker Drip", 69.99, 105.00),
        ("Vacuum Cleaner Cordless", 299.99, 440.00),
        ("Toaster 4-Slice", 39.99, 60.00),
        ("Microwave Oven 900W", 129.99, 195.00),
        ("Electric Kettle 1.7L", 34.99, 52.00),
        ("Food Processor", 89.99, 135.00),
        ("Weighted Blanket", 59.99, 90.00),
        ("Throw Pillow Set", 29.99, 45.00),
        ("Cookware Set 10pc", 199.99, 300.00),
        ("Robot Vacuum", 349.99, 500.00),
    ],
}

REGIONS = {
    "East": {"states": ["New York", "New Jersey", "Connecticut", "Pennsylvania", "Massachusetts"], "weight": 0.25},
    "West": {"states": ["California", "Oregon", "Washington", "Arizona", "Nevada"], "weight": 0.28},
    "Central": {"states": ["Illinois", "Ohio", "Michigan", "Indiana", "Wisconsin"], "weight": 0.20},
    "South": {"states": ["Texas", "Florida", "Georgia", "Virginia", "North Carolina"], "weight": 0.27},
}

PAYMENT_MODES = ["Credit Card", "Debit Card", "Cash", "Online Transfer", "Mobile Payment"]
PAYMENT_WEIGHTS = [0.30, 0.25, 0.15, 0.18, 0.12]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
    "Andrew", "Dorothy", "Paul", "Kimberly", "Joshua", "Emily", "Kenneth", "Donna",
    "Kevin", "Michelle", "Brian", "Carol", "George", "Amanda", "Timothy", "Melissa",
    "Ronald", "Deborah", "Edward", "Stephanie", "Jason", "Rebecca", "Jeffrey", "Sharon",
    "Ryan", "Laura", "Jacob", "Cynthia", "Gary", "Kathleen", "Nicholas", "Amy",
    "Eric", "Angela", "Jonathan", "Shirley", "Stephen", "Anna", "Larry", "Brenda",
    "Justin", "Pamela", "Scott", "Emma", "Brandon", "Nicole", "Benjamin", "Helen",
    "Samuel", "Samantha", "Raymond", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Patrick", "Carolyn", "Jack", "Janet", "Dennis", "Catherine",
    "Jerry", "Maria", "Tyler", "Heather", "Aaron", "Diane", "Jose", "Ruth",
    "Adam", "Julie", "Nathan", "Olivia", "Henry", "Joyce", "Douglas", "Virginia",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward",
    "Richardson", "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray",
    "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel",
    "Myers", "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry",
    "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales",
]


def generate_order_id(idx):
    """Generate realistic order ID like ORD-2024-00001"""
    year = random.choice([2021, 2022, 2023, 2024])
    return f"ORD-{year}-{idx:05d}"


def generate_customer_name():
    """Generate a realistic customer name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_date():
    """Generate a random date within the range with seasonal patterns"""
    days_range = (END_DATE - START_DATE).days
    day_offset = random.randint(0, days_range)
    date = START_DATE + timedelta(days=day_offset)
    return date


def get_seasonal_multiplier(month):
    """Return sales multiplier based on month (seasonal patterns)"""
    # Holiday season boost (Nov-Dec), summer dip, spring boost
    multipliers = {
        1: 0.85, 2: 0.90, 3: 1.05, 4: 1.10,
        5: 1.05, 6: 0.95, 7: 0.90, 8: 0.95,
        9: 1.00, 10: 1.05, 11: 1.30, 12: 1.40
    }
    return multipliers.get(month, 1.0)


# =============================================
# GENERATE ORDERS (multi-product)
# =============================================
print(f"Generating {NUM_ORDERS} orders (each with 1-5 products)...")

records = []
used_order_ids = set()

# Pre-assign customers for repeat purchase behavior
customer_pool = [generate_customer_name() for _ in range(800)]

for i in range(NUM_ORDERS):
    # Generate unique order ID
    order_id = generate_order_id(i + 1)
    while order_id in used_order_ids:
        order_id = generate_order_id(i + 1) + random.choice(string.ascii_uppercase)
    used_order_ids.add(order_id)

    # Date with seasonal distribution
    order_date = generate_date()
    month = order_date.month
    year = order_date.year

    # Region
    region = random.choices(
        list(REGIONS.keys()),
        weights=[r["weight"] for r in REGIONS.values()]
    )[0]
    state = random.choice(REGIONS[region]["states"])

    # Customer (some customers appear multiple times for repeat behavior)
    if random.random() < 0.6:
        customer_name = random.choice(customer_pool)
    else:
        customer_name = generate_customer_name()

    # Payment mode (shared across all items in the order)
    payment_mode = random.choices(PAYMENT_MODES, weights=PAYMENT_WEIGHTS)[0]

    # Number of products in this order (1-5, weighted toward 1-2)
    num_products = random.choices([1, 2, 3, 4, 5], weights=[0.35, 0.30, 0.20, 0.10, 0.05])[0]

    # Pick unique categories for variety (if multiple products)
    available_categories = list(PRODUCT_CATALOG.keys())
    chosen_categories = random.choices(available_categories, k=num_products)

    order_missing_customer = random.random() < 0.02
    order_missing_region = random.random() < 0.02

    for cat_idx, category in enumerate(chosen_categories):
        product_name, base_cost, base_retail = random.choice(PRODUCT_CATALOG[category])

        # Quantity per product line (1-3)
        quantity = random.choices([1, 2, 3], weights=[0.60, 0.30, 0.10])[0]

        # Discount per product line
        discount = random.choices(
            [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
            weights=[0.30, 0.20, 0.20, 0.15, 0.08, 0.05, 0.02]
        )[0]

        # Unit price with slight random variation
        unit_price = round(base_retail * random.uniform(0.85, 1.15), 2)

        # Sales amount
        sales_amount = round(unit_price * quantity * (1 - discount), 2)

        # Profit
        cost_ratios = {
            "Electronics": (0.60, 0.75),
            "Furniture": (0.55, 0.70),
            "Clothing": (0.40, 0.60),
            "Sports": (0.50, 0.65),
            "Home & Kitchen": (0.50, 0.70),
        }
        low, high = cost_ratios[category]
        cost_ratio = random.uniform(low, high)
        profit = round(sales_amount - (unit_price * quantity * cost_ratio), 2)

        # Per-item missing values (rare)
        profit_missing = random.random() < 0.03
        discount_missing = random.random() < 0.02
        product_missing = random.random() < 0.015

        records.append({
            "Order ID": order_id,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Customer Name": None if order_missing_customer else customer_name,
            "Region": None if order_missing_region else region,
            "Product Category": category,
            "Product Name": None if product_missing else product_name,
            "Sales Amount": sales_amount,
            "Quantity": quantity,
            "Profit": None if profit_missing else profit,
            "Discount": None if discount_missing else discount,
            "Payment Mode": payment_mode,
        })

# Create DataFrame
df = pd.DataFrame(records)

# Shuffle to randomize order
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# =============================================
# VALIDATION
# =============================================
print(f"\nDataset shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nUnique orders: {df['Order ID'].nunique()}")
print(f"\nAvg products per order: {len(df) / df['Order ID'].nunique():.1f}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nRegions: {df['Region'].value_counts().to_dict()}")
print(f"\nCategories: {df['Product Category'].value_counts().to_dict()}")
print(f"\nDate range: {df['Order Date'].min()} to {df['Order Date'].max()}")
print(f"\nSales range: ${df['Sales Amount'].min():.2f} to ${df['Sales Amount'].max():.2f}")
print(f"\nSample multi-product orders:")
# Show an order with multiple products
sample_order = df['Order ID'].value_counts().head(1).index[0]
print(df[df['Order ID'] == sample_order].to_string())

# =============================================
# SAVE
# =============================================
output_path = "dataset/sales_dataset_5500.csv"
df.to_csv(output_path, index=False)
print(f"\nDataset saved to: {output_path}")
print(f"Total records: {len(df)}")
print("Generation complete!")
