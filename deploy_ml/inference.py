"""
API de inferência para classificação de patologias da coluna vertebral.

Endpoints:
  GET  /health    -> verifica se a API está no ar
  POST /predict   -> recebe features e retorna a previsão do modelo
"""

import os
import joblib
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo.pkl")

try:
    _artifacts = joblib.load(MODEL_PATH)
    MODEL = _artifacts["model"]
    LABEL_ENCODER = _artifacts["label_encoder"]
except FileNotFoundError:
    raise RuntimeError(
        f"Model file not found: {MODEL_PATH}. "
        "Run train.py from the repository root to generate it."
    )
except (KeyError, Exception) as exc:
    raise RuntimeError(f"Failed to load model artifacts: {exc}") from exc

FEATURES = ["V1", "V2", "V3", "V4", "V5", "V6"]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        values = pd.DataFrame([[float(data[f]) for f in FEATURES]], columns=FEATURES)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid feature value: {exc}"}), 400

    prediction_idx = MODEL.predict(values)[0]
    prediction_label = LABEL_ENCODER.inverse_transform([prediction_idx])[0]

    probabilities = MODEL.predict_proba(values)[0]
    prob_dict = {
        label: round(float(prob), 4)
        for label, prob in zip(LABEL_ENCODER.classes_, probabilities)
    }

    return jsonify({"prediction": prediction_label, "probabilities": prob_dict}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
