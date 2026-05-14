"""APScheduler job definitions."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def poll_disaster_apis():
    """Poll GDACS + ReliefWeb + NewsAPI for new disaster events (Phase 4)."""
    logger.info("Polling disaster APIs... (stub — External APIs pending Phase 4)")


def recheck_all_pending_orders():
    """Re-run AI delay prediction on all pending/in_transit orders (Phase 3)."""
    logger.info("Rechecking pending orders... (stub — AI module pending Phase 3)")


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
