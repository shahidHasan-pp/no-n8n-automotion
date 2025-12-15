"""
Background worker for Telegram bot polling
Can be run as a separate process or integrated with Celery
"""

import time
import signal
import sys
from typing import Optional

from app.database.session import SessionLocal
from app.services.messaging.telegram_bot import telegram_bot_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramPollingWorker:
    """
    Background worker that polls Telegram for updates
    """
    
    def __init__(self, poll_interval: int = 5):
        """
        Args:
            poll_interval: Seconds to wait between polls (default: 5)
        """
        self.poll_interval = poll_interval
        self.running = False
        
    def start(self):
        """Start the polling worker"""
        self.running = True
        logger.info("[Telegram Worker] Starting polling worker...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        while self.running:
            try:
                with SessionLocal() as db:
                    count = telegram_bot_service.process_updates(db)
                    if count > 0:
                        logger.info(f"[Telegram Worker] Processed {count} updates")
                    
                # Wait before next poll
                time.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                logger.info("[Telegram Worker] Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"[Telegram Worker] Error in polling loop: {e}")
                time.sleep(self.poll_interval)
        
        logger.info("[Telegram Worker] Polling worker stopped")
    
    def stop(self):
        """Stop the polling worker"""
        logger.info("[Telegram Worker] Stopping polling worker...")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"[Telegram Worker] Received signal {signum}")
        self.stop()
        sys.exit(0)


def run_polling_worker(poll_interval: int = 5):
    """
    Run the Telegram polling worker
    
    Usage:
        python -m app.workers.telegram_polling
    
    Args:
        poll_interval: Seconds between polls
    """
    worker = TelegramPollingWorker(poll_interval=poll_interval)
    
    try:
        worker.start()
    except Exception as e:
        logger.error(f"[Telegram Worker] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram Bot Polling Worker")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Polling interval in seconds (default: 5)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"[Telegram Worker] Starting with interval: {args.interval}s")
    run_polling_worker(poll_interval=args.interval)
