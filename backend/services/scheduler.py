"""APScheduler job definitions."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

import asyncio
from backend.database import SessionLocal
from backend.routers.predictions import _recheck_orders_task
from backend.routers.disaster import _poll_and_process_disasters

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def poll_disaster_apis():
    """Poll GDACS + ReliefWeb + NewsAPI for new disaster events (Phase 4)."""
    logger.info("Polling disaster APIs...")
    db = SessionLocal()
    try:
        # Run the async function synchronously inside the scheduler thread
        added = asyncio.run(_poll_and_process_disasters(db))
        logger.info(f"Disaster polling complete. {added} new events added.")
    except Exception as e:
        logger.error(f"Error polling disaster APIs: {e}")
    finally:
        db.close()


def recheck_all_pending_orders():
    """Re-run AI delay prediction on all pending/in_transit orders (Phase 3)."""
    logger.info("Rechecking pending orders via AI module...")
    db = SessionLocal()
    try:
        _recheck_orders_task(db)
    except Exception as e:
        logger.error(f"Error rechecking pending orders: {e}")
    finally:
        db.close()

def refresh_disaster_predictions():
    """Refresh predictions for active disaster (Phase 3)."""
    logger.info("Refreshing disaster predictions... (stub — AI module pending Phase 3)")


def start_scheduler():
    """Register jobs and start the background scheduler."""
    scheduler.add_job(poll_disaster_apis, "interval", minutes=15, id="poll_disaster")
    scheduler.add_job(recheck_all_pending_orders, "interval", hours=24, id="recheck_orders")
    scheduler.add_job(refresh_disaster_predictions, "interval", hours=1, id="refresh_preds")
    scheduler.start()
    logger.info("APScheduler started with 3 jobs")


def stop_scheduler():
    scheduler.shutdown(wait=False)
