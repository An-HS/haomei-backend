from flask import Flask, request, abort, render_template, send_from_directory, send_from_directory
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
from verify_location import verify_bp


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


# 收到文字訊息就原封不動回覆
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你說的是：「{user_msg}」")
    )

if __name__ == "__main__":
    app.run(port=8000)