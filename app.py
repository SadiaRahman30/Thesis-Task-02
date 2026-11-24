import os
import sys
import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


class IrisClassifier:
    def predict(self, X):
        preds = []
        for row in X:
            petal_length = row[2]
            petal_width = row[3]
            if petal_length < 2.5:
                preds.append(0)
            elif petal_width < 1.75:
                preds.append(1)
            else:
                preds.append(2)
        return preds


# Ensure unpickler can always find IrisClassifier
if "__main__" in sys.modules:
    setattr(sys.modules["__main__"], "IrisClassifier", IrisClassifier)


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
    port = int(os.environ.get("PORT", 5001))
    print(f"Server starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port)
