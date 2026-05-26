# 檔案路徑：backend/api/line_bot.py
from fastapi import APIRouter, Request, Header, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from backend.config import settings
from backend.core.agent_a import LobsterAgentA
from backend.database.db_manager import save_new_order

router = APIRouter()
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
agent_a = LobsterAgentA()

@router.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text
    
    # 🦞 呼叫我們最強的 3.1 Flash-Lite 預覽版大腦
    # 這裡暫時用 user_id 當名字，之後可以透過 API 抓真實暱稱
    result = agent_a.parse_order_text(user_id, user_text)
    
    if result.get("action") == "order" and result.get("is_valid"):
        # 成功解析：存入 SQLite 並回傳成功訊息
        order_id = save_new_order(user_id, result.get("items"))
        reply = f"✅ 龍蝦收到！訂單編號 #{order_id}\n{result.get('final_msg')}"
    else:
        # 被風控攔截 (例如雞腿一百個)
        reply = f"🚨 龍蝦提醒：{result.get('final_msg', '無法處理此訊息')}"
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))