from django.db import models
 

class LandDetails(models.Model):
    land_details_id = models.AutoField(primary_key=True)
    parcel_number = models.CharField(max_length=255, unique=True)
    date_acquired = models.DateField()
    land_description = models.TextField(default='No description provided')
    price = models.FloatField(default=0.0)
    owner_name = models.CharField(max_length=25)
    previous_owner = models.CharField(max_length=30, blank=True, null=True)
    national_id = models.CharField(max_length=20, default='0')  
    address = models.CharField(max_length=30)
    date_sold = models.DateField(blank=True, null=True)
    date_purchased = models.DateField(blank=True, null=True)
    location_name = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.address} currently owned by {self.owner_name}"

    objects = models.Manager()

