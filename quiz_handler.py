from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage, PostbackEvent, ImageSendMessage
from firebase_admin import db
import os
from generate_congrats_card import generate_card
from firebase_init import save_checkin 
from push_message import push_audio_and_chart

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 題庫設計
quizzes = {
    "忘憂森林": [
        {
            "question": "忘憂森林形成的主要原因是什麼？",
            "options": ["A. 森林火災", "B. 長期積水", "C. 過度砍伐", "D. 土石流"],
            "answer": "B"
        },
        {
            "question": "林木死亡的主要原因是？",
            "options": ["A. 氣候太冷", "B. 遭受病蟲害", "C. 根部缺氧", "D. 動物踐踏"],
            "answer": "C"
        },
        {
            "question": "為什麼枯木不會立刻腐爛？",
            "options": ["A. 浸在水中", "B. 土壤太乾", "C. 被動物吃掉", "D. 日照太強"],
            "answer": "A"
        }
    ],
    "開溝築堤": [
        {
            "question": "開溝築堤改善了哪項問題？",
            "options": ["A. 野生動物過多", "B. 改善鹽鹼土壤", "C. 觀光客不足", "D. 空氣污染"],
            "answer": "B"
        },
        {
            "question": "土堤邊坡為何要種紅樹林？",
            "options": ["A. 美化景觀", "B. 改善水質", "C. 提供果實", "D. 穩固邊坡"],
            "answer": "D"
        }
    ],
    "防風林": [
        {
            "question": "臺灣海岸林的價值最早可追溯到哪個時期？",
            "options": ["A. 元朝末期", "B. 荷蘭統治時期", "C. 清法戰爭", "D. 民國初年"],
            "answer": "C"
        },
        {
            "question": "近年海岸造林採兩階段的原因是？",
            "options": ["A. 純林結構於環境適應性太高", "B. 單一物種生長太快", "C. 使森林更加美觀", "D. 增加生態韌性"],
            "answer": "D"
        },
        {
            "question": "複層林的第一層植物是？",
            "options": ["A. 黃槿", "B. 草海桐", "C. 馬鞍藤", "D. 木麻黃"],
            "answer": "D"
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
    
    if params.get("action") == "choose_sub_station":
        sub_station = params.get("station")

        if not sub_station:
            # 沒拿到站名就回個 debug 訊息（幫你測）
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"⚠️ 無法辨識站點，收到的 data 為：{data}")
            )
            return
        
        save_checkin(user_id, sub_station)
        push_audio_and_chart(user_id, sub_station)

        # 回一句話確認這個分支有被觸發
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"已為你開始「{sub_station}」的導覽與小測驗，請留意後續語音與圖片。")
        )

        return

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
            card_url = generate_card(user_name, f"{correct_rate}%", station)
            
            # 發送小卡給使用者
            line_bot_api.push_message(user_id, ImageSendMessage(
                original_content_url=card_url,
                preview_image_url=card_url
            ))
        
