from agreements.models import Agreements
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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
    

    # def put(self, request, id):
    #     agreement = self.get_object(id)
    #     if agreement is not None:

    #         if hasattr(request.user, 'lawyer'):
    #             serializer = AgreementsSerializer(agreement, data=request.data)
    #             if serializer.is_valid():