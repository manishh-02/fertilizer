from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# load dataset on startup (sampled for charts to keep responsiveness)
DATA_PATH = os.path.join(os.path.dirname(__file__), "dataset", "fertilizer_dataset_100k.csv")
df = pd.read_csv(DATA_PATH)

@app.route("/")
def index():
    # pass a small sample for client-side plotting options
    sample = df.sample(1000, random_state=1).to_dict(orient="records")
    crops = sorted(df['crop'].unique().tolist())
    locations = sorted(df['location'].unique().tolist())
    return render_template("index.html", sample_json=sample, crops=crops, locations=locations)

def compute_recommendation_manual(payload):
    crop = payload.get("crop", "Wheat")
    soil_n = float(payload.get("soil_n", 1000))
    soil_p = float(payload.get("soil_p", 200))
    soil_k = float(payload.get("soil_k", 800))
    organic_matter = float(payload.get("organic_matter", 2.5))
    rainfall = float(payload.get("annual_rainfall_mm", 900))
    temp = float(payload.get("avg_temp_c", 26))
    # baseline (same rules as dataset generation)
    baseline = {
        "Wheat": (120, 60, 40),
        "Rice": (160, 40, 40),
        "Maize": (140, 60, 60),
        "Sugarcane": (200, 100, 100),
        "Cotton": (100, 50, 40),
        "Soybean": (20, 40, 30),
        "Potato": (180, 60, 120),
        "Tomato": (120, 60, 80),
        "Chili": (80, 60, 60),
        "Mustard": (60, 30, 30)
    }
    N0, P0, K0 = baseline.get(crop, (100,50,50))
    n_adj = N0 * (1 - (soil_n - 1000)/8000)
    p_adj = P0 * (1 - (soil_p - 200)/2000)
    k_adj = K0 * (1 - (soil_k - 800)/8000)
    n_adj *= max(0.6, 1 - (organic_matter - 2.5)/10)
    if rainfall < 500:
        n_adj *= 1.05
        k_adj *= 1.05
    if temp > 32:
        k_adj *= 1.08
    N = float(round(max(0, n_adj),1))
    P = float(round(max(0, p_adj),1))
    K = float(round(max(0, k_adj),1))
    if N > 150 or K > 150:
        fert = "Complex NPK + Micronutrients"
    elif P < 30:
        fert = "P-rich (SSP/DAP) + balanced N"
    else:
        fert = "Balanced NPK"
    score = float(round(100 - (abs(N-N0)+abs(P-P0)+abs(K-K0))/3,1))
    return {"rec_N": N, "rec_P": P, "rec_K": K, "fertilizer_type": fert, "score": score}

@app.route("/predict", methods=["POST"])
def predict():
    payload = request.json or request.form.to_dict()
    res = compute_recommendation_manual(payload)
    return jsonify({"success": True, "recommendation": res})

@app.route("/api/summary")
def api_summary():
    # return aggregated stats for charts
    by_crop = df.groupby('crop').agg({"rec_N":"mean","rec_P":"mean","rec_K":"mean","score":"mean"}).reset_index().round(1)
    by_loc = df.groupby('location').agg({"rec_N":"mean","rec_P":"mean","rec_K":"mean"}).reset_index().round(1)
    out = {"by_crop": by_crop.to_dict(orient="records"), "by_location": by_loc.to_dict(orient="records")}
    return jsonify(out)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)