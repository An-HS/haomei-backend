from linebot import LineBotApi
from linebot.models import ImageSendMessage, AudioSendMessage, FlexSendMessage
import os

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 各站點的語音導覽文字（之後可替換成 TTS）
voice_guides = {
    "忘憂森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/forest.mp3", #原大潤發
    "開溝築堤": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/dike.mp3", #原民雄
    "防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/windbreak.mp3", #原蘭潭
    # "好美船屋": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/dike.mp3",
    # "好美里3D彩繪村": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/dike.mp3",
    # "好美苗圃": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/forest.mp3",
    # "1920美漾森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/windbreak.mp3",
    # "好美里防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/windbreak.mp3",
    # "潮間帶": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/forest.mp3" ,
}

# 各站點對應的統計圖網址（目前為測試圖）
charts = {
    "忘憂森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/RT_MART.png",
    "開溝築堤": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/3D_painting.jpg",
    "防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/RT_MART.png",
    # "好美船屋": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/garden.jpeg",
    # "好美里3D彩繪村": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/chiayi_langtang.jpeg",
    # "好美苗圃": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/chiayi_minxiog.jpeg",
    # "1920美漾森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/1920_meiyan.jpg",
    # "好美里防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/chiayi_minxiog.jpeg",
    # "潮間帶": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets@main/station_images/RT_MART.png" ,
}

audio_durations = {
    "忘憂森林": 44, #秒
    "開溝築堤": 50,
    "防風林": 59,
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


def push_audio_and_chart(user_id, station_name, duration):
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
