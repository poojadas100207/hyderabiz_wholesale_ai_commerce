"""Configuration settings for the Autonomous E-Commerce Shopping Concierge Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

# Model Configuration
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

# Data & Persistence Paths
DATA_DIR = BASE_DIR / "data"
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db")))
PRICE_ALERTS_FILE = DATA_DIR / "price_alerts.json"
USER_PROFILES_FILE = DATA_DIR / "user_profiles.json"
CART_FILE = DATA_DIR / "user_cart.json"

# Ensure essential directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)


def get_api_key() -> str:
    """Return the active Gemini API key from environment or config."""
    global GEMINI_API_KEY
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    return GEMINI_API_KEY


def set_api_key(api_key: str, persist_to_env: bool = False):
    """Set or update the Gemini API key dynamically."""
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key.strip()
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

    if persist_to_env:
        env_path = BASE_DIR / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={GEMINI_API_KEY}\n")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"GEMINI_API_KEY={GEMINI_API_KEY}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
