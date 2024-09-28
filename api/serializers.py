from rest_framework import serializers
from landDetails.models import LandDetails
from transactions.models import Transactions
from agreements.models import Agreements
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model
import phonenumbers
from users.models import CustomUser
from chatroom.models import Room
from rest_framework import serializers
from chatroom.models import ChatMessage, Invitation, ChatRoom
from django.contrib.auth.models import Permission

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'user', 'content', 'timestamp']
        read_only_fields = ['user', 'timestamp']
class InvitationSerializer(serializers.ModelSerializer):
    invited_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Invitation
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']
class ChatRoomSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'users']
        read_only_fields = ['users']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__' 


User = get_user_model()

class CustomUserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'phone_number', 'password', 'role', 'permissions']

    def get_permissions(self, obj):
        return list(obj.user_permissions.values_list('codename', flat=True))

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

    def validate_phone_number(self, value):
        try:
            parsed_number = phonenumbers.parse(value, "KE")
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['permissions'] = self.get_permissions(instance)
        return ret


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
    seller_first_name = serializers.CharField(source='seller.first_name', read_only=True)
    buyer_first_name = serializers.CharField(source='buyer.first_name', read_only=True)
    lawyer_first_name = serializers.CharField(source='lawyer.first_name', read_only=True)

    class Meta:
        model = Agreements
        fields = [
            'agreement_id','parcel_number','seller','buyer','lawyer','seller_first_name','buyer_first_name',
            'lawyer_first_name','date_created','contract_duration','agreed_amount','installment_schedule',
            'penalties_interest_rate','down_payment','buyer_agreed','seller_agreed','terms_and_conditions',
            'transaction_count','remaining_amount','total_amount_made','agreement_hash','previous_hash',
            'transactions_history',
        ]

        
    def validate_parcel_number(self, value):
        """Ensure the parcel number exists in LandDetails."""
        if not LandDetails.objects.filter(parcel_number=value).exists():
            raise serializers.ValidationError("LandDetails with this parcel number does not exist.")
        return value
    
    def create(self, validated_data):
        parcel_number = validated_data.pop('parcel_number')
        land_detail = LandDetails.objects.get(parcel_number=parcel_number)
        agreement = Agreements.objects.create(
            parcel_number=land_detail,
            **validated_data
        )
        return agreement

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ['unique_code', 'amount', 'date', 'status', 'agreement', 'seller', 'buyer', 'lawyer']
    def validate_agreement(self, value):
        """ Ensure the agreement is valid """

        if not Agreements.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The agreement does not exist.")
        
        return value
    def create(self, validated_data):
        return Transactions.objects.create(**validated_data)
    
class BlockchainValidationSerializer(serializers.Serializer):
    validation_result = serializers.CharField()


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
    