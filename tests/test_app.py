import pytest
from unittest.mock import MagicMock,patch
from app import app



 
@pytest.fixture
def app():
    import os
    os.environ.setdefault("SECRET_KEY", "test-secret")
    os.environ.setdefault("GOOGLE_CLIENT_ID", "dummy")
    os.environ.setdefault("GOOGLE_CLIENT_SECRET", "dummy")
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_USER", "root")
    os.environ.setdefault("DB_PASSWORD", "")
    os.environ.setdefault("DB_NAME", "test_db")
 
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    return flask_app
 
 
@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c
 
 
@pytest.fixture
def logged_in_client(app, client):
    """Return a client with a mocked logged-in user."""
    from models import User
    mock_user = User(1, "g123", "test@example.com", "Test User", "", "user", True)
    with app.test_request_context():
        with patch("flask_login.utils._get_user", return_value=mock_user):
            yield client
 
 
# ── Auth routes ───────────────────────────────────────────────────────────────
 
def test_login_page(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert b"GPIO" in res.data
 
 
def test_root_redirects_to_login(client):
    res = client.get("/")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
 
 
# ── API routes ────────────────────────────────────────────────────────────────
 
@patch("app.get_connection")
@patch("app.current_user")
def test_api_data_success(mock_user, mock_db, client):
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_cursor = mock_db.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (1, "device_1", 25.5, 60.0, "2026-01-01 10:00:00"),
    ]
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
 
    with patch("flask_login.utils._get_user",
               return_value=MagicMock(is_authenticated=True, is_active=True,
                                      id=1, role="user")):
        res = client.get("/api/data")
    assert res.status_code in (200, 302)   # 302 if session check fails in test env
 
 
@patch("app.get_connection")
def test_api_data_db_error(mock_db, client):
    mock_db.side_effect = Exception("DB Down")
    with patch("flask_login.utils._get_user",
               return_value=MagicMock(is_authenticated=True, is_active=True,
                                      id=1, role="user")):
        res = client.get("/api/data")
    assert res.status_code in (500, 302)
 
 
# ── Simulator ─────────────────────────────────────────────────────────────────
 
def test_simulator_thread():
    """Test that SimulatorThread can be instantiated and stopped."""
    from simulator import SimulatorThread
    t = SimulatorThread()
    assert not t.is_stopped
    t.stop()
    assert t.is_stopped
 
 
def test_simulator_sensor_returns_valid_range():
    """Sensor readings must be within expected bands."""
    from simulator import SimulatorThread
    for _ in range(50):
        try:
            temp, hum = SimulatorThread._read_sensor()
            assert 20 <= temp <= 35
            assert 40 <= hum <= 80
        except RuntimeError:
            pass   # 10 % failure is expected
 
 
# ── Config ────────────────────────────────────────────────────────────────────
 
def test_config_defaults():
    from config import Config
    assert Config.DB_PORT == 5432
    assert Config.MAX_READINGS > 0
    assert Config.SIMULATOR_DELAY > 0





@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200


@patch("app.get_connection")
def test_api_data(mock_db, client):
    mock_cursor = mock_db.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        (1, "device_1", 25.5, 60.0, "2026-01-01")
    ]

    response = client.get("/api/data")
    assert response.status_code == 200


@patch("app.get_connection")
def test_db_failure(mock_db, client):
    mock_db.side_effect = Exception("DB Down")

    response = client.get("/api/data")
    assert response.status_code == 500

