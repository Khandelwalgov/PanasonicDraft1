from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import traceback

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "recordings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set your active ngrok URL here
COLAB_URL = "https://ae3e-35-230-59-62.ngrok-free.app/process"

@app.route("/upload", methods=["POST"])
def upload():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    filepath = os.path.join(UPLOAD_DIR, "recording.wav")
    audio_file.save(filepath)

    try:
        print("[RENDER] Forwarding audio to Colab backend...")

        with open(filepath, 'rb') as f:
            files = {'audio': f}
            response = requests.post(COLAB_URL, files=files, timeout=1200)  # ⏱️ 20-minute timeout

        if response.status_code != 200:
            print("[RENDER] Colab returned non-200 status")
            return jsonify({"error": "Colab backend failed", "details": response.text}), 500

        print("[RENDER] Received response from Colab.")
        return jsonify(response.json())

    except Exception as e:
        print("[RENDER] Error occurred while forwarding to Colab:")
        traceback.print_exc()
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

# Ensure port binding for Render platform
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
