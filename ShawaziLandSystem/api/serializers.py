from rest_framework import serializers
from agreements.models import Agreements

class AgreementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreements
        fields = '__all__'
        