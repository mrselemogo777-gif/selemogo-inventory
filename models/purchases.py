from database import get_connection, with_transaction
from .base import next_po_no


class Purchase:
    @staticmethod
    def create(items, supplier_id=None, notes=""):
        if not items:
            return False, "Purchase order is empty.", None
        try:
            with with_transaction() as cur:
                total_cost = 0
                for item in items:
                    row = cur.execute(
                        "SELECT name FROM products WHERE id=?",
                        (item["product_id"],),
                    ).fetchone()
                    if not row:
                        raise ValueError(f"Product {item['product_id']} not found")
                    if item["quantity"] <= 0:
                        raise ValueError(f"Invalid qty for {row['name']}")
                    if item["unit_cost"] < 0:
                        raise ValueError(f"Invalid cost for {row['name']}")
                    total_cost += item["quantity"] * item["unit_cost"]

                po_number = next_po_no(cur)
                cur.execute(
                    """INSERT INTO purchases (po_number, supplier_id, total_cost, notes)
                       VALUES (?, ?, ?, ?)""",
                    (po_number, supplier_id, total_cost, notes),
                )
                purchase_id = cur.lastrowid

                for item in items:
                    line_total = item["quantity"] * item["unit_cost"]
                    cur.execute(
                        """INSERT INTO purchase_items
                           (purchase_id, product_id, quantity, unit_cost, line_total)
                           VALUES (?, ?, ?, ?, ?)""",
                        (purchase_id, item["product_id"], item["quantity"],
                         item["unit_cost"], line_total),
                    )
                    cur.execute(
                        "UPDATE products SET stock = stock + ? WHERE id=?",
                        (item["quantity"], item["product_id"]),
                    )
                    cur.execute(
                        """INSERT INTO stock_movements
                           (product_id, movement_type, quantity, reference_type, reference_id, reason, user_name, action)
                           VALUES (?, 'IN', ?, 'PURCHASE', ?, ?, 'purchasing', 'Purchase')""",
                        (item["product_id"], item["quantity"], purchase_id,
                         f"Purchase {po_number}"),
                    )
            return True, f"Purchase {po_number} recorded — P {total_cost:,.2f}", purchase_id
        except Exception as e:
            return False, f"Purchase failed: {e}", None

    @staticmethod
    def list(limit=50):
        with get_connection() as c:
            return c.execute(
                """SELECT pu.*, s.name AS supplier
                   FROM purchases pu LEFT JOIN suppliers s ON s.id = pu.supplier_id
                   ORDER BY pu.purchase_date DESC LIMIT ?""",
                (limit,),
            ).fetchall()
