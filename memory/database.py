import sqlite3
import os

DB_PATH = "sales.db"

def init_database():
    """Create sample sales database with realistic data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10,2)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            city TEXT
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            customer_id INTEGER REFERENCES customers(id),
            quantity INTEGER,
            amount DECIMAL(10,2),
            sale_date DATE
        );

        -- Sample products
        INSERT OR IGNORE INTO products VALUES
            (1, 'Widget A', 'Electronics', 299.99),
            (2, 'Widget B', 'Electronics', 199.99),
            (3, 'Gadget X', 'Accessories', 49.99),
            (4, 'Gadget Y', 'Accessories', 79.99),
            (5, 'SuperTool', 'Tools', 149.99);

        -- Sample customers
        INSERT OR IGNORE INTO customers VALUES
            (1, 'Alice Johnson', 'alice@email.com', 'Mumbai'),
            (2, 'Bob Smith', 'bob@email.com', 'Delhi'),
            (3, 'Carol White', 'carol@email.com', 'Bangalore'),
            (4, 'David Brown', 'david@email.com', 'Chennai'),
            (5, 'Eva Davis', 'eva@email.com', 'Hyderabad');

        -- Sample sales (recent months)
        INSERT OR IGNORE INTO sales VALUES
            (1, 1, 1, 2, 599.98, '2025-03-05'),
            (2, 2, 2, 1, 199.99, '2025-03-12'),
            (3, 3, 3, 5, 249.95, '2025-03-18'),
            (4, 1, 4, 1, 299.99, '2025-02-10'),
            (5, 4, 5, 3, 239.97, '2025-02-20'),
            (6, 5, 1, 2, 299.98, '2025-02-25'),
            (7, 2, 2, 4, 799.96, '2025-01-08'),
            (8, 3, 3, 10, 499.90, '2025-01-15'),
            (9, 1, 4, 1, 299.99, '2025-01-22'),
            (10, 5, 5, 1, 149.99, '2025-03-28');
    """)

    conn.commit()
    conn.close()
    print(" Database initialized")

def get_schema() -> dict:
    """Return database schema as dict"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [
            {"name": row[1], "type": row[2], "primary_key": bool(row[5])}
            for row in cursor.fetchall()
        ]
        schema[table] = columns

    conn.close()
    return schema

def execute_query(sql: str) -> list:
    """Execute SQL and return results as list of dicts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results