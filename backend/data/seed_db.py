"""Seed the SQLite database from generated CSV files."""
import sys
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import engine, SessionLocal, Base
from backend.models import (
    Supplier, Item, Order, PurchaseOrder, GoodsReceiptNote,
    Inventory, DeliveryHistory, DisasterHistoryRecord,
)

DATA_DIR = PROJECT_ROOT / "data_output"


def parse_dt(val):
    if pd.isna(val) or val is None or val == "None":
        return None
    return datetime.fromisoformat(str(val))


def parse_date(val):
    if pd.isna(val) or val is None or val == "None":
        return None
    return datetime.fromisoformat(str(val)).date() if "T" in str(val) else datetime.strptime(str(val), "%Y-%m-%d").date()


def seed():
    print("\n━━━ Seeding Database ━━━\n")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Suppliers
        df = pd.read_csv(DATA_DIR / "suppliers.csv")
        for _, r in df.iterrows():
            db.add(Supplier(
                supplier_id=r["supplier_id"], name=r["name"], city=r["city"], state=r["state"],
                lat=r["lat"], lng=r["lng"], reliability_score=r["reliability_score"],
                avg_lead_days=int(r["avg_lead_days"]),
                supply_categories=json.loads(r["supply_categories"]) if isinstance(r["supply_categories"], str) else r["supply_categories"],
                is_emergency_certified=bool(r["is_emergency_certified"]),
                is_govt_reserve=bool(r["is_govt_reserve"]),
                contact_email=r.get("contact_email"), contact_phone=r.get("contact_phone"),
            ))
        db.commit()
        print(f"  ✓ suppliers — {len(df)} rows")

        # 2. Items
        df = pd.read_csv(DATA_DIR / "items.csv")
        for _, r in df.iterrows():
            db.add(Item(
                item_id=r["item_id"], name=r["name"], category=r["category"],
                criticality=r["criticality"], unit=r["unit"],
                disaster_surge_category=r.get("disaster_surge_category"),
                typical_monthly_demand=int(r["typical_monthly_demand"]) if pd.notna(r.get("typical_monthly_demand")) else None,
            ))
        db.commit()
        print(f"  ✓ items — {len(df)} rows")

        # 3. Orders
        df = pd.read_csv(DATA_DIR / "orders.csv")
        for _, r in df.iterrows():
            db.add(Order(
                order_id=r["order_id"], item_id=r["item_id"], supplier_id=r["supplier_id"],
                quantity=int(r["quantity"]), order_date=parse_dt(r["order_date"]),
                expected_delivery_date=parse_date(r["expected_delivery_date"]),
                status=r["status"], is_emergency_order=bool(r.get("is_emergency_order", False)),
                triggered_by_disaster_event_id=None,
            ))
        db.commit()
        print(f"  ✓ orders — {len(df)} rows")

        # 4. Delivery History
        df = pd.read_csv(DATA_DIR / "delivery_history.csv")
        for _, r in df.iterrows():
            db.add(DeliveryHistory(
                delivery_id=r["delivery_id"], order_id=r["order_id"],
                supplier_id=r["supplier_id"], item_id=r["item_id"],
                expected_date=parse_date(r["expected_date"]),
                actual_date=parse_date(r.get("actual_date")),
                delay_days=int(r["delay_days"]) if pd.notna(r.get("delay_days")) else None,
                delay_reason=r.get("delay_reason") if pd.notna(r.get("delay_reason")) else None,
                season=r.get("season"),
            ))
        db.commit()
        print(f"  ✓ delivery_history — {len(df)} rows")

        # 5. Purchase Orders
        df = pd.read_csv(DATA_DIR / "purchase_orders.csv")
        for _, r in df.iterrows():
            db.add(PurchaseOrder(
                po_id=r["po_id"], po_number=r["po_number"], order_id=r["order_id"],
                raised_by=r["raised_by"],
                approved_by=r.get("approved_by") if pd.notna(r.get("approved_by")) else None,
                approval_date=parse_dt(r.get("approval_date")),
                approval_status=r["approval_status"], budget_code=r["budget_code"],
                payment_terms=r["payment_terms"], payment_status=r["payment_status"],
                total_value_inr=float(r["total_value_inr"]),
            ))
        db.commit()
        print(f"  ✓ purchase_orders — {len(df)} rows")

        # 6. GRNs
        df = pd.read_csv(DATA_DIR / "goods_receipt_notes.csv")
        for _, r in df.iterrows():
            db.add(GoodsReceiptNote(
                grn_id=r["grn_id"], grn_number=r["grn_number"],
                order_id=r["order_id"], po_id=r["po_id"],
                received_date=parse_dt(r["received_date"]),
                received_by=r["received_by"], inspected_by=r["inspected_by"],
                ordered_qty=int(r["ordered_qty"]), received_qty=int(r["received_qty"]),
                accepted_qty=int(r["accepted_qty"]), rejected_qty=int(r["rejected_qty"]),
                quality_status=r["quality_status"],
                rejection_reason=r.get("rejection_reason") if pd.notna(r.get("rejection_reason")) else None,
                added_to_inventory=bool(r.get("added_to_inventory", False)),
                batch_number=r.get("batch_number"),
                expiry_date=parse_date(r.get("expiry_date")),
            ))
        db.commit()
        print(f"  ✓ goods_receipt_notes — {len(df)} rows")

        # 7. Inventory
        df = pd.read_csv(DATA_DIR / "inventory.csv")
        for _, r in df.iterrows():
            db.add(Inventory(
                inventory_id=r["inventory_id"], item_id=r["item_id"],
                current_stock=int(r["current_stock"]), reorder_level=int(r["reorder_level"]),
                max_capacity=int(r["max_capacity"]),
                daily_consumption_normal=float(r["daily_consumption_normal"]),
                daily_consumption_disaster=float(r["daily_consumption_disaster"]),
            ))
        db.commit()
        print(f"  ✓ inventory — {len(df)} rows")

        # 8. Disaster History
        df = pd.read_csv(DATA_DIR / "disaster_history.csv")
        for _, r in df.iterrows():
            db.add(DisasterHistoryRecord(
                hist_id=r["hist_id"], disaster_type=r["disaster_type"],
                severity=int(r["severity"]), location_name=r["location_name"],
                year=int(r["year"]),
                items_most_affected=json.loads(r["items_most_affected"]) if isinstance(r["items_most_affected"], str) else r["items_most_affected"],
                avg_supply_delay_added_days=float(r["avg_supply_delay_added_days"]) if pd.notna(r.get("avg_supply_delay_added_days")) else None,
                demand_multipliers=json.loads(r["demand_multipliers"]) if isinstance(r["demand_multipliers"], str) else r["demand_multipliers"],
                notes=r.get("notes"),
            ))
        db.commit()
        print(f"  ✓ disaster_history — {len(df)} rows")

        print("\n✅ Database seeded successfully!\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
