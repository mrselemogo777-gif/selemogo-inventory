from database import init_db, get_connection
import models


def seed():
    init_db()
    with get_connection() as c:
        if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] > 0:
            print("Already seeded. Delete data/inventory.db to reset.")
            return

    cats = ["Construction", "Solar & Power", "Electronics", "Hardware", "Plumbing"]
    for cat in cats:
        models.add_category(cat, f"{cat} supplies")
    cat_ids = {c["name"]: c["id"] for c in models.list_categories()}

    suppliers = [
        ("Botswana Builders Depot", "Thabo Molefe", "sales@bbdepot.co.bw", "+267 71 234 567", "Gaborone"),
        ("SolarTech Botswana", "Naledi Kgosi", "info@solartech.co.bw", "+267 72 345 678", "Francistown"),
        ("Kgalagadi Hardware Wholesale", "Kagiso Phiri", "orders@kgalahardware.co.bw", "+267 73 456 789", "Maun"),
        ("Phakalane Electronics", "Mpho Sekgoma", "sales@phakalane-elec.co.bw", "+267 74 567 890", "Gaborone"),
    ]
    for s in suppliers:
        models.add_supplier(*s)
    sup_ids = {s["name"]: s["id"] for s in models.list_suppliers()}

    products = [
        ("CEM-001", "PPC Cement 50kg",              "Construction",   "Botswana Builders Depot",   85,    115,    800,  100),
        ("CEM-002", "Lafarge Cement 50kg",          "Construction",   "Botswana Builders Depot",   88,    120,    600,  100),
        ("BRK-001", "Clay Bricks (per 100)",        "Construction",   "Botswana Builders Depot",   450,   650,    200,  30),
        ("RBR-001", "Rebar 12mm x 6m",              "Construction",   "Kgalagadi Hardware Wholesale", 95, 145,    500,  80),
        ("TIM-001", "Pine Timber 4x2 (2.4m)",       "Construction",   "Kgalagadi Hardware Wholesale", 110, 165,   350,  50),
        ("SLR-001", "Solar Panel 450W Mono",        "Solar & Power",  "SolarTech Botswana",        1800,  2600,   120,  20),
        ("SLR-002", "Solar Panel 550W Mono",        "Solar & Power",  "SolarTech Botswana",        2200,  3100,   80,   15),
        ("INV-001", "Solar Inverter 5kW Hybrid",    "Solar & Power",  "SolarTech Botswana",        8500,  12500,  25,   5),
        ("BAT-001", "Lithium Battery 5.1kWh",       "Solar & Power",  "SolarTech Botswana",        12000, 17500,  18,   4),
        ("CHG-001", "Solar Charge Controller 60A",  "Solar & Power",  "SolarTech Botswana",        1200,  1850,   40,   10),
        ("ELC-001", "Samsung 55in 4K TV",           "Electronics",    "Phakalane Electronics",     5500,  7800,   22,   5),
        ("ELC-002", "Hisense 43in Smart TV",        "Electronics",    "Phakalane Electronics",     3200,  4500,   35,   8),
        ("ELC-003", "LG 1.5HP Split AC",            "Electronics",    "Phakalane Electronics",     6500,  9200,   14,   4),
        ("ELC-004", "Defy 300L Fridge",             "Electronics",    "Phakalane Electronics",     5800,  8200,   10,   3),
        ("HRD-001", "Bosch Drill 750W",             "Hardware",       "Kgalagadi Hardware Wholesale", 850, 1350,  45,   10),
        ("HRD-002", "Stanley Tool Kit 100pc",       "Hardware",       "Kgalagadi Hardware Wholesale", 1400, 2100,  28,   8),
        ("HRD-003", "Angle Grinder 900W",           "Hardware",       "Kgalagadi Hardware Wholesale", 750, 1150,  40,   10),
        ("PLB-001", "PVC Pipe 110mm x 6m",          "Plumbing",       "Botswana Builders Depot",   180,   260,    400,  60),
        ("PLB-002", "Geyser 150L Electric",         "Plumbing",       "Kgalagadi Hardware Wholesale", 2800, 4200,  22,   5),
        ("PLB-003", "Toilet Suite Complete",        "Plumbing",       "Botswana Builders Depot",   1200,  1800,   30,   8),
    ]
    for sku, name, cat, sup, cost, sell, stock, reorder in products:
        models.add_product(sku, name, cat_ids[cat], sup_ids[sup], cost, sell, stock, reorder)

    with get_connection() as c:
        pid = {r["sku"]: r["id"] for r in c.execute("SELECT id, sku FROM products").fetchall()}

    models.create_sale(
        [{"product_id": pid["CEM-001"], "quantity": 100},
         {"product_id": pid["BRK-001"], "quantity": 5}],
        customer_name="Mogoditshane Builders"
    )
    models.create_sale(
        [{"product_id": pid["SLR-001"], "quantity": 8},
         {"product_id": pid["INV-001"], "quantity": 1},
         {"product_id": pid["BAT-001"], "quantity": 1}],
        customer_name="Kgale Solar Installers"
    )
    models.create_sale(
        [{"product_id": pid["ELC-001"], "quantity": 2},
         {"product_id": pid["ELC-003"], "quantity": 1}],
        discount=500, customer_name="Walk-in Gaborone Mall"
    )
    models.create_sale(
        [{"product_id": pid["HRD-001"], "quantity": 3},
         {"product_id": pid["HRD-002"], "quantity": 2},
         {"product_id": pid["PLB-001"], "quantity": 20}],
        customer_name="Maun Construction Ltd"
    )
    models.create_sale(
        [{"product_id": pid["SLR-002"], "quantity": 5},
         {"product_id": pid["CHG-001"], "quantity": 5}],
        customer_name="Serowe Solar Co-op"
    )
    models.create_sale(
        [{"product_id": pid["CEM-002"], "quantity": 80},
         {"product_id": pid["TIM-001"], "quantity": 30}],
        customer_name="Palapye Hardware Retail"
    )

    models.create_purchase(
        [{"product_id": pid["CEM-001"], "quantity": 200, "unit_cost": 85},
         {"product_id": pid["RBR-001"], "quantity": 100, "unit_cost": 95}],
        supplier_id=sup_ids["Botswana Builders Depot"],
        notes="Monthly cement restock"
    )
    models.create_purchase(
        [{"product_id": pid["SLR-001"], "quantity": 20, "unit_cost": 1800},
         {"product_id": pid["BAT-001"], "quantity": 5, "unit_cost": 12000}],
        supplier_id=sup_ids["SolarTech Botswana"],
        notes="Q4 solar installation stock"
    )

    print("Seeded: 5 categories, 4 suppliers, 20 products, 6 sales, 2 purchases.")


if __name__ == "__main__":
    seed()
