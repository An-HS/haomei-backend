from flask import Flask, request, abort, render_template, send_from_directory, send_from_directory
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent
import os
from dotenv import load_dotenv
from verify_location import verify_bp
from quiz_handler import handle_postback as quiz_handle_postback
# from postback_handler import handle_postback as general_handle_postback


load_dotenv()  # 讀取 .env 檔

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

app = Flask(__name__)
CORS(app) #Flask允許跨網域請求
app.register_blueprint(verify_bp) #呼叫函式驗證位置訊息

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/map_checkin")
def map_checkin():
    return render_template("map_checkin.html")

@handler.add(PostbackEvent)
def on_postback(event):
    handle_postback(event)

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 LINE 傳來的簽章
    signature = request.headers['X-Line-Signature']

    # 取得請求的主體內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證簽章與處理內容
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route('/favicon.ico') #定位打勾圖片
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
# 收到 Postback
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("quiz_start") or "quiz_station" in data:
        quiz_handle_postback(event)
    # else:
    #     general_handle_postback(event)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 會提供 PORT，否則預設用 5000
    app.run(host="0.0.0.0", port=port)