from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# DATA
# ============================================================

DATA_DIR = BASE_DIR / "data"


# Current RailSync datasets
REQUEST_DATASET = (
    DATA_DIR
    / "railsync_department_requests_420.csv"
)

ASSET_DATASET = (
    DATA_DIR
    / "railsync_asset_master.csv"
)

TOPOLOGY_DATASET = (
    DATA_DIR
    / "railsync_railway_topology.csv"
)

STATION_DATASET = (
    DATA_DIR
    / "railsync_station_master.csv"
)

TRAIN_MOVEMENT_DATASET = (
    DATA_DIR
    / "railsync_train_movements_7day.csv"
)

BLOCK_AVAILABILITY_DATASET = (
    DATA_DIR
    / "railsync_weekly_block_availability.csv"
)

WORK_REQUIREMENTS_DATASET = (
    DATA_DIR
    / "railsync_work_requirements.csv"
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = (
    f"sqlite:///"
    f"{BASE_DIR / 'railsync.db'}"
)


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "RailSync AI"

APP_VERSION = "1.0.0"

APP_DESCRIPTION = (
    "AI-Powered Automatic Block Planning "
    "for Indian Railways"
)


# ============================================================
# API
# ============================================================

API_PREFIX = "/api"


# ============================================================
# CORS
# ============================================================

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]


# ============================================================
# OPTIMIZATION
# ============================================================

OPTIMIZER_MAX_TIME_SECONDS = 10