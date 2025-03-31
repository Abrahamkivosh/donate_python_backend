import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_FILE = 'ml_model.pkl'

def load_data(csv_file):
    """Load and preprocess the data."""
    df = pd.read_csv(csv_file)
    
    # Ensure necessary columns exist
    required_columns = [ 'total_donations', 'total_amount', 'avg_donation', 'frequency',
                        'last_donation_date', 'preferred_payment_method', 'recurring_donor', 'campaign',
                        'predicted_donation', 'next_donation_date']
    
    if not all(col in df.columns for col in required_columns):
        raise ValueError("CSV file must contain required columns.")
    
    # Convert categorical fields
    df = pd.get_dummies(df, columns=['preferred_payment_method', 'campaign'])
    
    # Convert date to numerical format (days since last donation)
    df['last_donation_date'] = pd.to_datetime(df['last_donation_date'])
    df['days_since_last_donation'] = (datetime.today() - df['last_donation_date']).dt.days
    
    # Drop unnecessary columns
    df = df.drop(columns=['last_donation_date'])
    
    return df

def train_model(csv_file):
    """Train the model and save it to a file."""
    df = load_data(csv_file)
    
    # Split features (X) and target labels (y)
    X = df.drop(columns=['predicted_donation', 'next_donation_date'])
    y_donation = df['predicted_donation']
    y_date = pd.to_datetime(df['next_donation_date']).apply(lambda x: (x - datetime.today()).days)
    
    # Train separate models
    donation_model = RandomForestRegressor(n_estimators=100, random_state=42)
    donation_model.fit(X, y_donation)
    
    date_model = RandomForestRegressor(n_estimators=100, random_state=42)
    date_model.fit(X, y_date)
    
    # Save models
    joblib.dump((donation_model, date_model), MODEL_FILE)
    logging.info("Models trained and saved successfully.")
    
    # Evaluate models
    evaluate_model(donation_model, date_model, X, y_donation, y_date)

def evaluate_model(donation_model, date_model, X, y_donation, y_date):
    """Evaluate the model's performance."""
    donation_preds = donation_model.predict(X)
    date_preds = date_model.predict(X)
    
    mae_donation = mean_absolute_error(y_donation, donation_preds)
    mae_date = mean_absolute_error(y_date, date_preds)
    
    logging.info(f"Donation Model MAE: {mae_donation}")
    logging.info(f"Date Model MAE: {mae_date}")

def predict_donation(total_donations, total_amount, avg_donation, frequency, last_donation_date, 
                     preferred_payment_method, recurring_donor, campaign):
    """Predict donation amount and next donation date."""
    try:
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        logging.error("Model file not found. Please train the model first.")
        return None, None
    
    donation_model, date_model = model
    
    # Convert categorical values
    input_data = {
        'total_donations': total_donations,
        'total_amount': total_amount,
        'avg_donation': avg_donation,
        'frequency': frequency,
        'days_since_last_donation': (datetime.today() - pd.to_datetime(last_donation_date)).days,
        'recurring_donor': int(recurring_donor)
    }
    
    # Dynamically handle one-hot encoding
    input_df = pd.DataFrame([input_data])
    
    # Add one-hot encoded columns for categorical variables
    for col in ['preferred_payment_method', 'campaign']:
        for category in donation_model.feature_names_in_:
            if col in category:
                input_df[category] = 1 if category.endswith(preferred_payment_method if col == "preferred_payment_method" else campaign) else 0
    
    # Ensure all columns are present and in the correct order
    input_df = input_df.reindex(columns=donation_model.feature_names_in_, fill_value=0)
    
    # Make predictions
    predicted_donation = donation_model.predict(input_df)[0]
    days_until_next_donation = int(date_model.predict(input_df)[0])
    predicted_next_donation_date = datetime.today() + timedelta(days=days_until_next_donation)
    
    return predicted_donation, predicted_next_donation_date.strftime('%Y-%m-%d')


if __name__ == "__main__":
    # Train the model (if not already trained)
    train_model('donation_data.csv')
    
    # Make a prediction
    predicted_donation, predicted_date = predict_donation(
        total_donations=10, 
        total_amount=2000, 
        avg_donation=50, 
        frequency=2,
        last_donation_date='2023-01-01', 
        preferred_payment_method='Mpesa',
        recurring_donor=True, 
        campaign="1"
    )
    logging.info(f"Predicted Donation: {predicted_donation}, Predicted Date: {predicted_date}")