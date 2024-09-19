from rest_framework import serializers
<<<<<<< HEAD
from landDetails.models import LandDetails
from django.conf import settings


class LandDetailSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()  
    land_history = serializers.SerializerMethodField()  

    class Meta:
        model = LandDetails
        fields = ['land_details_id','parcel_number','date_acquired','land_description','price','owner_name','previous_owner','national_id','address','date_sold','date_purchased','location_name','latitude','longitude','position','land_history', 
        ]
        
    def get_position(self, obj):
        """ Method to serialize latitude and longitude """
        if obj.latitude and obj.longitude:
            return {'latitude': obj.latitude, 'longitude': obj.longitude}
        return None
    
    def get_land_history(self, obj):
        """ Method to serialize previous owner, sale date, and purchase date """
        history = {}
        if obj.previous_owner:
            history['owner'] = obj.previous_owner
        if obj.date_sold:
            history['date_sold'] = obj.date_sold
        if obj.date_purchased:
            history['date_purchased'] = obj.date_purchased
        return history if history else None
=======
from agreements.models import Agreements

class AgreementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreements
        fields = '__all__'
        
>>>>>>> origin/dev
