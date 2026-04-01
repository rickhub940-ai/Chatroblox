from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ตัวแปรเก็บข้อความ (จะหายเมื่อ Vercel หลับ)
messages_list = []

@app.route('/')
def home():
    return "API is Online! Use /get to see messages."

@app.route('/get', methods=['GET'])
def get_messages():
    return jsonify(messages_list)

@app.route('/send', methods=['POST'])
def send_message():
    try:
        # รับข้อมูล JSON จาก Roblox
        data = request.get_json(force=True)
        
        if not data or 'u' not in data or 'm' not in data:
            return jsonify({"error": "Invalid Data"}), 400
            
        # เก็บข้อความ (จำกัดไว้ 20 ข้อความ)
        messages_list.append({
            "u": str(data['u']),
            "m": str(data['m'])
        })
        
        if len(messages_list) > 20:
            messages_list.pop(0)
            
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ส่วนนี้สำคัญมากสำหรับ Vercel
if __name__ == '__main__':
    app.run(debug=True)
    
