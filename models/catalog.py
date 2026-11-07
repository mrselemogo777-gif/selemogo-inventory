from database import get_connection, with_transaction


class Category:
    @staticmethod
    def list():
        with get_connection() as c:
            return c.execute("SELECT * FROM categories ORDER BY name").fetchall()

    @staticmethod
    def add(name, description=""):
        try:
            with with_transaction() as cur:
                cur.execute(
                    "INSERT INTO categories (name, description) VALUES (?, ?)",
                    (name, description),
                )
            return True, "Category added."
        except Exception as e:
            return False, f"Error: {e}"


class Supplier:
    @staticmethod
    def list():
        with get_connection() as c:
            return c.execute("SELECT * FROM suppliers ORDER BY name").fetchall()

    @staticmethod
    def add(name, contact, email, phone, address):
        try:
            with with_transaction() as cur:
                cur.execute(
                    """INSERT INTO suppliers (name, contact_person, email, phone, address)
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, contact, email, phone, address),
                )
            return True, "Supplier added."
        except Exception as e:
            return False, f"Error: {e}"


class Product:
    @staticmethod
    def list(search="", category_id=None, only_low_stock=False, limit=25, offset=0):
        q = """SELECT p.*, c.name AS category, s.name AS supplier
               FROM products p
               LEFT JOIN categories c ON c.id = p.category_id
               LEFT JOIN suppliers s ON s.id = p.supplier_id
               WHERE p.is_active = 1"""
        params = []
        if search:
            q += " AND (p.name LIKE ? OR p.sku LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        if category_id:
            q += " AND p.category_id = ?"
            params.append(category_id)
        if only_low_stock:
            q += " AND p.stock <= p.reorder_level"
        q += " ORDER BY p.name LIMIT ? OFFSET ?"
        params += [limit, offset]
        with get_connection() as c:
            return c.execute(q, params).fetchall()

    @staticmethod
    def count(search="", category_id=None, only_low_stock=False):
        q = "SELECT COUNT(*) FROM products p WHERE p.is_active = 1"
        params = []
        if search:
            q += " AND (p.name LIKE ? OR p.sku LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        if category_id:
            q += " AND p.category_id = ?"
            params.append(category_id)
        if only_low_stock:
            q += " AND p.stock <= p.reorder_level"
        with get_connection() as c:
            return c.execute(q, params).fetchone()[0]

    @staticmethod
    def add(sku, name, category_id, supplier_id, cost_price, sell_price,
            stock, reorder_level):
        try:
            with with_transaction() as cur:
                cur.execute(
                    """INSERT INTO products
                       (sku, name, category_id, supplier_id, cost_price, sell_price, stock, reorder_level)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sku, name, category_id, supplier_id, cost_price, sell_price,
                     stock, reorder_level),
                )
                pid = cur.lastrowid
                if stock > 0:
                    cur.execute(
                        """INSERT INTO stock_movements
                           (product_id, movement_type, quantity, reference_type, reason, user_name, action)
                           VALUES (?, 'IN', ?, 'OPENING', 'Opening stock', 'admin', 'Opening Stock')""",
                        (pid, stock),
                    )
            return True, f"Product '{name}' added."
        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def update(pid, name, category_id, supplier_id, cost_price, sell_price, reorder_level):
        try:
            with with_transaction() as cur:
                cur.execute(
                    """UPDATE products SET name=?, category_id=?, supplier_id=?,
                       cost_price=?, sell_price=?, reorder_level=? WHERE id=?""",
                    (name, category_id, supplier_id, cost_price, sell_price,
                     reorder_level, pid),
                )
            return True, "Product updated."
        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def low_stock():
        with get_connection() as c:
            return c.execute("""
                SELECT id, sku, name, stock, reorder_level
                FROM products WHERE is_active = 1 AND stock <= reorder_level
                ORDER BY stock ASC
            """).fetchall()
