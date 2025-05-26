from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import replicate
from replicate.client import Client
import tempfile
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "recordings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Replicate models
WHISPER_MODEL = "openai/whisper"
NLLB_MODEL = "facebook/nllb-200-distilled-1.3b"
LLM_MODEL = "mistralai/mistral-7b-instruct-v0.1"

@app.route("/upload", methods=["POST"])
def upload():

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']
    filepath = os.path.join(UPLOAD_DIR, "recording.wav")
    audio_file.save(filepath)

    try:
        print("[BACKEND] Starting transcription using Replicate...")
        replicate_client = Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

        # Whisper transcription on Replicate
        with open(filepath, "rb") as f:
            output = replicate_client.run(
                WHISPER_MODEL,
                input={"audio": f, "language": "hi"}
            )
        hindi_text = output['text']
        print("[BACKEND] Transcription complete.")

        print("[BACKEND] Starting translation using Replicate...")
        # NLLB Translation
        translation_output = replicate_client.run(
            NLLB_MODEL,
            input={"text": hindi_text, "src_lang": "hin_Deva", "tgt_lang": "eng_Latn"}
        )
        english_text = translation_output[0] if isinstance(translation_output, list) else translation_output

        print("[BACKEND] Translation complete.")

        print("[BACKEND] Starting review using Replicate LLM...")
        # LLM Prompt for Review

        # You may later replace this prompt-building logic with your own custom logic
        original_script = """Let me introduce you the Latest 4K LED TV from Panasonic the # 1 appliance brand in Japan, known for quality, reliability, durability, and value for features.  
        A perfect TV is based on 4 Pillars of Picture, Sound, Design and connectivity + we are offering it with GOOGLE OS 
        This Premium 4K TV has a perfect Picture Quality & Superior sound to deliver an ultimate entertainment experience 
        1) The unique Hexa Chroma Drive provides combination of 6 colors for a vibrant color detailing and 4K Studio Color Engine for smooth, life like picture quality in every scene. 
        → (Play the 4K Content & Show Colour Details) 
        
        2) Here, you get Dolby Atmos 3D sound for clear dialogue and theatre-like sound, creating a realistic experience for movies, shows, and gaming. Additionally, Panasonic's built-in home theatre delivers powerful, high-quality sound. 
        → (Play the 4k song & experience Superior sound clarity & Quality) 
        
        3) With Hands-Free Voice Assistant [ Far Field] , you can control the TV and find content, making the experience more convenient and accessible. → (Hands-on Activity of google assistance) 
        
        4) Besides Premium Picture & Sound, it comes with Latest Google TV Operating System for a user-friendly experience, supports 10,000+ apps, allowing you to easily click and watch your favourite shows/movies. You can also create multiple profiles, including a kids' profile." 
        → (Show google TV interface & Kids profile)  
        
        5) Sleek & bezel Less design adds more premium elements to this LED to perfectly match with your home interior & aesthetics. 
        → (Touch & feel the bezel less design) 
        
        With these unique features, this Premium LED TV is the most advanced TV in the market at this moment."""

        prompt = f"""
        ### Instruction:
        You are a professional evaluator of retail product pitches and customer experience communication. Your task is to critically evaluate a spoken product pitch, focusing on its real-world impact on customer understanding, trust, and purchase intent, with respect to the original script.

        Spoken pitch:
        {english_text}

        Original script:
        {original_script}

        Evaluate the spoken pitch using the following practical criteria with reference to the original script:
        Anything that is in brackets should be ommitted as they are actions and not verbal in nature.
        Note: You dont have to rate the product or the original script. You just have to rate the spoken pitch with respect to the original script, at no point should you talk about things like technical jargon etc. Strictly evaluate the spoken text with respect to the original script only.
        Display the score only at the end

        1. Accuracy of Key Features: Harshly grade any inaccurate information or wrong information
        2. Coverage of Selling Points: Harshly grade any missing information that is significant, or is a feature.
        3. Clarity and Accessibility
        4. Customer Experience Impact
        5. Final Summary and overall score: should focus heavily on accuracy, coverage of selling points, while still talking about other criteria.

        Avoid nitpicking on harmless stylistic differences unless they significantly disrupt understanding.

        ### Response:
        """

        review_response = replicate_client.run(
            LLM_MODEL,
            input={"prompt": prompt, "temperature": 0.7, "max_new_tokens": 1024}
        )
        review_text = review_response if isinstance(review_response, str) else review_response[0]

        print("[BACKEND] Review complete.")

        return jsonify({
            "hindi_transcript": hindi_text,
            "english_translation": english_text,
            "review_feedback": review_text
        })

    except Exception as e:
        print(f"[BACKEND] Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
