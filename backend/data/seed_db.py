"""Seed the SQLite database from the project CSV datasets."""
import argparse
import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import Base, SessionLocal, engine
from backend.models import (
    AIPredictionsLog,
    AffectedRoute,
    DeliveryHistory,
    DisasterEvent,
    DisasterHistoryRecord,
    DisasterPrediction,
    GoodsReceiptNote,
    Inventory,
    Item,
    Order,
    PurchaseOrder,
    Supplier,
)

DATA_DIR = PROJECT_ROOT / "datasets"

UNIT_BY_CATEGORY = {
    "medicine": "units",
    "consumable": "units",
    "equipment": "units",
    "instrument": "pcs",
    "surgical": "pcs",
}

UNIT_PRICE_INR = {
    "medicine": 120.0,
    "consumable": 35.0,
    "equipment": 8000.0,
    "instrument": 950.0,
    "surgical": 650.0,
}


def clean(val, default=None):
    if pd.isna(val) or val is None or val == "None":
        return default
    return val


def parse_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if pd.isna(val) or val is None:
        return False
    return str(val).strip().lower() in {"1", "true", "yes", "y"}


def parse_dt(val):
    val = clean(val)
    if val is None:
        return None
    return pd.to_datetime(val).to_pydatetime()


def parse_date(val):
    val = clean(val)
    if val is None:
        return None
    return pd.to_datetime(val).date()


def parse_categories(val):
    if pd.isna(val) or val is None:
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(str(val))
    except json.JSONDecodeError:
        parsed = [part.strip() for part in str(val).split(",")]
    return [str(cat).strip() for cat in parsed if str(cat).strip()]


def get_season(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.month in (6, 7, 8, 9):
        return "monsoon"
    if dt.month in (10, 11):
        return "post_monsoon"
    if dt.month in (12, 1, 2):
        return "winter"
    return "summer"


def read_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset file: {path}")
    return pd.read_csv(path)


def reset_tables(db):
    for model in (
        AIPredictionsLog,
        AffectedRoute,
        DisasterPrediction,
        GoodsReceiptNote,
        PurchaseOrder,
        DeliveryHistory,
        Order,
        Inventory,
        DisasterHistoryRecord,
        DisasterEvent,
        Item,
        Supplier,
    ):
        db.query(model).delete()
    db.commit()


def seed(reset: bool = False):
    print("\n━━━ Seeding Database ━━━\n")
    print(f"  source — {DATA_DIR}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if reset:
            reset_tables(db)
            print("  reset — cleared existing database rows")

        suppliers_df = read_csv("suppliers.csv")
        for _, r in suppliers_df.iterrows():
            db.add(Supplier(
                supplier_id=r["supplier_id"],
                name=r["name"],
                city=r["city"],
                state=r["state"],
                lat=float(r["lat"]),
                lng=float(r["lng"]),
                reliability_score=float(r["reliability_score"]),
                avg_lead_days=int(r["avg_lead_days"]),
                supply_categories=parse_categories(r["supply_categories"]),
                is_emergency_certified=parse_bool(r["is_emergency_certified"]),
                is_govt_reserve=parse_bool(r["is_govt_reserve"]),
                contact_email=clean(r.get("contact_email")),
                contact_phone=clean(r.get("contact_phone")),
            ))
        db.commit()
        print(f"  ✓ suppliers — {len(suppliers_df)} rows")

        items_df = read_csv("items.csv")
        for _, r in items_df.iterrows():
            daily_normal = float(clean(r.get("daily_consumption_normal"), 0) or 0)
            db.add(Item(
                item_id=r["item_id"],
                name=r["name"],
                category=r["category"],
                criticality=r["criticality"],
                unit=clean(r.get("unit"), UNIT_BY_CATEGORY.get(r["category"], "units")),
                disaster_surge_category=clean(r.get("disaster_surge_category"), "general"),
                typical_monthly_demand=int(clean(r.get("typical_monthly_demand"), daily_normal * 30) or 0),
            ))
        db.commit()
        print(f"  ✓ items — {len(items_df)} rows")

        item_lookup = items_df.set_index("item_id").to_dict("index")

        orders_df = read_csv("orders.csv")
        for _, r in orders_df.iterrows():
            db.add(Order(
                order_id=r["order_id"],
                item_id=r["item_id"],
                supplier_id=r["supplier_id"],
                quantity=int(r["quantity"]),
                order_date=parse_dt(r["order_date"]),
                expected_delivery_date=parse_date(r["expected_delivery_date"]),
                status=r["status"],
                is_emergency_order=parse_bool(r.get("is_emergency_order")),
                triggered_by_disaster_event_id=clean(r.get("triggered_by_disaster_event_id")),
            ))
        db.commit()
        print(f"  ✓ orders — {len(orders_df)} rows")

        for _, r in orders_df.iterrows():
            actual_date = parse_date(r.get("actual_delivery_date"))
            order_dt = parse_dt(r.get("order_date"))
            delay_days = clean(r.get("delay_days"))
            db.add(DeliveryHistory(
                delivery_id=str(uuid.uuid4()),
                order_id=r["order_id"],
                supplier_id=r["supplier_id"],
                item_id=r["item_id"],
                expected_date=parse_date(r["expected_delivery_date"]),
                actual_date=actual_date,
                delay_days=int(delay_days) if delay_days is not None else None,
                delay_reason=clean(r.get("delay_reason")),
                season="monsoon" if parse_bool(r.get("is_monsoon_season")) else get_season(order_dt),
            ))
        db.commit()
        print(f"  ✓ delivery_history — {len(orders_df)} rows")

        for idx, (_, r) in enumerate(orders_df.iterrows(), start=1):
            order_dt = parse_dt(r["order_date"])
            item = item_lookup.get(r["item_id"], {})
            unit_price = UNIT_PRICE_INR.get(item.get("category"), 100.0)
            status = "rejected" if r["status"] == "cancelled" else "approved"
            db.add(PurchaseOrder(
                po_id=str(uuid.uuid4()),
                po_number=f"PO-{order_dt.year}-{idx:05d}",
                order_id=r["order_id"],
                raised_by="Dataset Import",
                approved_by="Supply Chain Lead" if status == "approved" else None,
                approval_date=order_dt + timedelta(hours=6) if status == "approved" else None,
                approval_status=status,
                budget_code=f"HOSP-{order_dt.year}-Q{((order_dt.month - 1) // 3) + 1}",
                payment_terms="NET30",
                payment_status="paid" if status == "approved" else "pending",
                total_value_inr=round(int(r["quantity"]) * unit_price, 2),
            ))
        db.commit()
        print(f"  ✓ purchase_orders — {len(orders_df)} rows")

        purchase_orders = db.query(PurchaseOrder).all()
        po_by_order_id = {po.order_id: po for po in purchase_orders}
        grn_count = 0
        for _, r in orders_df.iterrows():
            if r["status"] != "delivered":
                continue
            po = po_by_order_id.get(r["order_id"])
            if not po:
                continue
            received_date = parse_dt(r.get("actual_delivery_date")) or parse_dt(r["expected_delivery_date"])
            ordered_qty = int(r["quantity"])
            rejected_qty = 0
            quality_status = "accepted"
            rejection_reason = None
            if clean(r.get("delay_reason")) == "stock_out":
                rejected_qty = max(1, int(ordered_qty * 0.05))
                quality_status = "partially_accepted"
                rejection_reason = "quantity_mismatch"
            db.add(GoodsReceiptNote(
                grn_id=str(uuid.uuid4()),
                grn_number=f"GRN-{received_date.year}-{grn_count + 1:05d}",
                order_id=r["order_id"],
                po_id=po.po_id,
                received_date=received_date,
                received_by="Warehouse Desk",
                inspected_by="Quality Desk",
                ordered_qty=ordered_qty,
                received_qty=ordered_qty,
                accepted_qty=ordered_qty - rejected_qty,
                rejected_qty=rejected_qty,
                quality_status=quality_status,
                rejection_reason=rejection_reason,
                added_to_inventory=True,
                batch_number=f"BATCH-{received_date.year}-{grn_count + 1:05d}",
                expiry_date=(received_date + timedelta(days=730)).date(),
            ))
            grn_count += 1
        db.commit()
        print(f"  ✓ goods_receipt_notes — {grn_count} rows")

        inventory_df = read_csv("inventory.csv")
        for _, r in inventory_df.iterrows():
            item = item_lookup.get(r["item_id"], {})
            db.add(Inventory(
                inventory_id=str(uuid.uuid4()),
                item_id=r["item_id"],
                current_stock=int(r["current_stock"]),
                reorder_level=int(r["reorder_level"]),
                max_capacity=int(r["max_capacity"]),
                daily_consumption_normal=float(clean(item.get("daily_consumption_normal"), 1.0)),
                daily_consumption_disaster=float(clean(item.get("daily_consumption_disaster"), 1.0)),
            ))
        db.commit()
        print(f"  ✓ inventory — {len(inventory_df)} rows")

        disaster_df = read_csv("disaster_events.csv")
        for _, r in disaster_df.iterrows():
            detected_at = parse_dt(r["event_date"])
            db.add(DisasterEvent(
                event_id=r["event_id"],
                source="dataset",
                external_event_id=r["event_id"],
                disaster_type=r["disaster_type"],
                severity=int(r["severity"]),
                location_name=f"{r['city']}, {r['state']}",
                lat=float(r["lat"]),
                lng=float(r["lng"]),
                affected_radius_km=int(round(float(r["radius_km"]))),
                detected_at=detected_at,
                is_active=not parse_bool(r["is_historical"]),
                raw_text=r["ai_summary"],
                ai_summary=r["ai_summary"],
            ))
            if parse_bool(r["is_historical"]):
                db.add(DisasterHistoryRecord(
                    hist_id=str(uuid.uuid4()),
                    disaster_type=r["disaster_type"],
                    severity=int(r["severity"]),
                    location_name=f"{r['city']}, {r['state']}",
                    year=detected_at.year,
                    items_most_affected=["medicine", "consumable", "surgical"],
                    avg_supply_delay_added_days=max(1.0, float(r["severity"]) * 1.5),
                    demand_multipliers={"general": float(r["surge_multiplier"])},
                    notes=r["ai_summary"],
                ))
        db.commit()
        print(f"  ✓ disaster_events — {len(disaster_df)} rows")

        facilities_path = DATA_DIR / "facilities.csv"
        if facilities_path.exists():
            facilities_df = pd.read_csv(facilities_path)
            print(f"  ✓ facilities — {len(facilities_df)} rows available for map/context data")

        print("\n✅ Database seeded successfully!\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the hospital supply-chain database.")
    parser.add_argument("--reset", action="store_true", help="Clear existing rows before importing datasets.")
    args = parser.parse_args()
    seed(reset=args.reset)
