from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "recordings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Your Colab/ngrok URL
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
            response = requests.post(COLAB_URL, files=files,timeout=400 )

        if response.status_code != 200:
            return jsonify({"error": "Colab backend failed", "details": response.text}), 500

        print("[RENDER] Received response from Colab.")
        return jsonify(response.json())

    except Exception as e:
        print(f"[RENDER] Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
