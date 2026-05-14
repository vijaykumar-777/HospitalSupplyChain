"""
Synthetic Data Generator for Hospital Supply Chain.
Generates realistic data with statistical distributions per PRD specs.
"""
import uuid
import json
import random
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Hospital location (Bengaluru)
HOSPITAL_LAT, HOSPITAL_LNG = 12.9716, 77.5946

# --- Constants ---
INDIAN_CITIES = {
    "Mumbai":     {"lat": 19.0760, "lng": 72.8777, "state": "Maharashtra", "pharma_weight": 0.4},
    "Chennai":    {"lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu", "pharma_weight": 0.2},
    "Delhi":      {"lat": 28.7041, "lng": 77.1025, "state": "Delhi", "pharma_weight": 0.3},
    "Hyderabad":  {"lat": 17.3850, "lng": 78.4867, "state": "Telangana", "pharma_weight": 0.35},
    "Pune":       {"lat": 18.5204, "lng": 73.8567, "state": "Maharashtra", "pharma_weight": 0.25},
    "Kolkata":    {"lat": 22.5726, "lng": 88.3639, "state": "West Bengal", "pharma_weight": 0.15},
    "Ahmedabad":  {"lat": 23.0225, "lng": 72.5714, "state": "Gujarat", "pharma_weight": 0.2},
}

CATEGORIES = ["medicine", "instrument", "consumable", "equipment"]

SEASONAL_MULTIPLIER = {
    "respiratory": {"monsoon": 1.4, "winter": 1.6, "summer": 0.9, "post_monsoon": 1.1},
    "trauma":      {"monsoon": 1.3, "winter": 1.0, "summer": 1.1, "post_monsoon": 1.2},
    "burn":        {"monsoon": 1.0, "winter": 1.1, "summer": 1.3, "post_monsoon": 1.0},
    "general":     {"monsoon": 1.1, "winter": 1.1, "summer": 1.0, "post_monsoon": 1.0},
}

DAY_OF_WEEK_MULTIPLIER = [1.10, 1.15, 1.10, 1.05, 1.00, 0.75, 0.65]

UNIT_PRICE_INR = {
    "medicine":   {"low": 2, "high": 500},
    "consumable": {"low": 5, "high": 150},
    "instrument": {"low": 200, "high": 15000},
    "equipment":  {"low": 2000, "high": 150000},
}

MEDICINES = [
    "Paracetamol 500mg", "Amoxicillin 250mg", "IV Normal Saline 500ml",
    "Insulin Glargine 100IU", "Morphine Sulfate 10mg", "Metformin 500mg",
    "Amlodipine 5mg", "Omeprazole 20mg", "Ciprofloxacin 500mg",
    "Azithromycin 500mg", "Diclofenac 50mg", "Ceftriaxone 1g IV",
    "Metronidazole 400mg", "Dexamethasone 4mg", "Atropine 0.6mg",
    "Adrenaline 1mg", "Lidocaine 2%", "Heparin 5000IU",
    "Enoxaparin 40mg", "Tramadol 50mg", "Ondansetron 4mg",
    "Furosemide 40mg", "Salbutamol Nebulizer 2.5mg", "Ranitidine 150mg",
    "Pantoprazole 40mg IV",
]

INSTRUMENTS = [
    "Scalpel Handle No.3", "Scalpel Handle No.4", "Mayo Scissors Curved",
    "Metzenbaum Scissors", "Artery Forceps Curved", "Artery Forceps Straight",
    "Needle Holder 6in", "Tissue Forceps", "Retractor Langenbeck",
    "Retractor Army-Navy", "Suction Cannula Yankauer", "Bone Rongeur",
    "Wire Cutter Ortho", "Periosteal Elevator", "Towel Clip",
    "Sponge Holder", "Babcock Forceps", "Allis Forceps",
    "Kocher Forceps", "Debakey Forceps",
]

CONSUMABLES = [
    "Nitrile Gloves M", "Nitrile Gloves L", "Syringes 5ml",
    "Syringes 10ml", "IV Cannula 18G", "IV Cannula 20G",
    "IV Cannula 22G", "Gauze Rolls 4in", "Cotton Rolls 500g",
    "Surgical Tape 1in", "Foley Catheter 16Fr", "Foley Catheter 18Fr",
    "Suture Silk 2-0", "Suture Vicryl 3-0", "Suture Ethilon 4-0",
    "Face Mask 3-ply", "N95 Respirator", "Surgical Gown Disposable",
    "Crepe Bandage 4in", "Elastic Bandage 6in", "ABD Pad 5x9",
    "Sterile Drape Sheet", "Blood Collection Tube EDTA",
    "Urine Collection Bag", "Oxygen Mask Adult",
]

EQUIPMENT = [
    "Pulse Oximeter Fingertip", "Infusion Pump IV", "BP Monitor Digital",
    "Nebulizer Portable", "Glucometer Kit", "ECG Machine 12-lead",
    "Defibrillator AED", "Suction Machine Portable",
    "Laryngoscope Set", "Ambu Bag Adult",
]

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def get_season(month):
    if month in (6, 7, 8, 9): return "monsoon"
    if month in (10, 11): return "post_monsoon"
    if month in (12, 1, 2): return "winter"
    return "summer"


# ============================================================
# 1. SUPPLIERS (30 records)
# ============================================================
def generate_suppliers():
    rows = []
    cities = list(INDIAN_CITIES.keys())

    for i in range(30):
        sid = str(uuid.uuid4())
        city = random.choice(cities)
        info = INDIAN_CITIES[city]

        # Bimodal reliability
        if random.random() < 0.7:
            rel = np.clip(np.random.normal(0.87, 0.05), 0.30, 0.99)
        else:
            rel = np.clip(np.random.normal(0.58, 0.08), 0.30, 0.99)

        dist = haversine(HOSPITAL_LAT, HOSPITAL_LNG, info["lat"], info["lng"])
        lead = max(1, int(1 + dist / 300 + np.random.normal(0, 0.5)))

        # Category weighting by city
        n_cats = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        weights = [info["pharma_weight"], 0.25, 0.25, 1 - info["pharma_weight"] - 0.25]
        weights = [max(0.05, w) for w in weights]
        cats = random.sample(CATEGORIES, k=min(n_cats, 4))

        is_emergency = i >= 25 and i < 29
        is_govt = i == 29

        rows.append({
            "supplier_id": sid, "name": fake.company() if not is_govt else "CMSS Central Medical Services Society",
            "city": city, "state": info["state"],
            "lat": round(info["lat"] + random.uniform(-0.1, 0.1), 4),
            "lng": round(info["lng"] + random.uniform(-0.1, 0.1), 4),
            "reliability_score": round(float(rel), 2),
            "avg_lead_days": lead,
            "supply_categories": json.dumps(cats),
            "is_emergency_certified": is_emergency or is_govt,
            "is_govt_reserve": is_govt,
            "contact_email": fake.email(),
            "contact_phone": fake.phone_number(),
            "created_at": datetime.now().isoformat(),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "suppliers.csv", index=False)
    print(f"  ✓ suppliers.csv — {len(df)} records")
    return df


# ============================================================
# 2. ITEMS (80 records)
# ============================================================
def generate_items():
    rows = []
    crit_pool = (["life_critical"] * 8 + ["high"] * 24 + ["medium"] * 32 + ["low"] * 16)
    random.shuffle(crit_pool)

    all_items = [
        (MEDICINES, "medicine", "tablets", ["respiratory", "general", "trauma"]),
        (INSTRUMENTS, "instrument", "pcs", ["trauma", "general"]),
        (CONSUMABLES, "consumable", "units", ["trauma", "burn", "respiratory", "general"]),
        (EQUIPMENT, "equipment", "units", ["trauma", "respiratory", "general"]),
    ]

    idx = 0
    for names, cat, unit, surge_opts in all_items:
        for name in names:
            demand = max(10, int(np.random.lognormal(4.5, 0.8)))
            rows.append({
                "item_id": str(uuid.uuid4()),
                "name": name, "category": cat,
                "criticality": crit_pool[idx % len(crit_pool)],
                "unit": unit,
                "disaster_surge_category": random.choice(surge_opts),
                "typical_monthly_demand": demand,
                "created_at": datetime.now().isoformat(),
            })
            idx += 1

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "items.csv", index=False)
    print(f"  ✓ items.csv — {len(df)} records")
    return df


# ============================================================
# 3. ORDERS (500 records)
# ============================================================
def generate_orders(suppliers_df, items_df):
    rows = []
    now = datetime.now()
    sup_list = suppliers_df.to_dict("records")
    item_list = items_df.to_dict("records")

    for i in range(500):
        item = random.choice(item_list)
        item_cats = item["category"]

        # Weighted supplier selection
        weights = []
        for s in sup_list:
            s_cats = json.loads(s["supply_categories"]) if isinstance(s["supply_categories"], str) else s["supply_categories"]
            cat_w = 2.0 if item_cats in s_cats else 0.3
            dist = haversine(HOSPITAL_LAT, HOSPITAL_LNG, s["lat"], s["lng"])
            dist_w = 1.0 / (1.0 + dist / 500)
            rel_w = s["reliability_score"]
            weights.append(cat_w * dist_w * rel_w)

        total = sum(weights)
        weights = [w / total for w in weights]
        supplier = random.choices(sup_list, weights=weights, k=1)[0]

        qty = max(10, int(np.random.lognormal(4.5, 0.8)))

        # Weekday-weighted order dates
        day_offset = random.randint(0, 364)
        order_dt = now - timedelta(days=day_offset)
        dow = order_dt.weekday()
        dow_weights = [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.2]
        if random.random() > dow_weights[dow]:
            order_dt -= timedelta(days=(dow - 4) if dow > 4 else 0)

        lead = max(1, supplier["avg_lead_days"] + int(np.random.normal(0, 1)))
        exp_date = (order_dt + timedelta(days=lead)).date()

        statuses = ["pending", "in_transit", "delivered", "delayed"]
        status = random.choices(statuses, weights=[0.15, 0.15, 0.55, 0.15])[0]

        rows.append({
            "order_id": str(uuid.uuid4()),
            "item_id": item["item_id"],
            "supplier_id": supplier["supplier_id"],
            "quantity": qty,
            "order_date": order_dt.isoformat(),
            "expected_delivery_date": exp_date.isoformat(),
            "status": status,
            "is_emergency_order": False,
            "triggered_by_disaster_event_id": None,
            "created_at": datetime.now().isoformat(),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "orders.csv", index=False)
    print(f"  ✓ orders.csv — {len(df)} records")
    return df


# ============================================================
# 4. DELIVERY HISTORY (500 records)
# ============================================================
def generate_delivery_history(orders_df, suppliers_df):
    sup_map = {s["supplier_id"]: s for s in suppliers_df.to_dict("records")}
    rows = []

    for _, order in orders_df.iterrows():
        sup = sup_map.get(order["supplier_id"], {})
        rel = sup.get("reliability_score", 0.7)
        order_dt = datetime.fromisoformat(str(order["order_date"]))
        month = order_dt.month
        season = get_season(month)

        is_good = rel >= 0.65
        is_monsoon = season == "monsoon"

        # Conditional exponential delay
        r = random.random()
        if r < 0.65:
            delay = 0
        elif r < 0.70:
            delay = -random.randint(1, 2)  # early
        else:
            if is_monsoon and not is_good:
                delay = min(21, int(np.random.exponential(6)))
            elif is_monsoon and is_good:
                delay = min(14, int(np.random.exponential(2.5)))
            elif not is_monsoon and not is_good:
                delay = min(14, int(np.random.exponential(3)))
            else:
                delay = min(7, int(np.random.exponential(1.2)))

        exp_date = datetime.fromisoformat(str(order["expected_delivery_date"])).date() if isinstance(order["expected_delivery_date"], str) else order["expected_delivery_date"]
        actual = exp_date + timedelta(days=delay) if order["status"] in ("delivered", "delayed") else None

        reasons_monsoon = ["weather", "weather", "transport", "stock_shortage", "other"]
        reasons_normal = ["transport", "stock_shortage", "customs", "other"]
        reason = random.choice(reasons_monsoon if is_monsoon else reasons_normal) if delay > 0 else None

        rows.append({
            "delivery_id": str(uuid.uuid4()),
            "order_id": order["order_id"],
            "supplier_id": order["supplier_id"],
            "item_id": order["item_id"],
            "expected_date": str(exp_date),
            "actual_date": str(actual) if actual else None,
            "delay_days": delay,
            "delay_reason": reason,
            "season": season,
            "created_at": datetime.now().isoformat(),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "delivery_history.csv", index=False)
    print(f"  ✓ delivery_history.csv — {len(df)} records")
    return df


# ============================================================
# 5. PURCHASE ORDERS (500 records)
# ============================================================
def generate_purchase_orders(orders_df, items_df):
    item_map = {i["item_id"]: i for i in items_df.to_dict("records")}
    rows = []

    for idx, (_, order) in enumerate(orders_df.iterrows()):
        item = item_map.get(order["item_id"], {})
        cat = item.get("category", "consumable")
        price_range = UNIT_PRICE_INR.get(cat, {"low": 10, "high": 100})
        unit_price = random.uniform(price_range["low"], price_range["high"])
        total = round(order["quantity"] * unit_price, 2)

        r = random.random()
        if r < 0.90: status = "approved"
        elif r < 0.95: status = "pending_approval"
        else: status = "rejected"

        terms = random.choices(["NET30", "NET60", "advance"], weights=[0.6, 0.3, 0.1])[0]
        pay_status = "paid" if status == "approved" and random.random() < 0.8 else ("overdue" if random.random() < 0.1 else "pending")

        order_dt = datetime.fromisoformat(str(order["order_date"]))
        approval_dt = order_dt + timedelta(hours=random.randint(2, 48)) if status == "approved" else None

        rows.append({
            "po_id": str(uuid.uuid4()),
            "po_number": f"PO-2025-{idx+1:05d}",
            "order_id": order["order_id"],
            "raised_by": fake.name(),
            "approved_by": fake.name() if status == "approved" else None,
            "approval_date": approval_dt.isoformat() if approval_dt else None,
            "approval_status": status,
            "budget_code": f"PHARM-2025-Q{random.randint(1,4)}",
            "payment_terms": terms,
            "payment_status": pay_status,
            "total_value_inr": total,
            "created_at": datetime.now().isoformat(),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "purchase_orders.csv", index=False)
    print(f"  ✓ purchase_orders.csv — {len(df)} records")
    return df


# ============================================================
# 6. GOODS RECEIPT NOTES
# ============================================================
def generate_grns(orders_df, po_df, items_df):
    po_map = {p["order_id"]: p for p in po_df.to_dict("records")}
    item_map = {i["item_id"]: i for i in items_df.to_dict("records")}
    rows = []
    grn_idx = 0

    for _, order in orders_df.iterrows():
        if order["status"] not in ("delivered", "delayed"):
            continue
        po = po_map.get(order["order_id"])
        if not po:
            continue

        item = item_map.get(order["item_id"], {})
        qty = order["quantity"]

        # 95% full shipment, 5% short
        if random.random() < 0.95:
            recv_qty = qty
        else:
            recv_qty = max(1, int(qty * random.uniform(0.85, 0.99)))

        # Quality
        r = random.random()
        if r < 0.88:
            q_status, rej_qty, reason = "accepted", 0, None
        elif r < 0.96:
            rej_qty = max(1, int(recv_qty * random.uniform(0.05, 0.2)))
            q_status, reason = "partially_accepted", random.choices(
                ["damaged", "expired", "wrong_item", "packaging_defect"],
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]
        else:
            q_status, rej_qty = "rejected", recv_qty
            reason = random.choices(
                ["damaged", "expired", "wrong_item", "packaging_defect"],
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]

        acc_qty = recv_qty - rej_qty
        order_dt = datetime.fromisoformat(str(order["order_date"]))
        recv_date = order_dt + timedelta(days=random.randint(2, 14))

        cat = item.get("category", "")
        exp_date = None
        if cat in ("medicine", "consumable"):
            exp_date = (recv_date + timedelta(days=random.randint(180, 1080))).date().isoformat()

        rows.append({
            "grn_id": str(uuid.uuid4()),
            "grn_number": f"GRN-2025-{grn_idx+1:05d}",
            "order_id": order["order_id"],
            "po_id": po["po_id"],
            "received_date": recv_date.isoformat(),
            "received_by": fake.name(),
            "inspected_by": fake.name(),
            "ordered_qty": qty,
            "received_qty": recv_qty,
            "accepted_qty": acc_qty,
            "rejected_qty": rej_qty,
            "quality_status": q_status,
            "rejection_reason": reason,
            "added_to_inventory": q_status != "rejected",
            "batch_number": f"BT-2025-{random.randint(10000,99999)}",
            "expiry_date": exp_date,
            "created_at": datetime.now().isoformat(),
        })
        grn_idx += 1

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "goods_receipt_notes.csv", index=False)
    print(f"  ✓ goods_receipt_notes.csv — {len(df)} records")
    return df


# ============================================================
# 7. INVENTORY (80 records — sawtooth simulation)
# ============================================================
def generate_inventory(items_df):
    rows = []
    snapshots = []
    start_date = datetime.now() - timedelta(days=90)

    for idx, item in items_df.iterrows():
        demand = item.get("typical_monthly_demand", 100)
        daily_normal = max(1, demand / 30)
        surge_cat = item.get("disaster_surge_category", "general")
        disaster_mult = random.uniform(2.0, 5.0)
        daily_disaster = round(daily_normal * disaster_mult, 2)

        max_cap = int(daily_normal * random.randint(30, 60))
        reorder = int(daily_normal * random.randint(5, 10))

        # Sawtooth simulation
        stock = float(max_cap)
        for day in range(90):
            dt = start_date + timedelta(days=day)
            season = get_season(dt.month)
            dow = dt.weekday()
            consumption = daily_normal * SEASONAL_MULTIPLIER.get(surge_cat, {}).get(season, 1.0) * DAY_OF_WEEK_MULTIPLIER[dow]
            stock = max(0, stock - consumption)
            if stock <= reorder:
                restock = random.randint(reorder * 2, max_cap)
                stock = min(stock + restock, max_cap)
            snapshots.append({
                "item_id": item["item_id"],
                "date": dt.date().isoformat(),
                "stock": round(stock, 1),
            })

        # Intentionally leave ~10 items below reorder
        if idx < 10:
            stock = random.randint(0, reorder - 1)

        rows.append({
            "inventory_id": str(uuid.uuid4()),
            "item_id": item["item_id"],
            "current_stock": int(stock),
            "reorder_level": reorder,
            "max_capacity": max_cap,
            "daily_consumption_normal": round(daily_normal, 2),
            "daily_consumption_disaster": daily_disaster,
            "last_updated": datetime.now().isoformat(),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "inventory.csv", index=False)
    snap_df = pd.DataFrame(snapshots)
    snap_df.to_csv(OUTPUT_DIR / "inventory_snapshots.csv", index=False)
    print(f"  ✓ inventory.csv — {len(df)} records")
    print(f"  ✓ inventory_snapshots.csv — {len(snap_df)} records")
    return df


# ============================================================
# 8. DISASTER HISTORY (50 records)
# ============================================================
def generate_disaster_history():
    events = [
        ("flood", "Kerala", 2018, 5), ("cyclone", "Odisha (Fani)", 2019, 5),
        ("earthquake", "Gujarat (Bhuj)", 2001, 5), ("flood", "Chennai", 2015, 4),
        ("cyclone", "Amphan, West Bengal", 2020, 5), ("flood", "Assam", 2020, 4),
        ("earthquake", "Nepal-Bihar border", 2015, 4), ("cyclone", "Nisarga, Maharashtra", 2020, 3),
        ("flood", "Mumbai", 2005, 5), ("flood", "Uttarakhand (Kedarnath)", 2013, 5),
        ("cyclone", "Hudhud, Andhra Pradesh", 2014, 4), ("earthquake", "Sikkim", 2011, 4),
        ("fire", "Delhi factory fire", 2019, 3), ("collapse", "Mumbai building collapse", 2017, 3),
        ("flood", "Bihar", 2017, 4), ("cyclone", "Vardah, Chennai", 2016, 4),
        ("flood", "Karnataka", 2019, 4), ("earthquake", "Manipur", 2016, 3),
        ("flood", "Hyderabad", 2020, 3), ("cyclone", "Tauktae, Gujarat", 2021, 4),
    ]

    rows = []
    for _ in range(50):
        dtype, loc, year, sev = random.choice(events)
        year = year + random.randint(-2, 4)
        sev = max(1, min(5, sev + random.randint(-1, 1)))

        mults = {
            "trauma": round(random.uniform(2.0, 5.0), 1),
            "burn": round(random.uniform(1.5, 4.0), 1),
            "respiratory": round(random.uniform(1.5, 3.5), 1),
            "general": round(random.uniform(1.2, 2.5), 1),
        }
        delay_added = round(sev * random.uniform(0.8, 2.0), 1)

        rows.append({
            "hist_id": str(uuid.uuid4()),
            "disaster_type": dtype,
            "severity": sev,
            "location_name": loc,
            "year": year,
            "items_most_affected": json.dumps(["trauma", "respiratory"] if dtype in ("earthquake", "collapse") else ["trauma", "burn"]),
            "avg_supply_delay_added_days": delay_added,
            "demand_multipliers": json.dumps(mults),
            "notes": f"Severity {sev} {dtype} in {loc} ({year}). Major supply chain disruption.",
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "disaster_history.csv", index=False)
    print(f"  ✓ disaster_history.csv — {len(df)} records")
    return df


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n━━━ Hospital Supply Chain — Synthetic Data Generator ━━━\n")

    print("Generating suppliers...")
    suppliers = generate_suppliers()

    print("Generating items...")
    items = generate_items()

    print("Generating orders...")
    orders = generate_orders(suppliers, items)

    print("Generating delivery history...")
    generate_delivery_history(orders, suppliers)

    print("Generating purchase orders...")
    pos = generate_purchase_orders(orders, items)

    print("Generating goods receipt notes...")
    generate_grns(orders, pos, items)

    print("Generating inventory (sawtooth sim)...")
    generate_inventory(items)

    print("Generating disaster history...")
    generate_disaster_history()

    print(f"\n✅ All CSVs written to: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
