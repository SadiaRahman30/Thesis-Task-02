import os
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def load_model():
    try:
        import joblib
        return joblib.load(MODEL_PATH)
    except Exception:
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)


model = None


@app.before_request
def init_model():
    global model
    if model is None and os.path.exists(MODEL_PATH):
        model = load_model()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Automating ML Model Deployment: A CI/CD Pipeline with Jenkins, Docker, and AWS ECS",
        "status": "running"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


@app.route("/predict", methods=["POST"])
def predict():
    global model
    if model is None:
        model = load_model()

    data = request.get_json(force=True)
    features = data.get("features")
    if features is None:
        return jsonify({"error": "No features provided"}), 400

    if isinstance(features, list) and len(features) > 0:
        if not isinstance(features[0], list):
            features = [features]

    try:
        import numpy as np
        features_arr = np.array(features)
    except Exception:
        features_arr = features

    prediction = model.predict(features_arr)
    return jsonify({"prediction": int(prediction[0])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
