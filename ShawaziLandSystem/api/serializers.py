from rest_framework import serializers
from landDetails.models import LandDetails
from transactions.models import Transactions
from agreements.models import Agreements
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
import phonenumbers
from users.models import CustomUser

User = get_user_model()


class CustomUserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'phone_number', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role=validated_data['role']
        )

    def validate_phone_number(self, value):
        try:
            parsed_number = phonenumbers.parse(value, "KE")
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'first_name', 'last_name', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)



class CustomUserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta: 
        model = CustomUser
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'is_active', 'permissions']

    def get_permissions(self, obj):
        return obj.user_permissions.values_list('codename', flat=True)


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

class AgreementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreements
        fields = '__all__'
class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'
class BlockchainValidationSerializer(serializers.Serializer):
    validation_result = serializers.CharField()
        

