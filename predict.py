import pickle 
import pandas as pd 
from flask import Flask, request, jsonify

with open ('customer_churn_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

model_columns = [
    'gender', 'seniorcitizen', 'partner', 'dependents', 'tenure', 
    'phoneservice', 'multiplelines', 'internetservice', 'onlinesecurity', 
    'onlinebackup', 'deviceprotection', 'techsupport', 'streamingtv', 
    'streamingmovies', 'contract', 'paperlessbilling', 'monthlycharges', 
    'totalcharges', 'paymentmethod_credit card (automatic)', 
    'paymentmethod_electronic check', 'paymentmethod_mailed check'
]
app = Flask('churn')

@app.route('/')
def ping():
    return "Churn Prediction Service is Active", 200

@app.route('/predict', methods=['POST'])
def predict():
    customer = request.get_json()
    df = pd.DataFrame([customer])
    binary_cols = ['partner', 'dependents', 'phoneservice', 'paperlessbilling']

    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map({'yes': 1, 'no': 0})

    df = pd.get_dummies(df)
    df = df.reindex(columns=model_columns, fill_value=0)
    y_pred = loaded_model.predict_proba(df)[0][1]
    churn = y_pred >= 0.5
    result = {
        'churn_probability': float(y_pred),
        'churn': bool(churn)
    }
    return jsonify(result)
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)