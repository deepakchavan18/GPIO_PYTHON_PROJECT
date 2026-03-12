import io
import json
import threading

import pandas as pd
from authlib.integrations.flask_client import OAuth
from flask import (Flask, jsonify, redirect, render_template,
                   request, send_file, session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

from config import Config
from database import get_connection, init_db
from models import User
from simulator import SimulatorThread

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# ── Flask-Login ───────────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to access the dashboard."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.before_first_request
def ensure_tables_exist():
    """Create database tables on first request (idempotent)."""
    try:
        init_db()
    except Exception as e:
        # Log to stderr; app will still try to serve the request.
        import sys, traceback
        print(f"[DB] init_db failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

# ── Google OAuth ──────────────────────────────────────────────────────────────
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ── Simulator singleton ───────────────────────────────────────────────────────
_sim_lock   = threading.Lock()
_sim_thread: SimulatorThread | None = None


def _get_sim_running() -> bool:
    return _sim_thread is not None and _sim_thread.is_alive()


# ═══════════════════════════════════════════════════════════════════════════════
#  Auth routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/auth/google")
def google_auth():
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def google_callback():
    """Handle Google OAuth callback and log any errors clearly."""
    try:
        token    = google.authorize_access_token()
        userinfo = token.get("userinfo")

        if not userinfo:
            raise RuntimeError("Google response missing userinfo; check OAuth scopes/config.")

        user = User.get_or_create(
            google_id=userinfo["sub"],
            email=userinfo["email"],
            name=userinfo["name"],
            picture=userinfo.get("picture", ""),
        )

        if not user or not user.is_active:
            return render_template(
                "login.html",
                error="Your account has been disabled. Contact an admin.",
            )

        login_user(user, remember=True)
        return redirect(url_for("dashboard"))

    except Exception as e:
        import traceback, sys
        traceback.print_exc(file=sys.stderr)
        return render_template(
            "login.html",
            error=f"Sign-in failed: {e}",
        ), 500


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ═══════════════════════════════════════════════════════════════════════════════
#  Main dashboard
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user,
                           sim_running=_get_sim_running())


# ═══════════════════════════════════════════════════════════════════════════════
#  Admin panel
# ═══════════════════════════════════════════════════════════════════════════════

def admin_required(fn):
    """Decorator: only admins may call this endpoint."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        if current_user.role != "admin":
            return jsonify({"error": "Forbidden – admins only"}), 403
        return fn(*args, **kwargs)
    return wrapper


@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    users = User.get_all()
    return render_template("admin.html", users=users, current_user=current_user)


@app.route("/api/admin/users/<int:uid>/toggle", methods=["POST"])
@login_required
@admin_required
def admin_toggle_user(uid):
    User.toggle_active(uid)
    return jsonify({"success": True})


@app.route("/api/admin/users/<int:uid>/role", methods=["POST"])
@login_required
@admin_required
def admin_change_role(uid):
    role = request.json.get("role")
    if role not in ("admin", "user"):
        return jsonify({"error": "Invalid role"}), 400
    if uid == current_user.id and role != "admin":
        return jsonify({"error": "Cannot demote yourself"}), 400
    User.change_role(uid, role)
    return jsonify({"success": True})


@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
@login_required
@admin_required
def admin_delete_user(uid):
    if uid == current_user.id:
        return jsonify({"error": "Cannot delete your own account"}), 400
    User.delete(uid)
    return jsonify({"success": True})


# ═══════════════════════════════════════════════════════════════════════════════
#  Sensor data API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/data")
@login_required
def get_data():
    try:
        limit  = min(int(request.args.get("limit", 50)), 500)
        device = request.args.get("device", "")

        db  = get_connection()
        cur = db.cursor()

        if device:
            cur.execute(
                "SELECT id, device_id, temperature, humidity, timestamp "
                "FROM readings WHERE device_id = %s "
                "ORDER BY timestamp DESC LIMIT %s",
                (device, limit),
            )
        else:
            cur.execute(
                "SELECT id, device_id, temperature, humidity, timestamp "
                "FROM readings ORDER BY timestamp DESC LIMIT %s",
                (limit,),
            )

        rows = cur.fetchall()
        cur.close(); db.close()

        return jsonify([{
            "id":          r[0],
            "device_id":   r[1],
            "temperature": r[2],
            "humidity":    r[3],
            "timestamp":   str(r[4]),
        } for r in rows])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
@login_required
def get_stats():
    """Return aggregate stats per device for the chart."""
    try:
        db  = get_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT device_id,
                   ROUND(AVG(temperature), 2),
                   ROUND(MIN(temperature), 2),
                   ROUND(MAX(temperature), 2),
                   ROUND(AVG(humidity), 2),
                   COUNT(*)
            FROM readings
            GROUP BY device_id
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return jsonify([{
            "device":       r[0],
            "avg_temp":     r[1],
            "min_temp":     r[2],
            "max_temp":     r[3],
            "avg_humidity": r[4],
            "count":        r[5],
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  Simulator control
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/simulator/start", methods=["POST"])
@login_required
def start_simulator():
    global _sim_thread
    with _sim_lock:
        if _get_sim_running():
            return jsonify({"status": "already_running"})
        _sim_thread = SimulatorThread()
        _sim_thread.start()
    return jsonify({"status": "started"})


@app.route("/api/simulator/stop", methods=["POST"])
@login_required
def stop_simulator():
    global _sim_thread
    with _sim_lock:
        if _sim_thread and _sim_thread.is_alive():
            _sim_thread.stop()
            _sim_thread = None
    return jsonify({"status": "stopped"})


@app.route("/api/simulator/status")
@login_required
def simulator_status():
    return jsonify({"running": _get_sim_running()})


# ═══════════════════════════════════════════════════════════════════════════════
#  Download
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/download/<fmt>")
@login_required
def download_data(fmt):
    try:
        db  = get_connection()
        cur = db.cursor()
        cur.execute("SELECT id, device_id, temperature, humidity, timestamp "
                    "FROM readings ORDER BY timestamp DESC")
        rows = cur.fetchall()
        cur.close(); db.close()

        data = [{
            "id": r[0], "device_id": r[1],
            "temperature": r[2], "humidity": r[3],
            "timestamp": str(r[4]),
        } for r in rows]

        if fmt == "json":
            buf = io.BytesIO(json.dumps(data, indent=2).encode())
            return send_file(buf, mimetype="application/json",
                             as_attachment=True, download_name="sensor_data.json")

        df = pd.DataFrame(data)

        if fmt == "csv":
            buf = io.BytesIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            return send_file(buf, mimetype="text/csv",
                             as_attachment=True, download_name="sensor_data.csv")

        if fmt == "excel":
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sensor Data")
            buf.seek(0)
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return send_file(buf, mimetype=mime,
                             as_attachment=True, download_name="sensor_data.xlsx")

        return jsonify({"error": "Unknown format. Use json, csv, or excel."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    app.run(debug=(Config.FLASK_ENV == "development"), port=5001)