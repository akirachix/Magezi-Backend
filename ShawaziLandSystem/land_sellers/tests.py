# Test not working



from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.db import IntegrityError
from users.models import CustomUser
from land_sellers.models import LandSeller
from lawyers.models import Lawyer
from landDetails.models import LandDetails

class LandSellerModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+254700000000',
            first_name='Jane',
            last_name='Doe',
            password='testpassword'
        )
        self.lawyer = Lawyer.objects.create(
            user=CustomUser.objects.create_user(
                phone_number='+254700000001',
                first_name='John',
                last_name='Smith',
                password='lawyerpassword'
            ),
            firm='Test Law Firm'
        )
        # self.land_details = LandDetails.objects.create(
            # Add necessary fields for LandDetails
        # )

    def test_create_land_seller(self):
        land_seller = LandSeller.objects.create(
            user=self.user,
            lawyer=self.lawyer,
            address='123 Test Street',
            LandDetail=self.land_details
        )
        self.assertEqual(LandSeller.objects.count(), 1)
        self.assertEqual(str(land_seller), 'Jane - Doe')

    def test_land_seller_without_lawyer(self):
        land_seller = LandSeller.objects.create(
            user=self.user,
            address='123 Test Street'
        )
        self.assertIsNone(land_seller.lawyer)

    def test_land_seller_unique_user(self):
        LandSeller.objects.create(
            user=self.user,
            address='123 Test Street'
        )
        with self.assertRaises(IntegrityError):
            LandSeller.objects.create(
                user=self.user,
                address='456 Another Street'
            )

    def test_land_seller_address_max_length(self):
        max_length = LandSeller._meta.get_field('address').max_length
        self.assertEqual(max_length, 25)

    def test_land_seller_without_land_detail(self):
        land_seller = LandSeller.objects.create(
            user=self.user,
            address='123 Test Street'
        )
        self.assertIsNone(land_seller.LandDetail)