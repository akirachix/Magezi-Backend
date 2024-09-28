import json
import logging
import random
from django.shortcuts import get_object_or_404, redirect
import requests
import re
from django.conf import settings
from datetime import timedelta
from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from landDetails.models import LandDetails
from transactions.models import Transactions
from .serializers import AgreementsSerializer, BlockchainValidationSerializer, LandDetailSerializer,TransactionsSerializer
from landDetails.maps import LandMapSerializer
from agreements.models import Agreements
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.http import JsonResponse
from transactions.blockchain import Blockchain
from django.views.generic import ListView
from django.contrib import messages
from google.cloud import vision
from google.oauth2 import service_account
import json
import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import logout,get_user_model
from django.utils import timezone
from chatroom.models import Room, Message
from rest_framework import generics, status
from rest_framework.decorators import api_view
from django.contrib.auth.models import Permission
from .serializers import RoomSerializer
from users.models import CustomUser, RegistrationCode
from .serializers import (
    CustomUserCreationSerializer,
    CustomUserSerializer,
    UserSerializer,
)
from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import pika
import json
import logging
from chatroom.models import ChatRoom, ChatMessage
from django.utils.timezone import now
from datetime import timedelta
import requests

def get_google_vision_client():
    google_credentials_json = settings.GOOGLE_VISION_CREDENTIALS
    if google_credentials_json:
        try:
            google_credentials_dict = json.loads(google_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(google_credentials_dict)
            return vision.ImageAnnotatorClient(credentials=credentials)
        except json.JSONDecodeError as e:
            print(f"Error loading Google Vision credentials JSON: {e}")
    else:
        print("Google Vision credentials not found in environment variables.")
    return None
client = get_google_vision_client()
if client:
    pass
else:
    pass

User = get_user_model()
logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone_number, otp):
    headers = {
        "Authorization": f"Basic {settings.SMSLEOPARD_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "source": "Akirachix",
        "message": f"Your OTP code is {otp}",
        "destination": [{"number": phone_number}],
    }
    try:
        response = requests.post(settings.SMSLEOPARD_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"OTP sent successfully to {phone_number}. Response: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to send OTP: {str(e)}")
        return {"error": str(e)}


@api_view(['POST'])
def user_create(request):
    serializer = CustomUserCreationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save(is_active=False)  
        
        return Response({
            "message": "User registered successfully.",
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "permissions": serializer.data['permissions']
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    data = request.data
    phone_number = data.get('phone_number')
    password = data.get('password')

    if not phone_number or not password:
        return Response({"message": "Both phone number and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(phone_number=phone_number)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if user.check_password(password):
        otp = generate_otp()
        RegistrationCode.objects.create(
            phone_number=user.phone_number,
            code=otp,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        send_otp(user.phone_number, otp)

        return Response({
            "message": "Login successful. OTP has been sent to your phone.",
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_200_OK)
    else:
        return Response({"message": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)    



@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)






@api_view(['POST'])
def otp_verification(request):
    otp = request.data.get('otp')
    phone_number = request.data.get('phone_number')
    
    if not otp or not phone_number:
        return Response({"message": "OTP and phone number are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Received OTP verification request: Phone Number: {phone_number}, OTP: {otp}")
    
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        registration_code = RegistrationCode.objects.filter(phone_number=phone_number, code=otp).first()

        if not registration_code:
            logger.error(f"No registration code found for Phone Number: {phone_number} and OTP: {otp}")
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        if registration_code.expires_at < timezone.now():
            logger.error(f"OTP for Phone Number: {phone_number} has expired.")
            return Response({"message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        user.is_active = True
        user.is_phone_verified = True
        user.save()
        registration_code.delete()  
        
        return Response({
            "message": "OTP Verified Successfully. You can now log in to the system.",
            "first_name": user.first_name,
            "last_name": user.last_name,
        }, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        logger.error(f"User with phone number {phone_number} does not exist.")
        return Response({"message": "User with this phone number does not exist"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def password_reset_confirm(request):
    phone_number = request.data.get('phone_number')
    new_password = request.data.get('new_password')
    otp = request.data.get('otp')
    
    if not all([phone_number, new_password, otp]):
        return Response({"message": "Phone number, new password, and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        registration_code = RegistrationCode.objects.get(phone_number=phone_number, code=otp)
        
        if registration_code.expires_at < timezone.now():
            return Response({"message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.is_active = True
        user.save()
        registration_code.delete()
        
        return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
    
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except RegistrationCode.DoesNotExist:
        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def home(request):
    if request.method == 'GET':
        return Response({'message': 'Welcome to the home page!'}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"message": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            return Response({
                'message': f'Welcome back, {user.first_name}!',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role, 
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def forgot_password(request):
    if len(request.data) != 1 or 'phone_number' not in request.data:
        return Response({"message": "Only phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response({"message": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        otp = generate_otp()
        RegistrationCode.objects.create(
            phone_number=user.phone_number,
            code=otp,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        send_otp(user.phone_number, otp)
        
        return Response({
            "message": "Password reset OTP has been sent to your phone.",
            "phone_number": user.phone_number
        }, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def reset_password(request):
    data = request.data
    phone_number = data.get('phone_number')
    otp = data.get('otp')
    new_password = data.get('new_password')

    if not all([phone_number, otp, new_password]):
        return Response({"message": "Phone number, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        registration_code = RegistrationCode.objects.get(phone_number=phone_number, code=otp)
        
        if timezone.now() + timedelta(seconds=50) > registration_code.expires_at:
            registration_code.delete()
            return Response({"message": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        registration_code.delete()
        
        return Response({"message": "Password has been reset successfully. You can now login with your new password."}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except RegistrationCode.DoesNotExist:
        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    


class UserProfileAPIView(APIView):

    def get_user_data(self, user):
        permissions = Permission.objects.filter(user=user).values_list('codename', flat=True)
        return {
            'id': user.id,
            'phone_number': user.phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'role': user.role,
            'permissions': list(permissions)
        }

    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=user_id)
        user_data = self.get_user_data(user)
        return Response(user_data)

    

class RegisteredUsersView(APIView):
    def get_user_data(self, user):
        permissions = user.user_permissions.values_list('codename', flat=True)
        return {
            'id': user.id,
            'phone_number': user.phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'role': user.role,
            'permissions': list(permissions)
        }

    def get(self, request, user_id=None):
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                return Response(self.get_user_data(user))
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = CustomUser.objects.all()  

            user_data = [self.get_user_data(user) for user in users]
            return Response(user_data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.get_user_data(user), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def count(self, request):
        payment_count = CustomUser.objects.count() 
        return Response({"count": payment_count}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer      



""" This class is used to list all land details and to create a new land detail"""
class LandListView(APIView):
    def get(self, request, format=None):
        """Retrieve a list of all land properties."""
        properties = LandDetails.objects.all()
        serializer = LandDetailSerializer(properties, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Create a new land detail entry."""
        serializer = LandDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def count(self, request):
        payment_count = User.objects.count() 
        return Response({"count": payment_count}, status=status.HTTP_200_OK)


""" This class handles detailed view and updates for specific land details """
class LandDetailView(APIView):
    def get(self, request, format=None):
        parcel_number = request.query_params.get('parcel_number')
        pk = request.query_params.get('pk')
        # Check for parcel_number first
        if parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=parcel_number)
                serializer = LandDetailSerializer(land_detail)
                return Response(serializer.data)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided parcel number do not exist"}, status=status.HTTP_404_NOT_FOUND)
        if pk:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
                serializer = LandDetailSerializer(land_detail)
                return Response(serializer.data)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided ID do not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "No valid identifier provided"}, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk=None, format=None):
        if pk is not None:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided ID do not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = LandDetailSerializer(land_detail, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        parcel_number = request.data.get('parcel_number')
        if parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=parcel_number)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided parcel number do not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = LandDetailSerializer(land_detail, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No valid identifier provided"}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, pk=None, format=None):
        if pk is not None:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided ID do not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = LandDetailSerializer(land_detail, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        parcel_number = request.data.get('parcel_number')
        if parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=parcel_number)
            except LandDetails.DoesNotExist:
                return Response({"error": "The land details with the provided parcel number do not exist"}, status=status.HTTP_404_NOT_FOUND)
            serializer = LandDetailSerializer(land_detail, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "No valid identifier provided"}, status=status.HTTP_400_BAD_REQUEST)

""" This view handles the list and create functionality for land map details """
class LandMapListView(viewsets.ModelViewSet):
    queryset = LandDetails.objects.all()
    serializer_class = LandMapSerializer

    def get_queryset(self):
        """Filter queryset to include only records with latitude and longitude."""
        return LandDetails.objects.filter(latitude__isnull=False, longitude__isnull=False)

    def perform_create(self, serializer):
        """Override create method to set latitude and longitude."""
        serializer.save(latitude=self.request.data.get('latitude'), longitude=self.request.data.get('longitude'))



""" This view handles retrieving land map details either by primary key or parcel number """
class LandMapDetailView(APIView):
    def get(self, request, pk=None, format=None):
        """Retrieve land details by ID or land parcel number."""
        land_parcel_number = request.query_params.get('land_parcel_number')
        
        if pk:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
            except LandDetails.DoesNotExist:
                return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        elif land_parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=land_parcel_number)
            except LandDetails.DoesNotExist:
                return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'No identifier provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LandMapSerializer(land_detail, context={'request': request})
        return Response(serializer.data)


class AgreementsView(APIView):
    def get(self, request):
        agreements = Agreements.objects.all()
        serializer = AgreementsSerializer(agreements, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = AgreementsSerializer(data=request.data)
        if serializer.is_valid():
            agreement = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def count(self, request):
        payment_count = Agreements.objects.count()
        return Response({"count": payment_count}, status=status.HTTP_200_OK)
    
class AgreementDetailView(APIView):
    def get_object(self, id):
        try:
            return Agreements.objects.get(agreement_id=id)
        except Agreements.DoesNotExist:
            return None
    def get(self, request, id):
        agreement = self.get_object(id)
        if agreement is not None:
            serializer = AgreementsSerializer(agreement)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    def put(self, request, id):
        agreement = self.get_object(id)
        if agreement is not None:
            if hasattr(request.user, 'lawyer'):
                serializer = AgreementsSerializer(agreement, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Only lawyers can update agreements"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "Agreement not found"}, status=status.HTTP_404_NOT_FOUND)




class AgreementResponseView(APIView):
    def post(self, request, id):
        agreement = Agreements.objects.filter(agreement_id=id).first()
        if not agreement:
            return Response({"detail": "Agreement not found."}, status=status.HTTP_404_NOT_FOUND)

        buyer_agreed = request.data.get('buyer_agreed', agreement.buyer_agreed)
        seller_agreed = request.data.get('seller_agreed', agreement.seller_agreed)

        # Update agreement status
        agreement.buyer_agreed = buyer_agreed
        agreement.seller_agreed = seller_agreed
        agreement.save()

        return Response({
            "detail": "Agreement response submitted.",
            "buyer_agreed": agreement.buyer_agreed,
            "seller_agreed": agreement.seller_agreed
        }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def update_agreement(request, agreement_id):
    try:
        agreement = Agreements.objects.get(agreement_id=agreement_id)
    except Agreements.DoesNotExist:
        return Response({"error": "Agreement not found"}, status=status.HTTP_404_NOT_FOUND)

    if 'buyer_agreed' in request.data:
        agreement.buyer_agreed = request.data['buyer_agreed']
    if 'seller_agreed' in request.data:
        agreement.seller_agreed = request.data['seller_agreed']

    agreement.save()
    serializer = AgreementsSerializer(agreement)
    return Response(serializer.data, status=status.HTTP_200_OK)



class TransactionsListView(APIView):
    def get(self, request):
        transactions = Transactions.objects.all()
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)
    def post(self, request):
        user_type = request.data.get('user_type')
        if not user_type:
            return Response({"error": "User type is required"}, status=status.HTTP_400_BAD_REQUEST)
        if user_type not in ['buyer', 'seller']:
            return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)
        image_key = f'{user_type}image'
        if image_key not in request.FILES:
            return Response({"error": f"{user_type.capitalize()} image must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        image_file = request.FILES[image_key]
        def extract_data_from_image(image_file):
            try:
                image_content = image_file.read()
                image = vision.Image(content=image_content)
                response = client.text_detection(image=image)
                texts = response.text_annotations
                extracted_text = texts[0].description if texts else ""
            except Exception as e:
                logger.error(f"Failed to process image: {str(e)}")
                raise ValueError("Failed to process image.")
            patterns = {
                'amount': [r'Ksh\s*([\d,]+\.\d{2})', r'KES\s*([\d,]+\.\d{2})'],
                'date': [r'on\s*(\d{1,2}/\d{1,2}/\d{2})', r'(\d{1,2}/\d{1,2}/\d{4})'],
                'code': [r'\b([A-Z0-9]{10})\b']
            }
            matches = {}
            for key, regex_list in patterns.items():
                for pattern in regex_list:
                    match = re.search(pattern, extracted_text)
                    if match:
                        matches[key] = match.group(1)
                        break
            return matches
        try:
            data = extract_data_from_image(image_file)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if all(k in data for k in ['amount', 'date', 'code']):
            try:
                amount = float(data['amount'].replace(',', ''))
            except ValueError:
                return Response({"error": "Invalid amount format in the image"}, status=status.HTTP_400_BAD_REQUEST)
            date = data['date']
            date_formats = ['%d/%m/%y', '%d/%m/%Y']
            date_obj = None
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date, fmt)
                    break
                except ValueError:
                    continue
            if date_obj is None:
                return Response({"error": "Date format is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            formatted_date = date_obj.strftime('%Y-%m-%d')
            agreement_id = request.data.get('agreement_id')
            if agreement_id:
                agreement = get_object_or_404(Agreements, pk=agreement_id)
                seller_instance = agreement.seller
                buyer_instance = agreement.buyer
                lawyer_instance = agreement.lawyer
            else:
                return Response({"error": "Agreement ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            transaction = Transactions.objects.filter(unique_code=data['code'], date=formatted_date, agreement=agreement).first()
            if transaction:
               
                if transaction.amount == amount:
                    transaction.status = 'Complete'
                    message = "Transaction updated and marked as complete"
                else:
                    transaction.status = 'Rejected'
                    message = "Transaction updated and marked as rejected"
                transaction.save()
            else:
               
                transaction = Transactions.objects.create(
                    unique_code=data['code'],
                    amount=amount,
                    date=date_obj,
                    status='Pending',  
                    agreement=agreement,
                    seller=seller_instance if user_type == 'seller' else None,
                    buyer=buyer_instance if user_type == 'buyer' else None,
                    lawyer=lawyer_instance
                )
                message = "Transaction created and marked as pending"
            return Response({"message": message, "amount": amount, "status": transaction.status}, status=status.HTTP_201_CREATED)
        return Response({"error": "Could not extract all required information from the image"}, status=status.HTTP_400_BAD_REQUEST)
        
class TransactionsDetailView(APIView):
    def get(self, request, id):
        transaction = get_object_or_404(Transactions, id=id)  
        serializer = TransactionsSerializer(transaction)
        return Response(serializer.data)



class CheckBlockchainView(APIView):
    def get(self, request):
        blockchain = Blockchain() 
        validation_result = blockchain.is_valid()

        serializer = BlockchainValidationSerializer(data={'validation_result': validation_result})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def Create_Room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room')
        if room_name:
            room_name, created = Room.objects.get_or_create(room_name=room_name)
            return redirect('messages', room_name=room_name)
    return render(request, 'index.html')

def RoomListView(request):
    rooms = Room.objects.all().values('id', 'room_name')
    return JsonResponse(list(rooms), safe=False)

@login_required
def Message_View(request, room_name):
    try:
        room = Room.objects.get(room_name=room_name)
    except Room.DoesNotExist:
        return Response({"error": "Room does not exist."}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        message_content = request.data.get('message')
        if not message_content:
            return Response({"error": "Message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        new_message = Message.objects.create(
            room=room,
            sender=request.user,
            message=message_content
        )
        new_message.save()
        response_data = {
            "id": new_message.id,
            "message": new_message.message,
            "sender": new_message.sender.username,
            "timestamp": new_message.timestamp.isoformat()
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
def Login_View(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')
def Index_View(request):
    return render(request, 'index.html')

class RoomCreateView(APIView):
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        rooms = Room.objects.all().values('id', 'room_name')
        return Response(list(rooms), status=status.HTTP_200_OK)



logger = logging.getLogger(__name__)
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        user_data = [{'id': user.id, 'username': user.username} for user in users]
        return Response({'users': user_data}, status=status.HTTP_200_OK)
def chat_message_view(request):
    users = User.objects.all()
    return render(request, 'chat/chat_message.html', {'users': users})

class ChatMessageListCreateView(APIView):
    def get(self, request):
        room_name = request.query_params.get('room_name')
        username = request.query_params.get('username')
        if not room_name:
            return Response({'error': 'room_name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        chat_room = get_object_or_404(ChatRoom, name=room_name)
        messages = ChatMessage.objects.filter(user__username=username) if username else ChatMessage.objects.all()
        messages = messages.order_by('timestamp')
        
        messages_data = [
            {
                'user': message.user.username,
                'message': message.content,
                'timestamp': message.timestamp.isoformat()
            }
            for message in messages
        ]
        return Response({'messages': messages_data}, status=status.HTTP_200_OK)

    def post(self, request):
        message_content = request.data.get('message')
        recipient_id = request.data.get('recipient_id')
        room_name = request.data.get('room_name')

        if not message_content or not recipient_id or not room_name:
            return Response({'error': 'message, recipient_id, and room_name are required'}, status=status.HTTP_400_BAD_REQUEST)

        message_data = {
            'user': "Guest",
            'message': message_content,
            'timestamp': now().isoformat(),  
            'recipient_id': recipient_id,
        }

        self.publish_message(message_data)

        return Response(message_data, status=status.HTTP_201_CREATED)

    def publish_message(self, message):
        try:
            room_group_name = f'chat_{message["recipient_id"]}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'user': message['user'],
                        'message': message['message'],
                        'timestamp': message['timestamp'],
                        'recipient_id': message['recipient_id'],
                    }
                }
            )
            logger.info(f"Message sent to WebSocket group {room_group_name}: {message}")
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")

class SendInvitationView(APIView):
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')

        if not all([first_name, last_name, phone_number]):
            return Response({'error': 'First name, last name, and phone number are required'}, status=status.HTTP_400_BAD_REQUEST)

        expiry_date = now() + timedelta(days=2)
        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello {first_name} {last_name}, you've been invited to join Shawazi. This invitation expires on {expiry_date_formatted}. Please check your app for more details."

        sms_response = send_sms(phone_number, message)
        if 'error' in sms_response:
            logger.error(f"SMS sending failed: {sms_response['error']}")
            return Response({'status': 'Invitation created, but SMS failed', 'sms_response': sms_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'Invitation SMS sent', 'sms_response': sms_response, 'expires_at': expiry_date_formatted}, status=status.HTTP_200_OK)

def send_sms(phone_number, message):
    headers = {
        "Authorization": f"Basic {settings.SMSLEOPARD_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "source": "Akirachix",
        "message": message,
        "destination": [{"number": phone_number}],
    }
    try:
        response = requests.post(settings.SMSLEOPARD_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"SMS sent successfully to {phone_number}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return {"error": str(e)}

def chat_room(request, room_name):
    users = User.objects.all()
    return render(request, 'chat_room.html', {
        'room_name': room_name,
        'users': users
    })
