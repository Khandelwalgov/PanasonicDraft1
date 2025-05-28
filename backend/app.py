# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import requests
# import traceback

# app = Flask(__name__)
# CORS(app)

# UPLOAD_DIR = "recordings"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # Set your active ngrok URL here
# COLAB_URL = "https://ae3e-35-230-59-62.ngrok-free.app/process"

# @app.route("/upload", methods=["POST"])
# def upload():
#     if 'audio' not in request.files:
#         return jsonify({"error": "No audio file found"}), 400

#     audio_file = request.files['audio']
#     filepath = os.path.join(UPLOAD_DIR, "recording.wav")
#     audio_file.save(filepath)

#     try:
#         print("[RENDER] Forwarding audio to Colab backend...")

#         with open(filepath, 'rb') as f:
#             files = {'audio': f}
#             response = requests.post(COLAB_URL, files=files, timeout=1200)  # ⏱️ 20-minute timeout

#         if response.status_code != 200:
#             print("[RENDER] Colab returned non-200 status")
#             return jsonify({"error": "Colab backend failed", "details": response.text}), 500

#         print("[RENDER] Received response from Colab.")
#         return jsonify(response.json())

#     except Exception as e:
#         print("[RENDER] Error occurred while forwarding to Colab:")
#         traceback.print_exc()
#         return jsonify({"error": "Exception occurred", "details": str(e)}), 500

#     finally:
#         if os.path.exists(filepath):
#             os.remove(filepath)

# # Ensure port binding for Render platform
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import traceback

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "recordings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

COLAB_BASE_URL = "https://fbad-34-23-222-137.ngrok-free.app"

@app.route("/upload", methods=["POST"])
def upload():
    if 'audio' not in request.files:
        print("No audio file in request")
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    filepath = os.path.join(UPLOAD_DIR, "recording.wav")
    audio_file.save(filepath)
    print(f"Audio file saved at {filepath}")

    try:
        with open(filepath, 'rb') as f:
            files = {'audio': f}
            print("Sending file to /transcribe")
            resp_trans = requests.post(f"{COLAB_BASE_URL}/transcribe", files=files, timeout=1200)

        print("Transcription response code:", resp_trans.status_code)
        print("Transcription response body:", resp_trans.text)
        if resp_trans.status_code != 200:
            return jsonify({"error": "Transcription failed", "details": resp_trans.text}), 500
        hindi_data = resp_trans.json()

        print("Sending Hindi transcript to /translate")
        resp_transl = requests.post(
            f"{COLAB_BASE_URL}/translate",
            json={"hindi_text": hindi_data["hindi_transcript"]},
            timeout=1200
        )
        print("Translation response code:", resp_transl.status_code)
        print("Translation response body:", resp_transl.text)
        if resp_transl.status_code != 200:
            return jsonify({"error": "Translation failed", "details": resp_transl.text}), 500
        english_data = resp_transl.json()

        print("Sending English translation to /evaluate")
        resp_eval = requests.post(
            f"{COLAB_BASE_URL}/evaluate",
            json={"english_text": english_data["english_translation"]},
            timeout=1200
        )
        print("Evaluation response code:", resp_eval.status_code)
        print("Evaluation response body:", resp_eval.text)
        if resp_eval.status_code != 200:
            return jsonify({"error": "Evaluation failed", "details": resp_eval.text}), 500
        eval_data = resp_eval.json()

        return jsonify({
            "hindi_transcript": hindi_data["hindi_transcript"],
            "english_translation": english_data["english_translation"],
            "review_feedback": eval_data["review_feedback"]
        })

    except Exception as e:
        print("Exception occurred:", e)
        traceback.print_exc()
        return jsonify({"error": "Exception occurred", "details": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted temp file: {filepath}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

