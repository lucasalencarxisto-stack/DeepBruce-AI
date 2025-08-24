from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/")
def root():
    return jsonify(message="OQS_step2 API is running", status="ok")

@app.get("/status")
def status():
    return jsonify(app="OQS_step2", version="0.1.0", health="healthy")

@app.post("/echo")
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify(received=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
