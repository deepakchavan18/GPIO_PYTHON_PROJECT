<div align="center">



# 🌡️ GPIO — Real-Time Sensor Dashboard

**A lightweight IoT monitoring system that collects, stores, and visualizes live temperature & humidity data from simulated GPIO sensors.**

[![CI](https://github.com/vishnugi/new_gpio/actions/workflows/ci.yml/badge.svg)](https://github.com/vishnugi/new_gpio/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

[Live Demo](#) · [Report Bug](https://github.com/vishnugi/new_gpio/issues) · [Request Feature](https://github.com/vishnugi/new_gpio/issues)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Screenshots](#-screenshots)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Running the App](#running-the-app)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

**GPIO** is a full-stack IoT sensor monitoring application that simulates real-world temperature and humidity sensors. It continuously generates sensor data, persists it to a MySQL database, and streams it to a live web dashboard — refreshing every 5 seconds automatically.

> Designed to mirror real Raspberry Pi / GPIO sensor pipelines, this project is ideal for learning IoT backend architectures, data simulation, and real-time web dashboards.

---

## ✨ Features

- 🔄 **Real-Time Data Streaming** — Dashboard auto-refreshes every 5 seconds
- 🌡️ **Multi-Device Simulation** — Simulates 3 independent sensor devices
- ⚠️ **Fault Tolerance** — 10% sensor failure simulation with graceful error handling
- 🗄️ **MySQL Persistence** — All readings stored with timestamps
- 📝 **Rotating Log Files** — Log rotation at 5MB with 3 backups
- 🧪 **Full Test Suite** — Unit tests with mocking + integration tests
- ⚙️ **CI/CD Ready** — GitHub Actions pipeline across Python 3.10, 3.11, 3.12
- 🔐 **Env-Based Config** — Secrets managed via `.env` (never committed)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square) **Language** | Python 3.10+ |
| ![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white&style=flat-square) **Web Framework** | Flask 2.x |
| ![MySQL](https://img.shields.io/badge/-MySQL-4479A1?logo=mysql&logoColor=white&style=flat-square) **Database** | MySQL 8.0 |
| ![GitHub Actions](https://img.shields.io/badge/-GitHub_Actions-2088FF?logo=githubactions&logoColor=white&style=flat-square) **CI/CD** | GitHub Actions |
| ![pytest](https://img.shields.io/badge/-pytest-0A9EDC?logo=pytest&logoColor=white&style=flat-square) **Testing** | pytest + pytest-cov |
| ![dotenv](https://img.shields.io/badge/-.env-ECD53F?logo=dotenv&logoColor=black&style=flat-square) **Config** | python-dotenv |
| ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5&logoColor=white&style=flat-square) **Frontend** | HTML5 + Vanilla JS |

---

## 🏗️ Architecture & Workflow

| Architecture |

```
┌─────────────────────────────────────────────────────────┐
│                       GPIO System                       │
│                                                         │
│  ┌──────────────┐    INSERT     ┌──────────────────┐    │
│  │  simulator.py │ ──────────►  │   MySQL Database  │   │
│  │  (3 devices)  │              │   (readings table)│   │
│  └──────────────┘              └────────┬─────────┘     │
│                                          │ SELECT       │
│  ┌──────────────────────────────────┐   │               │
│  │           Flask App (app.py)      │ ◄─┘              │
│  │  GET /         → dashboard.html  │                   │
│  │  GET /api/data → JSON response   │                   │
│  └────────────────┬─────────────────┘                   │
│                   │ HTTP fetch (every 5s)               │
│  ┌────────────────▼─────────────────┐                   │
│  │       Browser Dashboard           │                  │
│  │    Live updating HTML table       │                  │
│  └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```
| Workflow |
| ![Workflow](https://i.ibb.co/HJW4VYB/Untitled-design.gif) |
---

## 📸 Screenshots

> **Add your screenshots here after running the app!**

| Dashboard View |
|:---:|
| ![Dashboard](https://i.ibb.co/xq8Yq42y/Whats-App-Image-2026-03-04-at-4-42-04-PM.jpg) |

*Live auto-refreshing table showing device ID, temperature, humidity, and timestamp.*

---

## 🚀 Getting Started

### Prerequisites

Make sure the following are installed on your machine:

- ![Python](https://img.shields.io/badge/-Python_3.10+-3776AB?logo=python&logoColor=white&style=flat-square) [Python 3.10+](https://www.python.org/downloads/)
- ![MySQL](https://img.shields.io/badge/-MySQL_8.0-4479A1?logo=mysql&logoColor=white&style=flat-square) [MySQL 8.0](https://dev.mysql.com/downloads/)
- ![Git](https://img.shields.io/badge/-Git-F05032?logo=git&logoColor=white&style=flat-square) [Git](https://git-scm.com/)
- `pip` (comes with Python)

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/vishnugi/new_gpio.git
cd new_gpio
```

**2. Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up your environment variables**

Create a `.env` file in the project root:

```bash
cp .env.example .env   # if .env.example exists
# OR manually create .env
```

Edit `.env` with your credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=sensor_db
FLASK_ENV=development
```

> ⚠️ **Never commit `.env` to version control.** It is already listed in `.gitignore`.

---

### Database Setup

**1. Log into MySQL**

```bash
mysql -u root -p
```

**2. Create the database and table**

```sql
CREATE DATABASE sensor_db;
USE sensor_db;

CREATE TABLE readings (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50)    NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity    DECIMAL(5,2) NOT NULL,
    timestamp   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
```

**3. Verify the table was created**

```sql
SHOW TABLES;
DESCRIBE readings;
```

---

### Running the App

You need **two terminal windows** — one for the simulator, one for the Flask server.

**Terminal 1 — Start the Sensor Simulator**

```bash
python simulator.py
```

Expected output:
```
Simulator Started... Press CTRL+C to stop.
Saved: device_2 28.34 61.45
Saved: device_1 22.10 75.88
...
```

**Terminal 2 — Start the Flask Web Server**

```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

**Open the dashboard**

Navigate to **[http://localhost:5001](http://localhost:5001)** in your browser. The table refreshes automatically every 5 seconds. 🎉

---

## 📁 Project Structure

```
new_gpio/
│
├── app.py                  # Flask web application & API routes
├── simulator.py            # Sensor data generator (runs independently)
├── database.py             # MySQL connection helper
├── config.py               # Loads environment variables via dotenv
│
├── templates/
│   └── dashboard.html      # Frontend — auto-refreshing sensor table
│
├── tests/
│   ├── test_app.py         # Unit tests for Flask routes (mocked DB)
│   └── test_database.py    # Integration test for DB connection
│
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
│
├── .env                    # 🔒 Local secrets (git-ignored)
├── .gitignore              # Ignored files
├── requirements.txt        # Python dependencies
└── sensor.log              # Rotating log file (git-ignored)
```

---

## 📡 API Reference

### `GET /`
Returns the dashboard HTML page.

| Response | Type | Description |
|---|---|---|
| `200 OK` | `text/html` | Renders `dashboard.html` |

---

### `GET /api/data`
Returns the latest 20 sensor readings as JSON.

| Response | Type | Description |
|---|---|---|
| `200 OK` | `application/json` | Array of reading objects |
| `500 Internal Server Error` | `application/json` | `{ "error": "..." }` |

**Example Response:**

```json
[
  {
    "id": 42,
    "device_id": "device_1",
    "temperature": 25.34,
    "humidity": 61.20,
    "timestamp": "2026-03-03 12:52:17"
  },
  ...
]
```

---

## 🧪 Testing

Run the full test suite with coverage:

```bash
pytest -v --cov=. --cov-report=term-missing
```

Run only unit tests (no DB required):

```bash
pytest tests/test_app.py -v
```

Run integration test (requires MySQL running):

```bash
pytest tests/test_database.py -v
```

**Test coverage includes:**

| Test | Description |
|---|---|
| `test_home_route` | Verifies `/` returns HTTP 200 |
| `test_api_data` | Mocks DB and verifies `/api/data` response |
| `test_db_failure` | Verifies graceful 500 on DB failure |
| `test_db_connection` | Live MySQL connection integration test |

---

## ⚙️ CI/CD Pipeline

The project uses **GitHub Actions** for continuous integration.

**Triggers:** Every `push` and `pull_request`

**Matrix:** Python `3.10`, `3.11`, `3.12`

**Pipeline Steps:**

```
1. ✅ Checkout code
2. 🐍 Set up Python (matrix versions)
3. 📦 Install dependencies from requirements.txt
4. 🗄️  Spin up MySQL 8.0 service container
5. ⏳ Wait for MySQL to be ready (health check)
6. 🧪 Run pytest with coverage report
```

View live pipeline status → [GitHub Actions](https://github.com/vishnugi/new_gpio/actions)

---

## 🔧 Configuration

All configuration is driven by environment variables loaded from `.env`:

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL host address |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | _(required)_ | MySQL password |
| `DB_NAME` | `sensor_db` | Target database name |
| `FLASK_ENV` | `development` | Flask environment mode |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
# 1. Fork the repo and clone it
git clone https://github.com/your-username/new_gpio.git

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and run tests
pytest -v

# 4. Commit and push
git commit -m "feat: add your feature"
git push origin feature/your-feature-name

# 5. Open a Pull Request on GitHub
```

Please make sure all tests pass before opening a PR.

---

## 📄 License

This project is made for the Educational Purpose , For any query Contact...!

---

<div align="center">

Made by [Vishnu Priya](https://github.com/vishnugi) & [Deepak Chavan](https://github.com/deepakchavan18) 

⭐ Star this repo if you found it useful!

</div>
