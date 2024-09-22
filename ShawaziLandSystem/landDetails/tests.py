from django.test import TestCase
from django.utils import timezone
from .models import LandDetails

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class LandDetailsModelTest(TestCase):

  

    def test_validation_error(self):
        """Test that validation errors are raised for invalid data"""
        land = LandDetails(
            parcel_number='',  
            date_acquired=timezone.now().date(),
            owner_name='Babi',
            address='321 Korongo Road',
            location_name='Kiseriana',
            latitude=34.5678,
            longitude=87.6543
        )
        with self.assertRaises(ValidationError):
            land.full_clean()  
            land.save()  

    def test_unique_constraint(self):
        """Test that parcel_number must be unique"""
        LandDetails.objects.create(
            parcel_number='1234567890',
            date_acquired=timezone.now().date(),
            owner_name='John Daakii',
            address='123 KOrongo Street',
            location_name='Kiserian',
            latitude=12.3456,
            longitude=65.4321
        )
        with self.assertRaises(IntegrityError):
            LandDetails.objects.create(
                parcel_number='1234567890', 
                date_acquired=timezone.now().date(),
                owner_name='Alice',
                address='789 Korongo Street',
                location_name='Kiserian',
                latitude=23.4567,
                longitude=76.5432
            )

