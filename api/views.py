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
        
        logging.info("Recurring donor: %s",  convert_string_to_bool(data.get('recurring_donor') ))
        
        # Make a prediction
        predicted_donation, predicted_date = predict_donation(
        total_donations= int(data.get('total_donations')) , 
        total_amount= int(data.get('total_amount')), 
        avg_donation= int( data.get('avg_donation')), 
        frequency= int(data.get('frequency')),
        last_donation_date= data.get('last_donation_date'), 
        preferred_payment_method= data.get('preferred_payment_method'),
        recurring_donor= convert_string_to_bool(data.get('recurring_donor')) , 
        campaign=str( data.get('campaign'))
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