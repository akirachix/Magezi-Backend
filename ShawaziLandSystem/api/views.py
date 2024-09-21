from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from landDetails.models import LandDetails
from .serializers import LandDetailSerializer,TransactionsSerializer
from landDetails.maps import LandMapSerializer
from .models import Agreements
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.utils import send_in_system_notification
from datetime import datetime
from django.http import JsonResponse
from django.views.generic import TemplateView
from transactions.blockchain import Blockchain
from django.views.generic import ListView
from django.contrib import messages
from google.cloud import vision



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


""" This class handles detailed view and updates for specific land details """
class LandDetailView(APIView):
    def get(self, request, pk=None, format=None):
        """Get details for a specific land entry by ID or parcel number."""
        land_parcel_number = request.query_params.get('land_parcel_number')
        
        if pk:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
            except LandDetails.DoesNotExist:
                raise NotFound('The Land details do not exist')
        elif land_parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=land_parcel_number)
            except LandDetails.DoesNotExist:
                raise NotFound('The Land details do not exist')
        else:
            raise NotFound('No valid identifier provided')

        serializer = LandDetailSerializer(land_detail)
        return Response(serializer.data)

    def put(self, request, pk=None, format=None):
        """Update a specific land detail entry by ID or parcel number."""
        land_parcel_number = request.data.get('land_parcel_number')
        
        if pk:
            try:
                land_detail = LandDetails.objects.get(pk=pk)
            except LandDetails.DoesNotExist:
                raise NotFound('The Land details do not exist')
        elif land_parcel_number:
            try:
                land_detail = LandDetails.objects.get(parcel_number=land_parcel_number)
            except LandDetails.DoesNotExist:
                raise NotFound('The Land details do not exist')
        else:
            raise NotFound('No valid identifier provided')

        serializer = LandDetailSerializer(land_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class AgreementDetailView(APIView):
    def get_object(self, id):
        try:
            return Agreements.objects.get(agreement_id=id)  # Use the correct field name
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

class TransactionsListView(APIView):
    def get(self, request):
       transactions = Transactions.objects.all()
       serializer = TransactionsSerializer(transactions, many=True)
       return Response(serializer.data)

    def post(self, request):
        if 'buyerimage' not in request.FILES or 'sellerimage' not in request.FILES:
            return Response({"error": "Both files (buyerimage and sellerimage) must be provided"}, status=400)

        image_file1 = request.FILES['buyerimage']
        image_file2 = request.FILES['sellerimage']
        client = vision.ImageAnnotatorClient()

        def extract_data_from_image(image_file):
            try:
                image_content = image_file.read()
                image = vision.Image(content=image_content)
                response = client.text_detection(image=image)
                texts = response.text_annotations
                extracted_text = texts[0].description if texts else ""
            except Exception as e:
                raise ValueError(f"Failed to process image: {str(e)}")

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
            data1 = extract_data_from_image(image_file1)
            data2 = extract_data_from_image(image_file2)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        if all(k in data1 and k in data2 for k in ['amount', 'date', 'code']):
            try:
                amount1 = float(data1['amount'].replace(',', ''))
                amount2 = float(data2['amount'].replace(',', ''))
            except ValueError:
                return Response({"error": "Invalid amount format in one of the images"}, status=400)

            date1, date2 = data1['date'], data2['date']
            date_formats = ['%d/%m/%y', '%d/%m/%Y']
            date_obj1 = date_obj2 = None

            for fmt in date_formats:
                try:
                    date_obj1 = datetime.strptime(date1, fmt)
                    date_obj2 = datetime.strptime(date2, fmt)
                    break
                except ValueError:
                    continue

            if date_obj1 is None or date_obj2 is None:
                return Response({"error": "Date format is incorrect"}, status=400)

            formatted_date1 = date_obj1.strftime('%Y-%m-%d')
            formatted_date2 = date_obj2.strftime('%Y-%m-%d')

            if (amount1 == amount2 and
                formatted_date1 == formatted_date2 and
                data1['code'] == data2['code']):
                
                agreement_id = request.data.get('agreement_id')
                
                if agreement_id:
                    agreement = get_object_or_404(Agreements, id=agreement_id)
                else:
                  
                    agreement = Agreements.objects.create(
                        contract_duration=12,  
                        agreed_amount=amount1,  
                        installment_schedule="Monthly", 
                        penalties_interest_rate=5, 
                        down_payment=0,  
                    )

                try:
                    transaction, created = Transactions.objects.update_or_create(
                        unique_code=data1['code'],
                        defaults={
                            'amount': amount1,
                            'date': timezone.now(),
                            'status': 'complete',
                            'agreement': agreement
                        }
                    )
                    agreement.update_on_transaction(amount1)

                    message = "Transaction created and marked as complete" if created else "Transaction updated and marked as complete"
                except Exception as e:
                    return Response({"error": f"Failed to save transaction: {str(e)}"}, status=500)

                return Response({"message": message, "amount": amount1}, status=201)

            else:
                return Response({
                    "error": "The amounts, dates, or unique codes do not match",
                    "amount1": amount1,
                    "amount2": amount2,
                    "date1": formatted_date1,
                    "date2": formatted_date2,
                    "code1": data1['code'],
                    "code2": data2['code']
                }, status=400)
        else:
            return Response({"error": "Could not extract all required information from both images"}, status=400)


class TransactionsDetailView(APIView):
    def get(self,request,id):
            transactionss = Transactions.objects.get(id=id)
            serializer = TransactionsSerializer(transactionss)
            return Response(serializer.data)
    def delete(self,request,id):
            transactions =Transactions.objects.get(id=id)
            transactions.delete()
            return Response(status=status.HTTP_202_ACCEPTED)


class NotificationsListView(APIView):
    def get(self,request,land_id):
         property_details = get_object_or_404(Land,land_id=land_id)
         return render(request,'property_details.html',{
             'property':property_details,
         })
    def post(self, request):
        seller_id = request.data.get('seller_id')
        buyer = request.user
        seller = get_object_or_404(User, id=seller_id)

       
        property_name = request.data.get('name', 'a property')
        notification_message = f"Buyer {buyer.username} is interested in {property_name}."

        
        messages.success(request, notification_message)

        
        return render(request, 'notification_success.html', {
            "message": "Notification sent successfully!",
            "buyer": buyer.username,
            "property": property_name
        })

class PropertyListView(ListView):
    model = Land
    template_name = 'property_list.html'  
    context_object_name = 'properties'

class SellerNotificationView(TemplateView):
    template_name = 'seller_notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = messages.get_messages(self.request)  # Get the messages
        return context

class AgreementsView(APIView):
    def get(self, request):
        agreements = Agreements.objects.all()
        serializer = AgreementsSerializer(agreements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            agreement = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            room, created = Room.objects.get_or_create(room_name=room_name)
            return redirect('messages', room_name=room_name) 
    return render(request, 'index.html')

@login_required
def Message_View(request, room_name):
    room = Room.objects.get(room_name=room_name)

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:

            new_message = Message.objects.create(
                room=room,
                sender=request.user,  
                message=message_content
            )
            new_message.save()
            return redirect('messages', room_name=room_name) 

    messages = Message.objects.filter(room=room).order_by('-timestamp') 
    return render(request, 'message.html', {
        'room_name': room_name,
        'messages': messages,
        'user': request.user.username
    })

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
