from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import csv
import os

# Load model
with open('final_xgb_smote_model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)

# Home page - form input
@app.route('/')
def home():
    return render_template('index.html')

# Prediction endpoint for web form
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get form values
        input_features = [
            float(request.form['air_temp']),
            float(request.form['process_temp']),
            float(request.form['rotational_speed']),
            float(request.form['torque']),
            float(request.form['tool_wear']),
            float(request.form['type_m']),
            float(request.form['type_h'])
        ]

        input_data = np.array(input_features).reshape(1, -1)

        # Predict
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]

        result_text = "⚡ Failure Predicted!" if prediction == 1 else "✅ Safe Operation."

        # Log prediction
        log_file = 'predictions.log.csv'
        file_exists = os.path.isfile(log_file)
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            # Write header if file is new
            if not file_exists or os.path.getsize(log_file) == 0:
                header = ['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear', 'type_m', 'type_h', 'prediction', 'probability']
                writer.writerow(header)
            # Write data
            log_data = input_features + [prediction, probability]
            writer.writerow(log_data)


        return render_template('index.html', prediction_text=f'{result_text} (Failure probability: {round(probability, 2)})')

if __name__ == '__main__':
    app.run(debug=True)
