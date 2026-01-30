import os
import json
import csv
from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_cors import CORS
from googletrans import Translator
from werkzeug.utils import secure_filename
from vosk import Model, KaldiRecognizer
import wave
from gtts import gTTS
from io import BytesIO
import base64
from flask_sock import Sock
import torch
from torchvision import transforms
from PIL import Image
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"
CORS(app)
sock = Sock(app)
translator = Translator()

# ---------------- Vosk Models ----------------
VOSK_MODELS = {
    "en": "vosk-model-small-en-us-0.15",
    "hi": "vosk-model-small-hi-0.22",
    "te": "vosk-model-te-0.4",
    "ta": "vosk-model-ta-0.1",
    "kn": "vosk-model-kn-0.5",
    "ml": "vosk-model-ml-0.4",
    "bn": "vosk-model-bn-0.1",
    "gu": "vosk-model-gu-0.4",
    "pa": "vosk-model-pa-0.5",
    "mr": "vosk-model-mr-0.4",
    "ur": "vosk-model-ur-pk-0.1",
    "or": "vosk-model-or-0.1",
    "as": "vosk-model-as-0.1",
}

# ---------------- Crop Disease Model ----------------
MODEL_PATH = 'models/crop_disease_model.pth'
LABELS_PATH = 'models/disease_labels.json'

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
try:
    disease_model = torch.load(MODEL_PATH, map_location=device)
    disease_model.eval()
    with open(LABELS_PATH, 'r') as f:
        disease_labels = json.load(f)
except Exception as e:
    print("Error loading crop disease model:", e)
    disease_model = None
    disease_labels = []

image_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

# ---------------- Helper Functions ----------------
def t(text):
    lang = session.get("lang", "en")
    if lang == "en":
        return text
    try:
        return translator.translate(text, dest=lang).text
    except:
        return text

def detect_crop_disease(image_path):
    if disease_model is None:
        return {"crop": "Unknown", "status": "Model not loaded", "confidence": "0%"}
    try:
        img = Image.open(image_path).convert('RGB')
        img_tensor = image_transforms(img).unsqueeze(0).to(device)
        with torch.no_grad():
            output = disease_model(img_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)[0]
        idx = torch.argmax(probs).item()
        confidence = probs[idx].item()
        label = disease_labels[idx]
        if '___' in label:
            crop_name, status = label.split('___')
            status = status.replace('_',' ').title()
        else:
            crop_name = 'Unknown'
            status = label.replace('_',' ').title()
        return {"crop": crop_name, "status": status, "confidence": f"{confidence*100:.2f}%"}
    except Exception as e:
        print("Disease detection error:", e)
        return {"crop": "Unknown", "status": "Error", "confidence": "0%"}

def load_soil_data():
    with open("soil_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_crop_data():
    crops = []
    with open("crop_data.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            crops.append(row)
    return crops

def get_crop_prices():
    return {"Rice":1800, "Wheat":2000, "Maize":1500, "Sugarcane":3200, "Cotton":5500}

def get_vosk_model(lang_code):
    model_name = VOSK_MODELS.get(lang_code, "vosk-model-small-en-us-0.15")
    model_path = os.path.join(os.getcwd(), "models", model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model not found at {model_path}")
    return Model(model_path)

def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode("utf-8")
    except:
        return ""

def get_soil_ph(lat, lon):
    try:
        response = requests.get(f"https://rest.soilgrids.org/query?lon={lon}&lat={lat}")
        data = response.json()
        ph = data.get("properties", {}).get("phh2o", {}).get("mean", {}).get("value", None)
        return ph
    except:
        return None

# ---------------- Load States/Districts ----------------
with open("states_districts.json", encoding="utf-8") as f:
    states_districts = json.load(f)["states"]

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def language_selection():
    if request.method == "POST":
        session["lang"] = request.form["language"]
        return redirect(url_for("index"))
    languages = {
        "en": "English",
        "hi": "हिन्दी",
        "te": "తెలుగు",
        "ta": "தமிழ்",
        "kn": "ಕನ್ನಡ",
        "ml": "മലയാളം",
        "bn": "বাংলা",
        "gu": "ગુજરાતી",
        "pa": "ਪੰਜਾਬੀ",
        "mr": "मराठी",
        "ur": "اردو",
        "or": "ଓଡ଼ିଆ",
        "as": "অসমীয়া"
    }
    return render_template("language.html", languages=languages, t=t)

@app.route("/index")
def index():
    return render_template("index.html", t=t, states_districts=states_districts, states_districts_json=json.dumps(states_districts))

@app.route("/recommend", methods=["POST"])
def recommend():
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    state = request.form.get("state")
    district = request.form.get("district")

    soil_data = load_soil_data()
    crops = load_crop_data()
    prices = get_crop_prices()
    recommendations = []

    avg_ph = None
    climate = None

    if lat and lon:
        ph = get_soil_ph(float(lat), float(lon))
        if ph:
            avg_ph = ph

    if avg_ph is None and state and district:
        region = soil_data.get(state, [])
        matched = [d for d in region if d["name"].lower().strip() == district.lower().strip()]
        if matched:
            avg_ph = float(matched[0].get("ph", 0))
            climate = matched[0].get("climate", "").strip()

    for crop in crops:
        try:
            ph_req = float(crop.get("ph", 0))
            crop_climate = crop.get("climate", "").strip().lower()
            if avg_ph is None:
                continue
            if abs(ph_req - avg_ph) <= 0.5 and (climate is None or crop_climate == climate.lower()):
                crop_name = crop.get("crop", "")
                price = prices.get(crop_name, "N/A")
                recommendations.append({"crop": crop_name, "price": price, "climate": climate or crop_climate})
        except:
            continue

    return render_template("index.html", t=t, states_districts=states_districts, states_districts_json=json.dumps(states_districts), recommendations=recommendations)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.form.get("message", "")
    if not user_msg.strip():
        return jsonify({"reply": t("Please type something."), "audio": ""})
    reply = f"You said: {user_msg}"
    lang = session.get("lang", "en")
    if lang != "en":
        try:
            reply = translator.translate(reply, dest=lang).text
        except:
            pass
    audio = speak(reply, lang)
    return jsonify({"reply": reply, "audio": audio})

@app.route("/voice", methods=["POST"])
def voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"})
    file = request.files["file"]
    filepath = os.path.join("static", "uploads", "voice.webm")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    wav_path = filepath.replace(".webm", ".wav")
    os.system(f"ffmpeg -i {filepath} -ar 16000 -ac 1 {wav_path} -y")

    lang = session.get("lang", "en")
    try:
        vosk_model = get_vosk_model(lang)
    except Exception as e:
        return jsonify({"error": str(e)})

    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())
    spoken_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            spoken_text += " " + result.get("text", "")
    wf.close()
    spoken_text = spoken_text.strip()
    if not spoken_text:
        return jsonify({"error": t("Could not recognize speech")})

    reply = f"You said: {spoken_text}"
    if lang != "en":
        try:
            reply = translator.translate(reply, dest=lang).text
        except:
            pass
    audio = speak(reply, lang)
    return jsonify({"reply": reply, "audio": audio})

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": t("No file uploaded")})
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join("static", "uploads", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    result = detect_crop_disease(filepath)
    result["crop"] = t(result["crop"])
    result["status"] = t(result["status"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
