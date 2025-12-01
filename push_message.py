from linebot import LineBotApi
from linebot.models import ImageSendMessage, AudioSendMessage, FlexSendMessage
import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

forest_sub_station = ["忘憂森林", "開溝築堤", "防風林"]

def push_station_selection(user_id, main_station="1920美漾森林", sub_stations=None):

    if sub_stations is None:
        sub_stations = forest_sub_station

    buttons = []
    for name in sub_stations:
        buttons.append({
            "type": "button",
            "style": "primary",
            "height": "sm",
            "action": {
                "type": "postback",
                "label": name,
                "data": f"action=choose_sub_station&station={name}"
            },
            "margin": "md"
        })

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"你現在在「{main_station}」附近，請選擇實際站點：",
                    "weight": "bold",
                    "size": "md",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": buttons,
                }
            ]
        }
    }

    line_bot_api.push_message(
        user_id,
        FlexSendMessage(
            alt_text="請選擇站點",
            contents=bubble
        )
    )

# 各站點的語音導覽文字（之後可替換成 TTS）
voice_guides = {
    "忘憂森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/forest.mp3",
    "開溝築堤": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/dike.mp3",
    "防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/windbreak.mp3",
}

# 各站點對應的統計圖網址（目前為測試圖）
charts = {
    "忘憂森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/forest.png",
    "開溝築堤": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/dike.jpg",
    "防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/windbreak.png",
}

audio_durations = {
    "忘憂森林": 34, #秒
    "開溝築堤": 57,
    "防風林": 62,
}

quiz_start = lambda station_name:{
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": f"🌟 {station_name} ：知識問答遊戲 🌟",
            "weight": "bold",
            "size": "lg",
            "wrap": True
        },
        {
            "type": "text",
            "text": "聽完語音導覽後，開啟小測驗！完成所有站點答題並達到85%以上正確率，即可獲得專屬禮券！",
            "wrap": True,
            "margin": "md"
        },
        {
            "type": "button",
            "style": "primary",
            "action": {
            "type": "postback",
            "label": "開始答題！",
            "data": f"quiz_start=true&station={station_name}"
            },
            "margin": "xl"
        }
        ]
    }
}


def push_audio_and_chart(user_id, station_name):
    audio_url = voice_guides.get(station_name)
    chart_url = charts.get(station_name)
    duration = audio_durations.get(station_name)

    messages = []

    if audio_url:
        messages.append(AudioSendMessage(original_content_url=audio_url, duration=duration*1000))

    if chart_url:
        messages.append(ImageSendMessage(
            original_content_url=chart_url,
            preview_image_url=chart_url  # 預覽圖也用同一張
        ))
        
    quiz_flex = quiz_start(station_name)
    messages.append(FlexSendMessage(
        alt_text="知識問答遊戲開始！",
        contents=quiz_flex
    ))


    # 一次推送所有訊息
    if messages:
        line_bot_api.push_message(user_id, messages)
