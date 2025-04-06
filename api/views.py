from datetime import datetime
from joblib import Logger
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .ml_model import  predict_donation
import logging


@api_view(['POST'])
@parser_classes([JSONParser])
def predict(request):
    """Predict next donation amount and date"""
    try:
        # Get Request Data
        data = request.data
        
        logging.info(f"Received data: {data}")
        
    
        # Validate input data
        required_fields = ['total_donations', 'total_amount', 'avg_donation', 'frequency', 
                           'last_donation_date', 'preferred_payment_method', 'recurring_donor', 'campaign']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing required field: {field}'}, status=400)
        # Convert frequency to 1 if it is 0
        frequency = convert_frequency(data.get('frequency'))
        # Convert last_donation_date to a simple date string
        last_donation_date = format_last_donation_date(data.get('last_donation_date'))
        # Convert preferred_payment_method to a string and capitalize it
        preferred_payment_method = str(data.get('preferred_payment_method')).capitalize()
        # Convert recurring_donor to a boolean
        recurring_donor = convert_string_to_bool(data.get('recurring_donor'))
        # Convert campaign to a string
        campaign = str(data.get('campaign'))
        # Check if the last_donation_date is in the correct format
        try:
            datetime.fromisoformat(last_donation_date.replace('Z', ''))
        except ValueError:
            return Response({'error': 'Invalid date format for last_donation_date'}, status=400)
        # Check if the preferred_payment_method is a valid string
        if not isinstance(preferred_payment_method, str):
            return Response({'error': 'preferred_payment_method must be a string'}, status=400)
        # Check if the recurring_donor is a valid boolean
        if not isinstance(recurring_donor, bool):
            return Response({'error': 'recurring_donor must be a boolean'}, status=400)
        # Check if the campaign is a valid string
        if not isinstance(campaign, str):
            return Response({'error': 'campaign must be a string'}, status=400)
        # Check if the total_donations, total_amount, and avg_donation are valid integers
        if not all(isinstance(data.get(field), (int, float)) for field in ['total_donations', 'total_amount', 'avg_donation']):
            return Response({'error': 'total_donations, total_amount, and avg_donation must be integers or floats'}, status=400)
        # Check if the frequency is a valid integer
        if not isinstance(frequency, int):
            return Response({'error': 'frequency must be an integer'}, status=400)
        # Check if the last_donation_date is a valid date
        if not isinstance(last_donation_date, str):
            return Response({'error': 'last_donation_date must be a string'}, status=400)
        # Check if the preferred_payment_method is a valid string
        if not isinstance(preferred_payment_method, str):
            return Response({'error': 'preferred_payment_method must be a string'}, status=400)
        # Check if the recurring_donor is a valid boolean
        if not isinstance(recurring_donor, bool):
            return Response({'error': 'recurring_donor must be a boolean'}, status=400)
        # Check if the campaign is a valid string
        if not isinstance(campaign, str):
            return Response({'error': 'campaign must be a string'}, status=400)
        # Check if the last_donation_date is in the correct format
    
        
        
        # Make a prediction
        predicted_donation, predicted_date = predict_donation(
            total_donations=data.get('total_donations'),
            total_amount=data.get('total_amount'),
            avg_donation=data.get('avg_donation'),
            frequency=frequency,
            last_donation_date=last_donation_date,
            preferred_payment_method=preferred_payment_method,
            recurring_donor=recurring_donor,
            campaign=campaign
        )
        
        responseData = {
            'predicted_donation': predicted_donation,
            'next_donation_date': predicted_date
        }
       

        return Response(
            data=responseData,
            status=200
            )
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def convert_string_to_bool(value):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return None
    
    

def format_last_donation_date(iso_date_string):
    """
    Convert ISO format datetime string to simple date string (YYYY-MM-DD)
    
    Args:
        iso_date_string (str): Date string in ISO format (e.g., "2025-04-06T08:55:13.000000Z")
    
    Returns:
        str: Date in 'YYYY-MM-DD' format
    """
    try:
        # Parse the ISO format string to a datetime object
        dt = datetime.fromisoformat(iso_date_string.replace('Z', ''))
        # Format the datetime object to just the date part
        return dt.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        # Return the original string if parsing fails
        return iso_date_string
    
def convert_frequency(frequency):
    """
    Convert frequency from 0 to 1, leave other values unchanged
    
    Args:
        frequency (int): The frequency value
        
    Returns:
        int: 1 if input is 0, otherwise the original value
    """
    try:
        freq = int(frequency)
        return 1 if freq == 0 else freq
    except (ValueError, TypeError):
        # Return 1 if conversion fails (optional - you might want different handling)
        return 1