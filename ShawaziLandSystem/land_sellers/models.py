from django.db import models

# Create your models here.
from users.models import CustomUser
from landDetails.models import LandDetails


class LandSeller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    lawyer = models.ForeignKey('lawyers.Lawyer', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=25)
    LandDetail = models.ForeignKey(LandDetails,on_delete=models.CASCADE, null=True,blank=True,related_name='seller_land_detail' )



    def __str__(self):
        return f"{self.user.first_name} - {self.user.last_name}"