from flask import Flask, request, jsonify
app = Flask(__name__)
msgs = []

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    if len(msgs) > 20: msgs.pop(0)
    msgs.append({"u": data['u'], "m": data['m']})
    return jsonify({"s": True})

@app.route('/get', methods=['GET'])
def get():
    return jsonify(msgs)
  
