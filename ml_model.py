import joblib
import logging

# Load pre-trained machine learning model
model = joblib.load('ml_model.pkl')

# Function to predict optimal configuration

def predict_optimal_config(features):
    try:
        prediction = model.predict([features])
        return prediction[0]
    except Exception as e:
        logging.error(f'Error in predict_optimal_config: {str(e)}')
        return None
