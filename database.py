import mysql.connector
from config import Config


def get_connection():
    """Return a new MySQL connection."""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=False,
        )
        return connection
    except mysql.connector.Error as err:
        print(f"[DB] Connection error: {err}")
        raise


def init_db():
    """Create tables if they don't already exist."""
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            device_id  VARCHAR(50)   NOT NULL,
            temperature FLOAT        NOT NULL,
            humidity    FLOAT        NOT NULL,
            timestamp   DATETIME     DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_timestamp (timestamp)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            google_id  VARCHAR(100)  UNIQUE NOT NULL,
            email      VARCHAR(200)  UNIQUE NOT NULL,
            name       VARCHAR(200)  NOT NULL,
            picture    VARCHAR(500)  DEFAULT '',
            role       ENUM('admin','user') DEFAULT 'user',
            is_active  BOOLEAN       DEFAULT TRUE,
            created_at DATETIME      DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    cursor.close()
    db.close()
    print("[DB] Tables initialised.")