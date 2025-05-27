from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import cloudinary
import cloudinary.uploader
import os, uuid
from datetime import datetime

# 初始化 Cloudinary（Render 上要設在環境變數）
cloudinary.config(
  cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key=os.getenv("CLOUDINARY_API_KEY"),
  api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def generate_card(user_name, correct_rate, station_name):
    # 取得 backend/static 的絕對路徑
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    # 根據站點名稱選擇不同背景圖
    bg_filename = {
        "大潤發": "wetland.png",
        "嘉義大學蘭潭校區": "wetland.png",
        "嘉義大學民雄校區": "wetland.png",
        "好美船屋": "wetland_minxiong.png",
        "好美里3D彩繪村": "wetland_minxiong.png",
        "好美苗圃": "wetland_minxiong.png",
        "1920美漾森林": "wetland_minxiong.png",
        "好美里防風林": "wetland_minxiong.png",
        "潮間帶": "wetland_minxiong.png"
    }.get(station_name, "wetland.png")  # 預設圖
    
    bg_path = os.path.join(static_dir, bg_filename)
    img = Image.open(bg_path)
    time = datetime.now().strftime("%Y-%m-%d")

    font_url = "https://github.com/notofonts/noto-cjk/blob/main/Sans/Mono/NotoSansMonoCJKjp-Bold.otf?raw=true"
    font_path = os.path.join(static_dir, "NotoSansMonoCJKjp-Bold.otf")
    if not os.path.exists(font_path):
        with open(font_path, "wb") as f:
            f.write(requests.get(font_url).content)
    with open(font_path, "rb") as f:
        font_data = f.read()

    draw = ImageDraw.Draw(img)
    font_large = ImageFont.truetype(BytesIO(font_data), 40)
    draw.text((42, 60), user_name, font=font_large, fill=(36, 71, 45, 1))
    
    font_small = ImageFont.truetype(BytesIO(font_data), 20)
    draw.text((42, 152), time, font=font_small, fill=(36, 71, 45, 1))

    font_rate = ImageFont.truetype(BytesIO(font_data), 80)
    draw.text((228, 20), correct_rate, font=font_rate, fill=(36, 71, 45, 1))
    
    # 暫存圖片
    temp_path = f"temp_{user_name}_{uuid.uuid4().hex}.png"
    img.save(temp_path)
    
    # 上傳到 Cloudinary
    result = cloudinary.uploader.upload(
        temp_path,
        folder="congrats_cards"  # 設定資料夾名稱
    )
    os.remove(temp_path) # 刪除暫存
    
    return result['secure_url']

# # 測試
# if __name__ == "__main__":
#     url = generate_card("阿熊", "85%")
#     print(f"圖片網址：{url}")