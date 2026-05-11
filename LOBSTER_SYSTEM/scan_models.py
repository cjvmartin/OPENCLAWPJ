# 檔案：scan_models.py
from google import genai
from backend.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEYS[0])

print("--- 🔍 正在掃描你的 API Key 可用的模型名稱 ---")
try:
    # 這裡會列出所有你可以用的模型
    for model in client.models.list():
        # 我們只找支援生成內容的 Flash 模型
        if "generateContent" in model.supported_generation_methods and "flash" in model.name:
            print(f"✅ 可用模型 ID: {model.name}")
except Exception as e:
    print(f"❌ 掃描失敗，請檢查金鑰：{e}")