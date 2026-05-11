# 檔案路徑：backend/core/agent_a.py
import json
from google import genai
from backend.config import settings

class LobsterAgentA:
    def __init__(self):
        self.keys = settings.GEMINI_API_KEYS
        self.current_key_index = 0
        self.model_id = settings.CURRENT_MODEL # 使用 gemini-3.1-flash-lite-preview
        self._init_client()

    def _init_client(self):
        if self.keys:
            self.client = genai.Client(api_key=self.keys[self.current_key_index])
            self.has_api = True
        else:
            self.has_api = False

    def parse_order_text(self, user_name, raw_text):
        if not self.has_api:
            return {"action": "order", "items": [], "user": user_name}

        # 🚀 注入風控指令：針對惡作劇與大宗訂單的判斷準則
        system_prompt = (
            "你是一個龍蝦外送系統的風控官。請將對話轉為 JSON。\n"
            "規則：\n"
            "1. 若內容是胡言亂語、無意義字元，action 設為 'invalid'。\n"
            "2. 統計總份數：\n"
            "   - 總數 > 15：視為惡作劇，action 設為 'rejected'，並在 message 寫下拒絕原因。\n"
            "   - 8 <= 總數 <= 15：action 為 'order'，但 warning 必須提醒『需承擔集體收款責任』。\n"
            "   - 總數 < 8：正常處理。\n"
            "3. 輸出格式必須包含：{action, items: [{name, qty}], warning, message, user}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"{system_prompt}\n用戶 {user_name} 說：{raw_text}"
            )
            
            result = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            
            # 輔助計算總數以確保判斷無誤
            total_qty = sum(item.get('qty', 0) for item in result.get('items', []))
            
            # --- 最終判定邏輯 ---
            if result.get("action") == "rejected" or total_qty > 15:
                result["is_valid"] = False
                result["final_msg"] = f"🚨 訂單不合理：偵測到數量達 {total_qty} 份，已自動攔截。"
            elif result.get("action") == "invalid":
                result["is_valid"] = False
                result["final_msg"] = "🦞 龍蝦偵測到無效訊息，請輸入正確點餐內容。"
            else:
                result["is_valid"] = True
                if total_qty >= 8:
                    result["final_msg"] = f"✅ 訂單已受理 (共 {total_qty} 份)。提醒：請自行向同事收款，系統將一次扣款。"
                else:
                    result["final_msg"] = "✅ 訂單已成功解析並存檔。"
            
            return result

        except Exception as e:
            print(f"❌ 3.1 Lite 引擎異常：{e}")
            return {"action": "error", "is_valid": False, "final_msg": "系統暫時無法處理您的請求"}