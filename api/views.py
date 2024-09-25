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

# GOOGLE_VISION_CREDENTIALS = settings.GOOGLE_VISION_CREDENTIALS
# credentials =  vision.ImageAnnotatorClient(credentials=GOOGLE_VISION_CREDENTIALS)
client = vision.ImageAnnotatorClient(credentials=settings.GOOGLE_VISION_CREDENTIALS)


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
                agreement = get_object_or_404(Agreements, agreement_id=agreement_id) 
                seller_instance = agreement.seller
                buyer_instance = agreement.buyer
                lawyer_instance = agreement.lawyer 
            else:
                agreement = Agreements.objects.create(
                    contract_duration=12,
                    agreed_amount=amount,
                    installment_schedule="Monthly",
                    penalties_interest_rate=5,
                    down_payment=0,
                )
            try:
                transaction, created = Transactions.objects.update_or_create(
                    unique_code=data['code'],
                    defaults={
                        'amount': amount,
                        'date': timezone.now(),
                        'status': 'complete',  
                        'agreement': agreement,
                        'seller':seller_instance,
                        'buyer':buyer_instance,
                        'lawyer':lawyer_instance  
                    }
                )
                
                agreement.update_on_transaction(amount)
                message = "Transaction created and marked as complete" if created else "Transaction updated and marked as complete"
            except Exception as e:
                logger.error(f"Failed to save transaction: {str(e)}")
                return Response({"error": f"Failed to save transaction: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": message, "amount": amount}, status=status.HTTP_201_CREATED)
        else:
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
    # @csrf_exempt
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        rooms = Room.objects.all().values('id', 'room_name')
        return Response(list(rooms), status=status.HTTP_200_OK)




