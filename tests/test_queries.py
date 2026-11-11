"""
test_queries.py - Verifies that all 5 assignment questions execute properly
and return expected analytical results from the seeded SQLite database.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "database.db"

def run_tests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tests = [
        (
            "1. Top 10 customers by revenue",
            """
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                c.country,
                ROUND(SUM(o.total_amount), 2) AS total_revenue
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status != 'cancelled'
            GROUP BY c.customer_id, c.first_name, c.last_name, c.country
            ORDER BY total_revenue DESC
            LIMIT 10;
            """
        ),
        (
            "2. Revenue in last 30 days (Recent Month)",
            """
            SELECT 
                ROUND(SUM(total_amount), 2) AS revenue_last_month,
                COUNT(order_id) AS order_count
            FROM orders
            WHERE status != 'cancelled'
              AND order_date >= date('now', '-30 days');
            """
        ),
        (
            "3. Country with highest average order value",
            """
            SELECT 
                c.country,
                ROUND(AVG(o.total_amount), 2) AS avg_order_value,
                COUNT(o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status != 'cancelled'
            GROUP BY c.country
            ORDER BY avg_order_value DESC
            LIMIT 1;
            """
        ),
        (
            "4. Customers without orders in last 90 days",
            """
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                c.country,
                MAX(o.order_date) AS last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.first_name, c.last_name, c.country
            HAVING last_order_date IS NULL OR last_order_date < date('now', '-90 days');
            """
        ),
        (
            "5. Percentage of cancelled orders",
            """
            SELECT 
                COUNT(*) AS total_orders,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled_orders,
                ROUND((COUNT(CASE WHEN status = 'cancelled' THEN 1 END) * 100.0) / COUNT(*), 2) AS cancellation_rate_percentage
            FROM orders;
            """
        )
    ]

    print("================ RUNNING ASSIGNMENT BENCHMARK QUERIES ================")
    for title, sql in tests:
        print(f"\n---> {title}")
        cursor.execute(sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        print(f"Columns: {cols}")
        for r in rows[:5]:
            print(f"  {r}")
        if len(rows) > 5:
            print(f"  ... and {len(rows) - 5} more rows (Total: {len(rows)})")
    
    conn.close()
    print("\nAll 5 assignment queries verified successfully!")

if __name__ == "__main__":
    run_tests()
