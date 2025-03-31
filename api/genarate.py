import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_donation_data(file_name, num_records=400):
    """Generate a synthetic donation data CSV file."""
    # Define possible values for categorical fields
    payment_methods = ['Cash','Mpesa']
    campaigns = [1, 2 ]
    
    # Generate synthetic data
    data = {
        'total_donations': np.random.randint(1, 50, size=num_records),
        'total_amount': np.random.uniform(100, 5000, size=num_records).round(2),
        'avg_donation': np.random.uniform(10, 500, size=num_records).round(2),
        'frequency': np.random.randint(1, 12, size=num_records),
        'last_donation_date': [datetime.today() - timedelta(days=np.random.randint(1, 365)) for _ in range(num_records)],
        'preferred_payment_method': [random.choice(payment_methods) for _ in range(num_records)],
        'recurring_donor': np.random.choice([True, False], size=num_records, p=[0.3, 0.7]),
        'campaign': [random.choice(campaigns) for _ in range(num_records)],
        'predicted_donation': np.random.uniform(10, 500, size=num_records).round(2),
        'next_donation_date': [datetime.today() + timedelta(days=np.random.randint(30, 365)) for _ in range(num_records)]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(file_name, index=False)
    print(f"Generated {num_records} records and saved to {file_name}")

# Example usage
generate_donation_data('donation_data.csv', num_records=400)