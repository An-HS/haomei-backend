from flask import Blueprint, request, jsonify
from geopy.distance import geodesic
from firebase_init import save_checkin  # 匯入儲存功能

verify_bp = Blueprint('verify', __name__)

# 預設站點清單（站名 + 經緯度）
stations = {
    "安珩家": (23.68219, 120.47902),
    "好美船屋": (23.48720, 120.16255),
    "好美里3D彩繪村": (23.48591, 120.16214),
    "好美苗圃": (23.48830, 120.16021),
    "1920美漾森林": (23.49180, 120.15833),
    "好美里防風林": (23.49801, 120.15452),
    "潮間帶": (23.50242, 120.14917)
}

@verify_bp.route("/verify-location", methods=["POST", "OPTIONS"])
def verify_location():
    if request.method == "OPTIONS":
        #print("收到預檢請求 OPTIONS（這裡不會有 userId）")
        return '', 200
  
    data = request.get_json()
    #print(f"📦 原始資料內容：{data}")
    user_id = data.get("userId")
    user_coords = (data.get("latitude"), data.get("longitude"))
    
    #print(f"🆔 收到打卡請求：UserID={user_id}，位置=({user_coords})")

    for station_name, station_coords in stations.items():
        distance = geodesic(user_coords, station_coords).meters
        #print(f"使用者與 {station_name} 的距離：{distance:.2f} 公尺")  # debug用
        if distance <= 500:  # 判斷 500 公尺內
            save_checkin(user_id, station_name)  # 儲存到 Firebase
            return jsonify({
                "status": "success",
                "message": f"✅ {station_name} 打卡成功！距離：{int(distance)} 公尺"
            })

    return jsonify({
        "status": "fail",
        "message": "❌ 你尚未進入任何打卡範圍，請靠近再試。"
    })
