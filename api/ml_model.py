import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta

MODEL_FILE = 'ml_model.pkl'

# Train Model
def train_model(csv_file):
    df = pd.read_csv(csv_file)

    # Ensure necessary columns exist
    required_columns = ['donor_id', 'total_donations', 'total_amount', 'avg_donation', 'frequency',
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
    df = df.drop(columns=['donor_id', 'last_donation_date'])

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
    return "Models trained successfully."

# Predict donation amount and next donation date
def predict_donation(total_donations, total_amount, avg_donation, frequency, last_donation_date, 
                     preferred_payment_method, recurring_donor, campaign):
    model = joblib.load(MODEL_FILE)
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

    # Convert categorical fields to one-hot encoding
    for col in ['preferred_payment_method_CreditCard', 'preferred_payment_method_PayPal', 
                'preferred_payment_method_BankTransfer', 'campaign_A', 'campaign_B']:
        input_data[col] = 1 if col.split('_')[-1] in [preferred_payment_method, campaign] else 0

    input_df = pd.DataFrame([input_data])

    # Make predictions
    predicted_donation = donation_model.predict(input_df)[0]
    days_until_next_donation = int(date_model.predict(input_df)[0])
    predicted_next_donation_date = datetime.today() + timedelta(days=days_until_next_donation)

    return predicted_donation, predicted_next_donation_date.strftime('%Y-%m-%d')
