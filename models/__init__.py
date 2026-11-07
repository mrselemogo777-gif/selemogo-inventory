"""
Models package — class-based domain logic.

Re-exports flat function names for backward compatibility with pages/*.py,
which call `models.list_products(...)`, `models.create_sale(...)`, etc.

New code can use the classes directly:
    from models.catalog import Product
    Product.list(...)
"""
from .base import money, money0, CURRENCY_CODE, CURRENCY_SYMBOL
from .catalog import Category, Supplier, Product
from .sales import Sale
from .purchases import Purchase
from .reports import Reports

# --- Flat function shims (backwards-compatible) ---
list_categories = Category.list
add_category = Category.add

list_suppliers = Supplier.list
add_supplier = Supplier.add

list_products = Product.list
count_products = Product.count
add_product = Product.add
update_product = Product.update
low_stock_list = Product.low_stock

create_sale = Sale.create
list_sales = Sale.list
get_sale_items = Sale.items

create_purchase = Purchase.create
list_purchases = Purchase.list

dashboard_kpis = Reports.dashboard_kpis
sales_by_day = Reports.sales_by_day
top_products = Reports.top_products
recent_movements = Reports.recent_movements
pnl_report = Reports.pnl

__all__ = [
    "money", "money0", "CURRENCY_CODE", "CURRENCY_SYMBOL",
    "Category", "Supplier", "Product", "Sale", "Purchase", "Reports",
    "list_categories", "add_category",
    "list_suppliers", "add_supplier",
    "list_products", "count_products", "add_product", "update_product", "low_stock_list",
    "create_sale", "list_sales", "get_sale_items",
    "create_purchase", "list_purchases",
    "dashboard_kpis", "sales_by_day", "top_products", "recent_movements", "pnl_report",
]
