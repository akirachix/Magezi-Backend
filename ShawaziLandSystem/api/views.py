from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from landDetails.models import LandDetails
from .serializers import LandDetailSerializer
from landDetails.maps import LandMapSerializer
from .models import Agreements
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response



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
