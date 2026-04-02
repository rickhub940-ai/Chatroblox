from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB
client = MongoClient(os.getenv("MONGO_URL"))
db = client.ChatDatabase
collection = db.messages

@app.route('/')
def home():
    return "Global Chat System is Online & Secure!"

# 🔥 ส่งข้อความ
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
            "id": str(ObjectId())  # 🔥 id ไม่ซ้ำแน่นอน
        }

        collection.insert_one(new_msg)

        # 🔥 ลบเก่าให้เหลือ 30 ข้อความ (เร็วกว่าเดิม)
        count = collection.count_documents({})
        if count > 30:
            to_delete = count - 30
            old_ids = collection.find({}, {"_id": 1}).sort("timestamp", 1).limit(to_delete)
            collection.delete_many({"_id": {"$in": [doc["_id"] for doc in old_ids]}})

        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error"}), 400


# 🔥 ดึงข้อความ
@app.route('/get', methods=['GET'])
def get_messages():
    msgs = list(
        collection.find(
            {},
            {
                "_id": 0,
                "u": 1,
                "m": 1,
                "time": 1,
                "id": 1
            }
        ).sort("timestamp", 1)
    )
    return jsonify(msgs)


# 🔥 run local (optional)
if __name__ == '__main__':
    app.run()
