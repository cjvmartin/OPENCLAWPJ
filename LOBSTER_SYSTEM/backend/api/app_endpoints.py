# api/gemini_api.py
def get_ai_response(user_input, test_mode=True):
    if test_mode:
        return f"【模擬模式】龍蝦收到了：{user_input}"
    else:
        # 這裡之後再放真正的 Gemini API 呼叫代碼
        pass