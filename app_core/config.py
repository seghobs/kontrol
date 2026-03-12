import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "app.db")

# Legacy JSON paths (only for one-time migration)
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
EXEMPTIONS_FILE = os.path.join(BASE_DIR, "exemptions.json")

ADMIN_PASSWORD = "seho"
SECRET_KEY = "seho_admin_panel_secret_key_2024"

IG_APP_ID = "567067343352427"
