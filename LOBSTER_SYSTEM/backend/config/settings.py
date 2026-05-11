# 檔案路徑：backend/config/settings.py
import os
from dotenv import load_dotenv

# 定義基礎路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 自動載入 .env 設定
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# --- 1. AI 服務設定 ---
raw_keys = os.getenv("GEMINI_API_KEYS", "")
GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# 🌟 就是少了這一行！鎖定 Gemini 3 Flash
CURRENT_MODEL = "gemini-3.1-flash-lite-preview" 

# --- 2. 通訊接口設定 ---
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# --- 3. 伺服器基礎設定 ---
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

# --- 4. 資料庫路徑設定 ---
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'orders.db')}"

# --- 5. 物流與分帳參數 ---
DEFAULT_DELIVERY_FEE = float(os.getenv("DEFAULT_DELIVERY_FEE", 50.0))
ORDER_EXPIRY_MINUTES = int(os.getenv("ORDER_EXPIRY_MINUTES", 15))