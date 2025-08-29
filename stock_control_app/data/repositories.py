import sqlite3
from datetime import datetime


class ProductRepository:
    @staticmethod
    def get_all():
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name")
        products = cursor.fetchall()
        conn.close()
        return products

    @staticmethod
    def get_by_id(product_id):
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product

    @staticmethod
    def get_by_code(code):
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE code = ?", (code,))
        product = cursor.fetchone()
        conn.close()
        return product

    @staticmethod
    def create(product_data):
        conn = sqlite3.connect("stock_control.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO products 
            (code, name, description, category, current_stock, min_stock, max_stock, cost, price) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                product_data["code"],
                product_data["name"],
                product_data["description"],
                product_data["category"],
                product_data["current_stock"],
                product_data["min_stock"],
                product_data["max_stock"],
                product_data["cost"],
                product_data["price"],
            ),
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def update(product_id, product_data):
        conn = sqlite3.connect("stock_control.db")
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE products SET 
            code = ?, name = ?, description = ?, category = ?, 
            current_stock = ?, min_stock = ?, max_stock = ?, cost = ?, price = ?,
            updated_at = CURRENT_TIMESTAMP
            WHERE id = ?""",
            (
                product_data["code"],
                product_data["name"],
                product_data["description"],
                product_data["category"],
                product_data["current_stock"],
                product_data["min_stock"],
                product_data["max_stock"],
                product_data["cost"],
                product_data["price"],
                product_id,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(product_id):
        conn = sqlite3.connect("stock_control.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def search(search_term):
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM products 
            WHERE code LIKE ? OR name LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY name""",
            (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"),
        )
        products = cursor.fetchall()
        conn.close()
        return products

    @staticmethod
    def update_stock(product_id, new_stock):
        conn = sqlite3.connect("stock_control.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_stock, product_id),
        )
        conn.commit()
        conn.close()


class MovementRepository:
    @staticmethod
    def get_all():
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.*, p.code, p.name 
            FROM movements m 
            LEFT JOIN products p ON m.product_id = p.id 
            ORDER BY m.created_at DESC"""
        )
        movements = cursor.fetchall()
        conn.close()
        return movements

    @staticmethod
    def create(movement_data):
        conn = sqlite3.connect("stock_control.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO movements 
            (product_id, type, quantity, reason, notes) 
            VALUES (?, ?, ?, ?, ?)""",
            (
                movement_data["product_id"],
                movement_data["type"],
                movement_data["quantity"],
                movement_data["reason"],
                movement_data["notes"],
            ),
        )
        movement_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return movement_id

    @staticmethod
    def get_by_product_id(product_id):
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.*, p.code, p.name 
            FROM movements m 
            LEFT JOIN products p ON m.product_id = p.id 
            WHERE m.product_id = ?
            ORDER BY m.created_at DESC""",
            (product_id,),
        )
        movements = cursor.fetchall()
        conn.close()
        return movements

    @staticmethod
    def get_by_date_range(start_date, end_date):
        conn = sqlite3.connect("stock_control.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.*, p.code, p.name 
            FROM movements m 
            LEFT JOIN products p ON m.product_id = p.id 
            WHERE date(m.created_at) BETWEEN ? AND ?
            ORDER BY m.created_at DESC""",
            (start_date, end_date),
        )
        movements = cursor.fetchall()
        conn.close()
        return movements