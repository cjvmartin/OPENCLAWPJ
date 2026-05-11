# 檔案路徑：backend/core/agent_b.py
from google import genai
from backend.config import settings

class LobsterAgentB:
    """
    龍蝦 B (物流協調員)：負責生成與店家的溝通腳本。
    """
    def __init__(self):
        # 這裡直接初始化 Client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEYS[0])
        self.model_id = settings.CURRENT_MODEL 
        self.name = "龍蝦 B (物流大師)"

    def generate_store_call_script(self, order_details):
        """
        利用 gemini-3.1-flash-lite-preview生成專業對話腳本
        """
        prompt = f"請根據以下訂單內容，生成一段給外送員參考的撥打給店家的專業確認電話劇本：{order_details}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"自動腳本生成失敗，錯誤訊息：{e}"