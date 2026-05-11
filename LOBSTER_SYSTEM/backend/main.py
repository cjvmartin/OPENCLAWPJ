# 檔案路徑：backend/main.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 匯入專案設定、大腦邏輯與資料庫管理
from backend.config import settings
from backend.core.agent_a import LobsterAgentA
from backend.core.agent_b import LobsterAgentB
from backend.database.db_manager import init_db, save_new_order, get_all_orders

# 1. 初始化 FastAPI APP
app = FastAPI(
    title="龍蝦外送系統 API",
    description="基於 Gemini 3.1 Flash-Lite 的自動化調度後端",
    version="2.1.0"
)

# 2. 處理 CORS 跨域請求 (讓 Flutter 能順利連線)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 在伺服器啟動時初始化資料庫與 AI 引擎
agent_a = LobsterAgentA()
agent_b = LobsterAgentB()

@app.on_event("startup")
async def startup_event():
    init_db()
    print("🗄️ 資料庫已就緒！")
    print(f"🦞 系統已串接核心模型：{settings.CURRENT_MODEL}")

# --- API 接口定義 ---

# 4. 根目錄檢查
@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "Lobster Empire 2.1",
        "database": "SQLite Connected"
    }

# 5. 訂單解析與自動存檔
@app.post("/api/order/parse")
async def parse_order(
    user_name: str = Body(..., embed=True),
    text: str = Body(..., embed=True)
):
    """
    接收 LINE 訊息，解析後自動存入 SQLite 資料庫
    """
    # 呼叫 Gemini 3.1 大腦進行解析
    result = agent_a.parse_order_text(user_name, text)
    
    if result.get("action") == "order":
        # 解析成功後，直接呼叫 db_manager 存入資料庫
        order_id = save_new_order(user_name, result.get("items", []))
        result["db_id"] = order_id
        print(f"✅ 訂單 #{order_id} 解析成功並已入庫")
        return result
    else:
        # 如果解析出來不是訂單格式，報錯 400
        raise HTTPException(status_code=400, detail="無法解析訂單內容")

# 6. 讀取所有訂單 (供 Flutter APP 顯示列表)
@app.get("/api/delivery/orders")
async def get_active_orders():
    """
    從資料庫讀取真實的訂單數據
    """
    db_orders = get_all_orders()
    return [
        {
            "order_id": f"LOB-{o.id:03d}",
            "user": o.user_name,
            "items": o.items_json,
            "status": o.status,
            "fee": o.total_fee,
            "time": o.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for o in db_orders
    ]

# 7. 語音輔助劇本接口
# 修改 backend/main.py 中的 parse_order 函數
# 檔案路徑：backend/main.py (關鍵修正版)

@app.post("/api/order/parse")
async def parse_order(user_name: str = Body(..., embed=True), text: str = Body(..., embed=True)):
    # 1. 讓 3.1 Flash-Lite 進行審核
    result = agent_a.parse_order_text(user_name, text)
    
    # 2. 只有「合理」的訂單才進資料庫
    if result.get("action") == "order" and result.get("is_valid"):
        order_id = save_new_order(user_name, result.get("items", []))
        result["db_id"] = order_id
        print(f"✅ 訂單 #{order_id} 成功入庫")
        return result
    
    # 3. 處理「被攔截」或「不合理」的情況 (不再噴 400，改用 200 回傳訊息)
    else:
        # 這裡直接回傳 AI 的判斷結果，讓使用者知道為什麼失敗
        return {
            "status": result.get("action"),
            "is_valid": False,
            "message": result.get("final_msg", "系統暫時無法處理此請求"),
            "parsed_items": result.get("items", []) # 就算被拒絕，也秀出解析結果給你看
        }

# --- 啟動入口 ---
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG_MODE
    )