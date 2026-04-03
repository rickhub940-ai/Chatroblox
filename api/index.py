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
online_collection = db.online_users # 🟢 Collection ใหม่สำหรับนับคนออนไลน์

# --- ฟังก์ชันช่วยนับคนออนไลน์ (หัวใจหลัก) ---
def get_online_count():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    now = datetime.now()
    
    # 1. บันทึก/อัปเดตเวลาที่ IP นี้ส่งสัญญาณมา
    online_collection.update_one(
        {"ip": user_ip},
        {"$set": {"last_seen": now}},
        upsert=True
    )
    
    # 2. ลบคนที่ไม่ส่งสัญญาณมาเกิน 1 นาที (ถือว่าออฟไลน์)
    threshold = now - timedelta(minutes=1)
    online_collection.delete_many({"last_seen": {"$lt": threshold}})
    
    # 3. นับจำนวน IP ที่เหลืออยู่
    return online_collection.count_documents({})

@app.route('/')
def home():
    return "009.exe Global Chat System is Online!"

# 🔥 ส่งข้อความ (เพิ่มการส่งค่า Online กลับไป)
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('u')
    message = data.get('m')
    
    if username and message:
        now = datetime.now()
        new_msg = {
            "u": username,
            "m": message,
            "time": now.strftime("%H:%M"),
            "timestamp": now,
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

# 🔥 ดึงข้อความ + จำนวนคนออนไลน์
@app.route('/get', methods=['GET'])
def get_messages():
    online_count = get_online_count() # 🟢 เช็คคนออนไลน์ทุกครั้งที่มีการ Get
    msgs = list(
        collection.find(
            {},
            {"_id": 0, "u": 1, "m": 1, "time": 1, "id": 1}
        ).sort("timestamp", 1)
    )
    # ส่งข้อมูลกลับไปแบบมีทั้ง Messages และ Online Count
    return jsonify({"messages": msgs, "online": online_count})

# 🔥 Route พิเศษสำหรับส่ง Heartbeat อย่างเดียว (เพื่อให้ UI อัปเดตเลขคนตลอด)
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    return jsonify({"online": get_online_count()}), 200

if __name__ == '__main__':
    app.run()
    
