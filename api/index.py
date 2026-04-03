from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URL"))
db = client.ChatDatabase
collection = db.messages
online_collection = db.online_users # สำหรับนับคนออนไลน์

# --- ฟังก์ชันนับคนออนไลน์ (อัปเดตทุกครั้งที่มีการเรียก) ---
def get_online_count():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    now_utc = datetime.utcnow()
    now_thailand = now_utc + timedelta(hours=7)
    
    # บันทึกเวลาล่าสุดของ IP นี้ (UTC+7)
    online_collection.update_one(
        {"ip": user_ip},
        {"$set": {"last_seen": now_thailand}},
        upsert=True
    )
    
    # ถ้าใครไม่ส่งสัญญาณเกิน 10 วินาที ให้ถือว่าออฟไลน์ (เพื่อให้เลขขยับไวตามที่คุณต้องการ)
    threshold = now_thailand - timedelta(seconds=10)
    online_collection.delete_many({"last_seen": {"$lt": threshold}})
    
    return online_collection.count_documents({})

@app.route('/')
def home():
    return "009.exe Global Chat Online (UTC+7)"

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('u')
    message = data.get('m')
    
    if username and message:
        now_utc = datetime.utcnow()
        now_thailand = now_utc + timedelta(hours=7)

        new_msg = {
            "u": username,
            "m": message,
            "time": now_thailand.strftime("%H:%M"),
            "timestamp": now_thailand,
            "id": str(ObjectId())
        }
        collection.insert_one(new_msg)

        # ลบเก่าให้เหลือ 30 ข้อความ
        count = collection.count_documents({})
        if count > 30:
            to_delete = count - 30
            old_ids = collection.find({}, {"_id": 1}).sort("timestamp", 1).limit(to_delete)
            collection.delete_many({"_id": {"$in": [doc["_id"] for doc in old_ids]}})

        return jsonify({"status": "success", "online": get_online_count()}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get', methods=['GET'])
def get_messages():
    online = get_online_count()
    msgs = list(collection.find({}, {"_id": 0, "u": 1, "m": 1, "time": 1, "id": 1}).sort("timestamp", 1))
    return jsonify({"messages": msgs, "online": online})

# 🔥 Route สำหรับ Heartbeat โดยเฉพาะ (รองรับการยิงทุก 1 วิ)
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    return jsonify({"online": get_online_count()}), 200

if __name__ == '__main__':
    app.run()
    
