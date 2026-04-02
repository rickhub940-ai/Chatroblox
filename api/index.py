from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# เชื่อมต่อ MongoDB (ใช้ MONGO_URL จาก Environment Variables)
import os
client = MongoClient(os.getenv("MONGO_URL"))
db = client.ChatDatabase
collection = db.messages

@app.route('/')
def home():
    return "Global Chat System is Online & Secure!"

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('u')
    message = data.get('m')
    
    if username and message:
        # 1. บันทึกข้อความใหม่
        new_msg = {
            "u": username,
            "m": message,
            "time": datetime.now().strftime("%H:%M"),
            "timestamp": datetime.now() # เก็บเวลาจริงไว้ใช้เรียงลำดับ
        }
        collection.insert_one(new_msg)
        
        # --- 2. ส่วนที่เพิ่มเข้ามา: ลบข้อมูลเก่าถ้าเกิน 30 ข้อความ ---
        count = collection.count_documents({})
        if count > 30:
            # หาข้อความที่เก่าที่สุด (เรียงตาม timestamp)
            oldest_messages = collection.find().sort("timestamp", 1).limit(count - 30)
            for msg in oldest_messages:
                collection.delete_one({"_id": msg["_id"]})
        # --------------------------------------------------
        
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get', methods=['GET'])
def get_messages():
    # ดึง 30 ข้อความล่าสุด เรียงตามเวลา
    msgs = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    return jsonify(msgs)
    
