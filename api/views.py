from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.response import Response
from .models import DonorProfile
from .ml_model import train_model, predict_donation

@api_view(['POST'])
def train(request):
    """Train ML Model using CSV"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=400)

    csv_file = request.FILES['file']
    
    try:
        train_model(csv_file)
        return Response({'message': 'Model trained successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@parser_classes([JSONParser])
def predict(request):
    """Predict next donation amount and date"""
    try:
        donor_id = request.data.get('donor_id')
        donor = get_object_or_404(DonorProfile, donor_id=donor_id)
        
        predicted_donation, next_donation_date = predict_donation(
            donor.total_donations,
            float(donor.total_amount),
            float(donor.avg_donation),
            donor.frequency,
            donor.last_donation_date,
            donor.preferred_payment_method,
            donor.recurring_donor,
            donor.campaign
        )
        
        donor.predicted_donation = predicted_donation
        donor.next_donation_date = next_donation_date
        donor.save()

        return Response({
            'donor_id': donor_id, 
            'predicted_donation': predicted_donation,
            'next_donation_date': next_donation_date
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)
