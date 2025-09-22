Fertilizer Recommendation App (Flask)
====================================

Contents:
- app.py : Flask application
- templates/index.html : front-end UI (Bootstrap + Chart.js)
- dataset/fertilizer_dataset_100k.csv : synthetic dataset with 100,000 records
- requirements.txt : Python dependencies

How to run locally:
1. Create and activate a virtualenv (recommended)
2. pip install -r requirements.txt
3. export FLASK_APP=app.py
4. flask run --host=0.0.0.0 --port=5000
5. Open http://127.0.0.1:5000 in your browser

NOTE: The dataset is synthetic and generated for demo and testing purposes only.