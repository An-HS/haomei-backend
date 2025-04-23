from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage, FlexSendMessage, PostbackEvent
import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 題庫設計
quizzes = {
    "大潤發": [
        {
            "question": "濕地的重要功能是？",
            "options": ["A. 提供生物棲息地", "B. 提供沙漠環境", "C. 阻擋颱風登陸", "D. 提供夜市美食"],
            "answer": "A"
        },
        {
            "question": "3D彩繪的特色是？",
            "options": ["A. 看起來很立體", "B. 用沙子畫的", "C. 需要戴3D眼鏡", "D. 晚上才看得見"],
            "answer": "A"
        }
    ],
    "嘉義大學蘭潭校區": [
        {
            "question": "潮間帶的生物特色是？",
            "options": ["A. 耐鹽性強", "B. 只能在深海生存", "C. 生活在沙漠", "D. 會飛行"],
            "answer": "A"
        }
    ]
}

# 啟動問答流程（推播第一題）
def start_quiz(user_id, station_name):
    quiz_list = quizzes.get(station_name)
    if not quiz_list:
        line_bot_api.push_message(user_id, TextSendMessage(text="此站點沒有題目哦！"))
        return

    first_quiz = quiz_list[0]
    flex_message = generate_quiz_flex(station_name, 1, first_quiz)
    line_bot_api.push_message(user_id, FlexSendMessage(alt_text="開始答題囉！", contents=flex_message))

# 建立題目 Flex Message
def generate_quiz_flex(station_name, question_index, quiz):
    options = [
        {
            "type": "button",
            "style": "primary",
            "action": {
                "type": "postback",
                "label": opt,
                "data": f"quiz_station={station_name}&question={question_index}&answer={opt[0]}"
            },
            "margin": "20px"
        }
        for opt in quiz['options']
    ]
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", 
                "text": f"問題 {question_index}: {quiz['question']}",
                "wrap": True,
                "weight": "bold", 
                "size": "md"},
                *options
            ]
        }
    }

# 監聽 Postback (這個流程要接到 Webhook 處理 PostbackEvent)
def handle_postback(event: PostbackEvent):
    data = event.postback.data
    params = dict(param.split('=') for param in data.split('&'))

    if params.get("quiz_start") == "true":
        station = params.get("station")
        start_quiz(event.source.user_id, station)

# 測試用
# start_quiz("user_id", "好美里3D彩繪村")
