from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage, PostbackEvent, ImageSendMessage
from firebase_admin import db
import os
from generate_congrats_card import generate_card

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

# 更新全站統計
def update_quiz_stats(station_name, question_number, is_correct):
    ref = db.reference(f"/quiz_stats/{station_name}/{question_number}")
    stats = ref.get() or {"total_attempts": 0, "correct_attempts": 0}
    stats["total_attempts"] += 1
    if is_correct:
        stats["correct_attempts"] += 1
    ref.set(stats)

# 儲存個人答題記錄
def save_user_answer(user_id, station_name, question_index, answer, correct):
    ref = db.reference(f"/quiz_records/{user_id}/{station_name}/question_{question_index}")
    ref.set({
        "answer": answer,
        "correct": correct
    })
    
# 計算答題正確率
def calculate_correct_rate(user_id, station_name):
    ref = db.reference(f"/quiz_records/{user_id}/{station_name}")
    records = ref.get()

    if not records:
        return 0

    total = len(records)
    correct = sum(1 for q in records.values() if q['correct'])

    return int((correct / total) * 100)  # 回傳百分比


# 監聽 Postback
def handle_postback(event: PostbackEvent):
    data = event.postback.data
    params = dict(param.split('=') for param in data.split('&'))

    user_id = event.source.user_id

    if params.get("quiz_start") == "true":
        station = params.get("station")
        start_quiz(user_id, station)
    elif "quiz_station" in params:
        station = params["quiz_station"]
        question_idx = int(params["question"])
        user_answer = params["answer"]

        quiz_list = quizzes[station]
        correct_answer = quiz_list[question_idx - 1]["answer"]
        is_correct = user_answer == correct_answer

        # 更新資料庫
        save_user_answer(user_id, station, question_idx, user_answer, is_correct)
        update_quiz_stats(station, question_idx, is_correct)

        # 如果還有下一題
        if question_idx < len(quiz_list):
            next_quiz = quiz_list[question_idx]
            flex_message = generate_quiz_flex(station, question_idx + 1, next_quiz)
            line_bot_api.push_message(user_id, FlexSendMessage(alt_text="下一題來囉！", contents=flex_message))
        else:
            # 全部答完，推送解答
            answers = "\n".join([f"問題 {i+1}: 正確答案是 {q['answer']}" for i, q in enumerate(quiz_list)])
            line_bot_api.push_message(user_id, TextSendMessage(text=f"🎉 你已完成所有題目！\n{answers}"))
            
            # 取得使用者名稱
            user_name = line_bot_api.get_profile(user_id).display_name
            correct_rate = calculate_correct_rate(user_id, station)
            card_url = generate_card(user_name, f"{correct_rate}%")
            
            # 發送小卡給使用者
            line_bot_api.push_message(user_id, ImageSendMessage(
                original_content_url=card_url,
                preview_image_url=card_url
            ))
        
