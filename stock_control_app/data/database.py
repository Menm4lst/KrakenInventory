import sqlite3
import os


def init_db():
    conn = sqlite3.connect("stock_control.db")
    cursor = conn.cursor()
    
    # Tabla de productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        current_stock INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 0,
        max_stock INTEGER DEFAULT 0,
        cost REAL DEFAULT 0,
        price REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabla de movimientos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'in' or 'out'
        quantity INTEGER NOT NULL,
        reason TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)
    
    # Índices para mejorar rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_product_id ON movements(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_created_at ON movements(created_at)")
    
    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect("stock_control.db")