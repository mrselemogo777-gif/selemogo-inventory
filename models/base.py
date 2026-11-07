from datetime import datetime
from database import get_connection, with_transaction

CURRENCY_CODE = "BWP"
CURRENCY_SYMBOL = "P"


def money(amount, decimals=2):
    try:
        return f"{CURRENCY_SYMBOL} {float(amount):,.{decimals}f}"
    except (TypeError, ValueError):
        return f"{CURRENCY_SYMBOL} 0.00"


def money0(amount):
    return money(amount, decimals=0)


def next_invoice_no(cur):
    row = cur.execute("SELECT COUNT(*) FROM sales").fetchone()
    return f"INV-{datetime.now().strftime('%Y%m')}-{row[0] + 1:04d}"


def next_po_no(cur):
    row = cur.execute("SELECT COUNT(*) FROM purchases").fetchone()
    return f"PO-{datetime.now().strftime('%Y%m')}-{row[0] + 1:04d}"
