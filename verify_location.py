from flask import Blueprint, request, jsonify
from geopy.distance import geodesic
from firebase_init import save_checkin  # 匯入儲存功能
from push_message import push_audio_and_chart  # 語音推播

verify_bp = Blueprint('verify', __name__)

# 預設站點清單（站名 + 經緯度）
stations = {
    "忘憂森林": (23.345022, 120.130486),
    "嘉義大學民雄校區": (23.54537, 120.42856),
    "嘉義大學蘭潭校區": (23.46807, 120.48486),
    "好美船屋": (23.48720, 120.16255),
    "好美里3D彩繪村": (23.48591, 120.16214),
    "好美苗圃": (23.48830, 120.16021),
    "1920美漾森林": (23.49180, 120.15833),
    "防風林": (23.345942, 120.128865),
    "開溝築堤": (23.345427, 120.129811),
    "潮間帶": (23.50242, 120.14917)
}

@verify_bp.route("/verify-location", methods=["POST", "OPTIONS"])
def verify_location():
    if request.method == "OPTIONS":
        return '', 200
  
    data = request.get_json()
    user_id = data.get("userId")
    user_coords = (data.get("latitude"), data.get("longitude"))
    

    for station_name, station_coords in stations.items():
        distance = geodesic(user_coords, station_coords).meters
        if distance <= 500:  # 判斷 500 公尺內
            save_checkin(user_id, station_name)  # 儲存到 Firebase
            push_audio_and_chart(user_id, station_name)  # 呼叫語音推播
            return jsonify({
                "status": "success",
                "message": f"✅ {station_name} 打卡成功！距離：{int(distance)} 公尺"
            })

    return jsonify({
        "status": "fail",
        "message": "❌ 你尚未進入任何打卡範圍，請靠近再試。"
    })
