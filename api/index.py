from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import pytz
import os

app = Flask(__name__)
CORS(app)

# ดึงค่าจาก Vercel Settings (Key: MONGO_URL)
MONGO_URI = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URI)
db = client.ChatDatabase
collection = db.Messages

@app.route('/get', methods=['GET'])
def get_messages():
    try:
        # ดึง 30 ข้อความล่าสุด เรียงตามเวลา
        chats = list(collection.find({}, {"_id": 0}).sort("t", -1).limit(30))
        chats.reverse() 
        return jsonify(chats)
    except:
        return jsonify([])

@app.route('/send', methods=['POST'])
def send_message():
    try:
        data = request.get_json(force=True)
        tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(tz).strftime("%H:%M")
        
        new_chat = {
            "u": str(data['u']),
            "m": str(data['m']),
            "time": now,
            "t": datetime.now(tz)
        }
        collection.insert_one(new_chat)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Global Chat System is Online & Secure!"
    
