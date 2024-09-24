from django.conf import settings
from rest_framework import serializers
from .models import LandDetails

class LandMapSerializer(serializers.ModelSerializer):
    map_url = serializers.SerializerMethodField()

    class Meta:
        model = LandDetails
        fields = ['map_url']

    def get_map_url(self, obj):
        if obj.latitude and obj.longitude:
            api_token = settings.OPENSTREETMAP_API_TOKEN
            center = f"{obj.latitude},{obj.longitude}"
            zoom = 15
            min_lat = obj.latitude - 0.01
            max_lat = obj.latitude + 0.01
            min_lon = obj.longitude - 0.01
            max_lon = obj.longitude + 0.01
            
            viewport_width = self.context.get('request').META.get('HTTP_CLIENT_REQUEST_WIDTH', 1920)
            width = int(viewport_width * 0.75)
            height = int(width * 16 / 9)

            url = (
                f"https://www.openstreetmap.org/export/embed.html"
                f"?bbox={min_lon},{min_lat},{max_lon},{max_lat}"
                f"&layer=mapnik"
                f"&zoom={zoom}"
                f"&width={width}"
                f"&height={height}"
                f"&center={center}"
                f"&marker={center}#marker"
            )

            url += "&margin-top=20&margin-bottom=20&margin-left=30&margin-right=30"

            if api_token:
                url += f"&token={api_token}"

            return url
        return None
