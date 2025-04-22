from linebot import LineBotApi
from linebot.models import ImageSendMessage, AudioSendMessage
import os

# 初始化 LINE API
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 各站點的語音導覽文字（之後可替換成 TTS）
voice_guides = {
    "大潤發": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/RT_MART.mp3",
    "嘉義大學民雄校區": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/chiayi_minxiog.mp3",
    "嘉義大學蘭潭校區": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/chiayi_langtang.mp3",
    "好美船屋": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/boat_house.mp3",
    "好美里3D彩繪村": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/3D_painting.mp3",
    "好美苗圃": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/garden.mp3",
    "1920美漾森林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/1920_meiyan.mp3",
    "好美里防風林": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/windbreak.mp3",
    "潮間帶": "https://cdn.jsdelivr.net/gh/An-HS/haomei-assets/audio/intertidal_zone.mp3" ,
}

# 各站點對應的統計圖網址（目前為測試圖）
charts = {
    "大潤發": "https://i.imgur.com/A0bZKOW.jpg",
    "嘉義大學民雄校區": "https://i.imgur.com/OteSTlJ.jpg",
    "嘉義大學蘭潭校區": "https://i.imgur.com/ojUDYvj.jpg",
    "好美船屋": "https://i.imgur.com/A0bZKOW.jpg",
    "好美里3D彩繪村": "https://i.imgur.com/OteSTlJ.jpg",
    "好美苗圃": "https://i.imgur.com/ojUDYvj.jpg",
    "1920美漾森林": "https://i.imgur.com/A0bZKOW.jpg",
    "好美里防風林": "https://i.imgur.com/OteSTlJ.jpg",
    "潮間帶": "https://i.imgur.com/ojUDYvj.jpg" ,
}

def push_audio_and_chart(user_id, station_name):
    audio_url = voice_guides.get(station_name)
    chart_url = charts.get(station_name)

    messages = []

    if audio_url:
        messages.append(AudioSendMessage(original_content_url=audio_url, duration=8000))

    if chart_url:
        messages.append(ImageSendMessage(
            original_content_url=chart_url,
            preview_image_url=chart_url  # 預覽圖也用同一張
        ))
        

    # 一次推送所有訊息
    if messages:
        line_bot_api.push_message(user_id, messages)
