"""
seed_data.py - Database setup and seed data generator for AI-Powered SQL Agent.
Creates SQLite database with customers, orders, order_items, and products tables.
Seeds data specifically tailored to validate the 5 assignment questions:
1. Top 10 customers by revenue
2. Revenue last month
3. Country with highest average order value
4. Customers without orders in last 90 days
5. Percentage of cancelled orders
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def create_schema(cursor):
    cursor.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT NOT NULL,
        created_at DATETIME NOT NULL
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATETIME NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('completed', 'cancelled', 'pending', 'shipped')),
        total_amount REAL NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)


def seed_data(conn):
    cursor = conn.cursor()
    now = datetime.now()

    # 1. Customers (20 customers across multiple countries)
    customers_data = [
        ("Ahmed", "Hassan", "ahmed.hassan@example.com", "Egypt", now - timedelta(days=200)),
        ("Sara", "Ali", "sara.ali@example.com", "Egypt", now - timedelta(days=180)),
        ("John", "Doe", "john.doe@example.com", "USA", now - timedelta(days=300)),
        ("Emily", "Smith", "emily.smith@example.com", "USA", now - timedelta(days=150)),
        ("Tarek", "Mansour", "tarek.mansour@example.com", "UAE", now - timedelta(days=120)),
        ("Fatima", "Al-Zahra", "fatima.z@example.com", "UAE", now - timedelta(days=90)),
        ("Hans", "Muller", "hans.muller@example.com", "Germany", now - timedelta(days=250)),
        ("Greta", "Schneider", "greta.s@example.com", "Germany", now - timedelta(days=210)),
        ("Pierre", "Dubois", "pierre.d@example.com", "France", now - timedelta(days=350)),
        ("Claire", "Moreau", "claire.m@example.com", "France", now - timedelta(days=130)),
        ("Omar", "Khaled", "omar.k@example.com", "Egypt", now - timedelta(days=400)),
        ("Layla", "Nour", "layla.nour@example.com", "Saudi Arabia", now - timedelta(days=160)),
        ("Zaid", "Harbi", "zaid.harbi@example.com", "Saudi Arabia", now - timedelta(days=100)),
        ("David", "Brown", "david.brown@example.com", "UK", now - timedelta(days=280)),
        ("Sophie", "Taylor", "sophie.t@example.com", "UK", now - timedelta(days=110)),
        ("Liam", "Wilson", "liam.wilson@example.com", "Canada", now - timedelta(days=310)),
        ("Olivia", "Clark", "olivia.clark@example.com", "Canada", now - timedelta(days=70)),
        ("Nour", "Eldin", "nour.eldin@example.com", "Egypt", now - timedelta(days=500)),
        ("Youssef", "Ibrahim", "youssef.i@example.com", "Egypt", now - timedelta(days=450)),
        ("Khaled", "Saeed", "khaled.saeed@example.com", "UAE", now - timedelta(days=60)),
    ]

    cursor.executemany("""
    INSERT INTO customers (first_name, last_name, email, country, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, [(c[0], c[1], c[2], c[3], c[4].strftime('%Y-%m-%d %H:%M:%S')) for c in customers_data])

    # 2. Products
    products_data = [
        ("Solar Inverter 5kW", "CleanTech", 1200.00),
        ("Smart Energy Monitor", "CleanTech", 250.00),
        ("Weather Sensor IoT", "Geospatial Hardware", 450.00),
        ("GIS Mapping Drone Unit", "Geospatial Hardware", 3500.00),
        ("LiDAR Scanning Attachment", "Geospatial Hardware", 5200.00),
        ("Thermal Environmental Probe", "CleanTech", 680.00),
        ("Soil Carbon Analyzer", "AgriTech", 1850.00),
        ("Water Quality Sensor Kit", "CleanTech", 890.00),
    ]

    cursor.executemany("""
    INSERT INTO products (product_name, category, price)
    VALUES (?, ?, ?)
    """, products_data)

    # 3. Orders & Items
    # Key scenarios needed:
    # - Inactive customers (no orders in last 90 days): e.g. Customer 18 (Nour), 19 (Youssef), 9 (Pierre Dubois).
    # - Orders in last month: date between (now - 30 days) and (now - 5 days).
    # - Top customers: e.g. Tarek (UAE), Hans (Germany), Ahmed (Egypt).
    # - Cancelled orders percentage: 5 cancelled out of 25 orders = 20%.
    # - Highest average order value by country: UAE purchases high-ticket LiDAR & Drone units.

    orders_config = [
        # Customer, days_ago, status, items [(product_id, qty)]
        # Top 1 - Tarek (UAE) -> Large orders
        (5, 15, 'completed', [(4, 2), (5, 1)]),          # 2*3500 + 5200 = 12200 (Last month)
        (5, 45, 'completed', [(4, 1), (3, 2)]),          # 3500 + 900 = 4400
        # Top 2 - Hans (Germany)
        (7, 20, 'completed', [(5, 2)]),                  # 10400 (Last month)
        (7, 110, 'completed', [(1, 2)]),                 # 2400
        # Top 3 - Ahmed (Egypt)
        (1, 10, 'completed', [(1, 3), (2, 2)]),          # 3600 + 500 = 4100 (Last month)
        (1, 55, 'completed', [(7, 2)]),                  # 3700
        # Top 4 - Sara (Egypt)
        (2, 25, 'completed', [(1, 2), (8, 1)]),          # 2400 + 890 = 3290 (Last month)
        # Top 5 - John (USA)
        (3, 40, 'completed', [(7, 1), (6, 1)]),          # 1850 + 680 = 2530
        (3, 150, 'completed', [(1, 1)]),                 # 1200
        # Top 6 - Fatima (UAE)
        (6, 12, 'completed', [(5, 1), (3, 1)]),          # 5200 + 450 = 5650 (Last month)
        # Top 7 - Layla (Saudi Arabia)
        (12, 18, 'completed', [(4, 1)]),                 # 3500 (Last month)
        # Top 8 - David (UK)
        (14, 80, 'completed', [(1, 2)]),                 # 2400
        # Top 9 - Sophie (UK)
        (15, 35, 'completed', [(7, 1)]),                 # 1850
        # Top 10 - Emily (USA)
        (4, 75, 'completed', [(8, 2)]),                  # 1780
        # Cancelled orders (for testing percentage of cancelled orders)
        (1, 8, 'cancelled', [(1, 1)]),                   # 1200 - cancelled
        (3, 22, 'cancelled', [(4, 1)]),                  # 3500 - cancelled
        (8, 60, 'cancelled', [(2, 2)]),                  # 500 - cancelled
        (10, 115, 'cancelled', [(6, 1)]),                # 680 - cancelled
        (13, 140, 'cancelled', [(7, 1)]),                # 1850 - cancelled
        # Older orders (> 90 days ago) for customers who became inactive
        (9, 200, 'completed', [(1, 1)]),                 # Pierre (France) - last ordered 200 days ago
        (11, 120, 'completed', [(2, 1)]),                # Omar (Egypt) - last ordered 120 days ago
        (16, 100, 'completed', [(8, 1)]),                # Liam (Canada) - last ordered 100 days ago
        # Recent orders (< 90 days)
        (17, 30, 'completed', [(2, 2)]),                 # Olivia (Canada)
        (20, 5, 'completed', [(3, 2)]),                  # Khaled (UAE)
    ]

    for cust_id, days_ago, status, items in orders_config:
        order_date = now - timedelta(days=days_ago)
        # calculate total amount
        total = 0.0
        item_rows = []
        for prod_id, qty in items:
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (prod_id,))
            price = cursor.fetchone()[0]
            subtotal = price * qty
            total += subtotal
            item_rows.append((prod_id, qty, price))

        cursor.execute("""
        INSERT INTO orders (customer_id, order_date, status, total_amount)
        VALUES (?, ?, ?, ?)
        """, (cust_id, order_date.strftime('%Y-%m-%d %H:%M:%S'), status, total))

        order_id = cursor.lastrowid

        for prod_id, qty, price in item_rows:
            cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """, (order_id, prod_id, qty, price))

    conn.commit()


def get_schema_representation():
    """Return schema representation as string for the LLM prompt."""
    return """
Table: customers
- customer_id (INTEGER, PK)
- first_name (TEXT)
- last_name (TEXT)
- email (TEXT)
- country (TEXT)
- created_at (DATETIME)

Table: products
- product_id (INTEGER, PK)
- product_name (TEXT)
- category (TEXT)
- price (REAL)

Table: orders
- order_id (INTEGER, PK)
- customer_id (INTEGER, FK -> customers.customer_id)
- order_date (DATETIME)
- status (TEXT: 'completed', 'cancelled', 'pending', 'shipped')
- total_amount (REAL)

Table: order_items
- item_id (INTEGER, PK)
- order_id (INTEGER, FK -> orders.order_id)
- product_id (INTEGER, FK -> products.product_id)
- quantity (INTEGER)
- unit_price (REAL)
"""


def init_db():
    print(f"Initializing database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    seed_data(conn)
    conn.close()
    print("Database initialized and seeded successfully.")


if __name__ == "__main__":
    init_db()
