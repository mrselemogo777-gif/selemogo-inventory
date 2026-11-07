from database import get_connection, with_transaction
from .base import next_invoice_no


class Sale:
    @staticmethod
    def create(items, discount=0, customer_name="", notes=""):
        if not items:
            return False, "Cart is empty.", None
        try:
            with with_transaction() as cur:
                subtotal = 0
                total_cost = 0
                resolved = []
                for item in items:
                    row = cur.execute(
                        "SELECT sell_price, cost_price, stock, name FROM products WHERE id=?",
                        (item["product_id"],),
                    ).fetchone()
                    if not row:
                        raise ValueError(f"Product {item['product_id']} not found")
                    if item["quantity"] <= 0:
                        raise ValueError(f"Invalid qty for {row['name']}")
                    if item["quantity"] > row["stock"]:
                        raise ValueError(
                            f"Insufficient stock for {row['name']} (only {row['stock']})"
                        )
                    line_total = row["sell_price"] * item["quantity"]
                    subtotal += line_total
                    total_cost += row["cost_price"] * item["quantity"]
                    resolved.append({
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": row["sell_price"],
                        "unit_cost": row["cost_price"],
                        "line_total": line_total,
                    })
                discount = max(0, min(discount, subtotal))
                total = subtotal - discount
                profit = total - total_cost
                invoice_no = next_invoice_no(cur)
                cur.execute(
                    """INSERT INTO sales
                       (invoice_no, subtotal, discount, total, profit, customer_name, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (invoice_no, subtotal, discount, total, profit, customer_name, notes),
                )
                sale_id = cur.lastrowid
                for r in resolved:
                    cur.execute(
                        """INSERT INTO sale_items
                           (sale_id, product_id, quantity, unit_price, unit_cost, line_total)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (sale_id, r["product_id"], r["quantity"],
                         r["unit_price"], r["unit_cost"], r["line_total"]),
                    )
                    cur.execute(
                        "UPDATE products SET stock = stock - ? WHERE id=?",
                        (r["quantity"], r["product_id"]),
                    )
                    cur.execute(
                        """INSERT INTO stock_movements
                           (product_id, movement_type, quantity, reference_type, reference_id, reason, user_name, action)
                           VALUES (?, 'OUT', ?, 'SALE', ?, ?, ?, 'Sale')""",
                        (r["product_id"], r["quantity"], sale_id,
                         f"Sale {invoice_no}", customer_name or "Walk-in"),
                    )
            return True, f"Sale {invoice_no} recorded — P {total:,.2f}", sale_id
        except Exception as e:
            return False, f"Sale failed: {e}", None

    @staticmethod
    def list(limit=50, offset=0, start_date=None, end_date=None):
        q = "SELECT * FROM sales WHERE 1=1"
        params = []
        if start_date:
            q += " AND DATE(sale_date) >= ?"
            params.append(start_date)
        if end_date:
            q += " AND DATE(sale_date) <= ?"
            params.append(end_date)
        q += " ORDER BY sale_date DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        with get_connection() as c:
            return c.execute(q, params).fetchall()

    @staticmethod
    def items(sale_id):
        with get_connection() as c:
            return c.execute(
                """SELECT si.*, p.name, p.sku
                   FROM sale_items si JOIN products p ON p.id = si.product_id
                   WHERE si.sale_id = ?""",
                (sale_id,),
            ).fetchall()
