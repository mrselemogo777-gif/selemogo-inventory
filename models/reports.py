from database import get_connection


class Reports:
    @staticmethod
    def dashboard_kpis():
        with get_connection() as c:
            products = c.execute("""
                SELECT COUNT(*) AS total,
                       COALESCE(SUM(stock * cost_price), 0) AS stock_value_cost,
                       COALESCE(SUM(stock * sell_price), 0) AS stock_value_retail,
                       SUM(CASE WHEN stock <= reorder_level THEN 1 ELSE 0 END) AS low_stock,
                       SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) AS out_of_stock
                FROM products WHERE is_active = 1
            """).fetchone()
            today = c.execute("""
                SELECT COUNT(*) AS sales_today,
                       COALESCE(SUM(total), 0) AS revenue_today,
                       COALESCE(SUM(profit), 0) AS profit_today
                FROM sales WHERE DATE(sale_date) = DATE('now')
            """).fetchone()
            return products, today

    @staticmethod
    def sales_by_day(days=30):
        with get_connection() as c:
            return c.execute(
                """SELECT DATE(sale_date) AS day, SUM(total) AS revenue,
                          SUM(profit) AS profit, COUNT(*) AS orders
                   FROM sales WHERE DATE(sale_date) >= DATE('now', ?)
                   GROUP BY DATE(sale_date) ORDER BY day""",
                (f"-{days} days",),
            ).fetchall()

    @staticmethod
    def top_products(limit=10, days=30):
        with get_connection() as c:
            return c.execute(
                """SELECT p.name, p.sku, SUM(si.quantity) AS units,
                          SUM(si.line_total) AS revenue,
                          SUM((si.unit_price - si.unit_cost) * si.quantity) AS profit
                   FROM sale_items si
                   JOIN sales s ON s.id = si.sale_id
                   JOIN products p ON p.id = si.product_id
                   WHERE DATE(s.sale_date) >= DATE('now', ?)
                   GROUP BY p.id ORDER BY revenue DESC LIMIT ?""",
                (f"-{days} days", limit),
            ).fetchall()

    @staticmethod
    def recent_movements(limit=20):
        with get_connection() as c:
            return c.execute(
                """SELECT m.id, m.product_id, p.name AS product, m.movement_type,
                          m.quantity, m.reference_type, m.reference_id, m.reason,
                          m.user_name, m.action, m.created_at
                   FROM stock_movements m JOIN products p ON p.id = m.product_id
                   ORDER BY m.created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()

    @staticmethod
    def pnl(start_date, end_date):
        with get_connection() as c:
            return c.execute(
                """SELECT COUNT(*) AS orders,
                          COALESCE(SUM(subtotal), 0) AS revenue,
                          COALESCE(SUM(discount), 0) AS discounts,
                          COALESCE(SUM(total), 0) AS net_revenue,
                          COALESCE(SUM(profit), 0) AS gross_profit
                   FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?""",
                (start_date, end_date),
            ).fetchone()
