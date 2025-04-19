import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# 初始化 Firebase
cred = credentials.Certificate("/etc/secrets/firebase_key.json")  # 金鑰檔放這裡
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://wetland-guild-default-rtdb.asia-southeast1.firebasedatabase.app/"  # 改成你的專案網址
})

def save_checkin(user_id, station_name):
    ref = db.reference(f"/checkins/{user_id}")
    ref.push({
        "station": station_name,
        "timestamp": datetime.now().isoformat()  # 儲存為 ISO 格式字串
    })
    # 標記這個站已經打過
    ref_simple = db.reference(f"/checkins_simple/{user_id}")
    ref_simple.update({station_name: True})
