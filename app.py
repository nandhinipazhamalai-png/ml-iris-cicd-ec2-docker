from flask import Flask, request, jsonify, render_template_string
import os
import joblib
import numpy as np

app = Flask(__name__)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
model = joblib.load(MODEL_PATH)

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Iris Flower Classifier</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 680px; margin: 40px auto; padding: 0 18px; background:#f5f7fb; color:#172033; }
    .card { background:white; border-radius:14px; padding:26px; box-shadow:0 6px 24px #15264a14; }
    h1 { margin-top:0; } p { line-height:1.5; color:#4b5563; }
    label { display:block; margin-top:14px; font-weight:bold; }
    input { width:100%; box-sizing:border-box; padding:11px; margin-top:6px; border:1px solid #ccd3df; border-radius:7px; }
    button { margin-top:20px; padding:12px 18px; background:#2457d6; color:white; border:0; border-radius:7px; cursor:pointer; font-weight:bold; }
    #result { margin-top:18px; padding:13px; background:#eef4ff; border-radius:8px; display:none; }
    code { background:#eef0f4; padding:2px 5px; border-radius:4px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Iris Flower Classification</h1>
    <p>Enter flower measurements in centimeters. The trained machine-learning model predicts the Iris species.</p>
    <form id="predict-form">
      <label>Sepal length (cm)<input name="sepal_length" type="number" step="any" min="0" value="5.1" required></label>
      <label>Sepal width (cm)<input name="sepal_width" type="number" step="any" min="0" value="3.5" required></label>
      <label>Petal length (cm)<input name="petal_length" type="number" step="any" min="0" value="1.4" required></label>
      <label>Petal width (cm)<input name="petal_width" type="number" step="any" min="0" value="0.2" required></label>
      <button type="submit">Predict flower type</button>
    </form>
    <div id="result" role="status"></div>
    <p>Health check: <a href="/health">/health</a> · API: <code>POST /predict</code></p>
  </div>
<script>
document.getElementById('predict-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries([...form.entries()].map(([k,v]) => [k, Number(v)]));
  const box = document.getElementById('result');
  box.style.display = 'block';
  box.textContent = 'Predicting...';
  try {
    const response = await fetch('/predict', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Prediction failed');
    box.textContent = 'Predicted species: ' + data.prediction;
  } catch (error) {
    box.textContent = 'Error: ' + error.message;
  }
});
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.get("/health")
def health():
    return jsonify(status="ok", service="iris-ml-classifier")

@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a JSON object with the four flower measurements."), 400
    fields = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    try:
        values = [float(data[field]) for field in fields]
        if not np.all(np.isfinite(values)) or any(value < 0 for value in values):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Provide four finite, non-negative numeric measurements."), 400
    prediction = model.predict([values])[0]
    return jsonify(prediction=str(prediction), inputs=dict(zip(fields, values)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
