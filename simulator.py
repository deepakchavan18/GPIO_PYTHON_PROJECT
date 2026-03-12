import random
import threading
import logging
from logging.handlers import RotatingFileHandler
from database import get_connection
from config import Config

# ── Logging ───────────────────────────────────────────────────────────────────
_handler = RotatingFileHandler("sensor.log", maxBytes=5_000_000, backupCount=3)
logging.basicConfig(
    handlers=[_handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("simulator")

DEVICES = ["device_1", "device_2", "device_3"]


class SimulatorThread(threading.Thread):
    """
    Background thread that writes sensor readings to MySQL.
    Stop gracefully via .stop() — the thread will exit within SIMULATOR_DELAY seconds.
    """

    def __init__(self):
        super().__init__(name="SimulatorThread", daemon=True)
        self._stop_event = threading.Event()

    # ── Public API ─────────────────────────────────────────────────────────────
    def stop(self):
        """Signal the thread to stop at the next opportunity."""
        self._stop_event.set()

    @property
    def is_stopped(self):
        return self._stop_event.is_set()

    # ── Private ────────────────────────────────────────────────────────────────
    def run(self):
        db = cursor = None
        try:
            db = get_connection()
            cursor = db.cursor()
            logger.info("Simulator started.")

            while not self._stop_event.is_set():
                device_id = random.choice(DEVICES)
                try:
                    temperature, humidity = self._read_sensor()
                    self._cleanup_old_readings(cursor, db)
                    cursor.execute(
                        "INSERT INTO readings (device_id, temperature, humidity) "
                        "VALUES (%s, %s, %s)",
                        (device_id, temperature, humidity),
                    )
                    db.commit()
                    logger.info(f"{device_id} → {temperature}°C  {humidity}%")

                except Exception as sensor_err:
                    logger.error(f"{device_id} sensor error: {sensor_err}")

                # Wait for delay, but wake up immediately if stop is requested
                self._stop_event.wait(Config.SIMULATOR_DELAY)

        except Exception as db_err:
            logger.error(f"Simulator DB error: {db_err}")

        finally:
            if cursor:
                try: cursor.close()
                except Exception: pass
            if db:
                try: db.close()
                except Exception: pass
            logger.info("Simulator stopped cleanly.")

    @staticmethod
    def _read_sensor():
        """Simulate a sensor reading; 10 % chance of failure."""
        if random.random() < 0.1:
            raise RuntimeError("Sensor not responding")
        return (
            round(random.uniform(20, 35), 2),
            round(random.uniform(40, 80), 2),
        )

    @staticmethod
    def _cleanup_old_readings(cursor, db):
        """Delete oldest rows so the table never exceeds MAX_READINGS."""
        cursor.execute("SELECT COUNT(*) FROM readings")
        count = cursor.fetchone()[0]
        if count >= Config.MAX_READINGS:
            excess = count - Config.MAX_READINGS + 1
            cursor.execute(
                "DELETE FROM readings ORDER BY timestamp ASC LIMIT %s", (excess,)
            )
            db.commit()
            logger.info(f"Cleaned up {excess} old reading(s). Table size: {count - excess}")