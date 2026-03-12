from database import get_connection


def test_db_connection():
    conn = get_connection()
    assert conn is not None
    conn.close()
