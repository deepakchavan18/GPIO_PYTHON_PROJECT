import psycopg
from config import Config


def get_connection():
    """Return a new PostgreSQL connection."""
    try:
        conn = psycopg.connect(
            host=Config.DB_HOST,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
        )
        return conn
    except psycopg.Error as err:
        print(f"[DB] Connection error: {err}")
        raise


def init_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id          SERIAL PRIMARY KEY,
            device_id   VARCHAR(50)   NOT NULL,
            temperature DOUBLE PRECISION NOT NULL,
            humidity    DOUBLE PRECISION NOT NULL,
            timestamp   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         SERIAL PRIMARY KEY,
            google_id  VARCHAR(100)  UNIQUE NOT NULL,
            email      VARCHAR(200)  UNIQUE NOT NULL,
            name       VARCHAR(200)  NOT NULL,
            picture    VARCHAR(500)  DEFAULT '',
            role       VARCHAR(10)   DEFAULT 'user',
            is_active  BOOLEAN       DEFAULT TRUE,
            created_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Helpful index for queries ordered by timestamp
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_readings_timestamp
        ON readings (timestamp)
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("[DB] Tables initialised.")