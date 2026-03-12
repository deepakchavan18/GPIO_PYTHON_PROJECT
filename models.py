from flask_login import UserMixin
from database import get_connection


class User(UserMixin):
    """Represents an authenticated user stored in MySQL."""

    def __init__(self, id, google_id, email, name, picture, role, is_active, created_at=None):
        self.id         = id
        self.google_id  = google_id
        self.email      = email
        self.name       = name
        self.picture    = picture
        self.role       = role
        # Flask-Login's UserMixin defines `is_active` as a property; keep the DB
        # value in a separate attribute and expose it via a property below.
        self._is_active = bool(is_active)
        self.created_at = created_at

    # ── Flask-Login required ──────────────────────────────────────────────────
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self._is_active

    # ── Queries ───────────────────────────────────────────────────────────────
    @staticmethod
    def _row_to_user(row):
        if row is None:
            return None
        return User(*row)

    @staticmethod
    def get_by_id(user_id):
        db = get_connection()
        cur = db.cursor()
        cur.execute("SELECT id, google_id, email, name, picture, role, is_active, created_at "
                    "FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close(); db.close()
        return User._row_to_user(row)

    @staticmethod
    def get_or_create(google_id, email, name, picture):
        """Return existing user or create a new one. First-ever user becomes admin."""
        db = get_connection()
        cur = db.cursor()

        cur.execute("SELECT id, google_id, email, name, picture, role, is_active, created_at "
                    "FROM users WHERE google_id = %s", (google_id,))
        row = cur.fetchone()

        if row:
            # Update name/picture in case they changed on Google side
            cur.execute("UPDATE users SET name=%s, picture=%s WHERE id=%s",
                        (name, picture, row[0]))
            db.commit()
            cur.close(); db.close()
            return User._row_to_user(row)

        # First user → admin
        cur.execute("SELECT COUNT(*) FROM users")
        is_first = cur.fetchone()[0] == 0
        role = 'admin' if is_first else 'user'

        cur.execute(
            "INSERT INTO users (google_id, email, name, picture, role) "
            "VALUES (%s, %s, %s, %s, %s)",
            (google_id, email, name, picture, role)
        )
        db.commit()
        user_id = cur.lastrowid
        cur.close(); db.close()
        return User(user_id, google_id, email, name, picture, role, True)

    @staticmethod
    def get_all():
        db = get_connection()
        cur = db.cursor()
        cur.execute("SELECT id, google_id, email, name, picture, role, is_active, created_at "
                    "FROM users ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close(); db.close()
        return [User._row_to_user(r) for r in rows]

    @staticmethod
    def toggle_active(user_id):
        db = get_connection()
        cur = db.cursor()
        cur.execute("UPDATE users SET is_active = NOT is_active WHERE id = %s", (user_id,))
        db.commit()
        cur.close(); db.close()

    @staticmethod
    def change_role(user_id, role):
        db = get_connection()
        cur = db.cursor()
        cur.execute("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
        db.commit()
        cur.close(); db.close()

    @staticmethod
    def delete(user_id):
        db = get_connection()
        cur = db.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        cur.close(); db.close()