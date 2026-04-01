from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # อนุญาตให้ Roblox เข้าถึงได้
msgs = []

@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.json
        if not data or 'u' not in data or 'm' not in data:
            return jsonify({"s": False}), 400
        if len(msgs) > 25: msgs.pop(0) # เก็บ 25 ข้อความล่าสุด
        msgs.append({"u": data['u'], "m": data['m']})
        return jsonify({"s": True})
    except:
        return jsonify({"s": False}), 500

@app.route('/get', methods=['GET'])
def get():
    return jsonify(msgs)

@app.route('/')
def home():
    return "Global Chat API is Online!"
    
