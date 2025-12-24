from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
DATA_FILE = "potholes.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- helpers ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- frontend ----------
@app.route("/")
def home():
    return send_from_directory("../Frontend", "index.html")

@app.route("/<path:path>")
def frontend_files(path):
    return send_from_directory("../Frontend", path)

# ---------- uploads ----------
@app.route("/uploads/<filename>")
def uploaded_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ---------- APIs ----------
@app.route("/report", methods=["POST"])
def report():
    image = request.files.get("image")
    severity = request.form.get("severity")
    lat = request.form.get("latitude")
    lng = request.form.get("longitude")

    if not image:
        return jsonify({"error": "Image missing"}), 400

    filename = f"{uuid.uuid4()}_{image.filename}"
    image.save(os.path.join(UPLOAD_FOLDER, filename))

    potholes = load_data()

    pothole = {
        "id": str(uuid.uuid4()),
        "latitude": lat,
        "longitude": lng,
        "severity": severity,
        "image": filename,
        "status": "Reported"
    }

    potholes.append(pothole)
    save_data(potholes)

    return jsonify({"message": "Reported", "data": pothole})

@app.route("/potholes")
def potholes():
    return jsonify(load_data())

# ---------- DELETE ----------
@app.route("/delete/<pothole_id>", methods=["DELETE"])
def delete_pothole(pothole_id):
    potholes = load_data()
    updated = []

    for p in potholes:
        if p["id"] == pothole_id:
            img_path = os.path.join(UPLOAD_FOLDER, p["image"])
            if os.path.exists(img_path):
                os.remove(img_path)
        else:
            updated.append(p)

    save_data(updated)
    return jsonify({"message": "Deleted successfully"})

# ---------- run ----------
if __name__ == "__main__":
    app.run(debug=True)
