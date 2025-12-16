from flask import Blueprint, request, jsonify
from geopy.distance import geodesic
from firebase_init import save_checkin  # 匯入儲存功能
from push_message import push_audio_and_chart, push_station_selection  # 語音推播

verify_bp = Blueprint('verify', __name__)

# 預設站點清單（站名 + 經緯度）
stations = {
    # "1920美漾森林": (23.345419, 120.1298145)
    "1920美漾森林": (23.682801, 120.478931) #test location
    # "忘憂森林": (23.344991,120.130489),
    # "防風林": (23.345301,120.129999),
    # "開溝築堤": (23.345427, 120.129811),
    # "嘉義大學民雄校區": (23.54537, 120.42856),
    # "嘉義大學蘭潭校區": (23.46807, 120.48486),
}

sub_stations = {
    "1920美漾森林": ["忘憂森林", "開溝築堤", "防風林"]
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

        if distance <= 300:  # 判斷 X 公尺內
            if station_name in sub_stations: #是否有子站點
                save_checkin(user_id, f"{station_name}_區域")
                push_station_selection(user_id, main_station=station_name, sub_stations=sub_stations[station_name])
                
                return jsonify({
                    "status": "success",
                    "message": f"✅ 已進入 {station_name} 附近（約 {int(distance)} 公尺），請在 LINE 選擇站點。"
                })
            else:    
                save_checkin(user_id, station_name)  # 儲存到 Firebase
                push_audio_and_chart(user_id, station_name)
                return jsonify({
                    "status": "success",
                    "message": f"✅ {station_name} 打卡成功！距離：{int(distance)} 公尺"
                })

    return jsonify({
        "status": "fail",
        "message": "❌ 你尚未進入任何打卡範圍，請靠近再試。"
    })
