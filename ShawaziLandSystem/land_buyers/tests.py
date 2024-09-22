from django.test import TestCase
from django.db import IntegrityError
from users.models import CustomUser
from land_buyers.models import LandBuyer
from lawyers.models import Lawyer

class LandBuyerModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+254700000000',
            first_name='John',
            last_name='Doe',
            password='testpassword'
        )
        self.lawyer = Lawyer.objects.create(
            user=CustomUser.objects.create_user(
                phone_number='+254700000001',
                first_name='Jane',
                last_name='Smith',
                password='lawyerpassword'
            ),
            firm='Test Law Firm'
        )

    def test_create_land_buyer(self):
        land_buyer = LandBuyer.objects.create(
            user=self.user,
            lawyer=self.lawyer,
            address='123 Test Street'
        )
        self.assertEqual(LandBuyer.objects.count(), 1)
        self.assertEqual(str(land_buyer), 'John - Doe')

    def test_land_buyer_without_lawyer(self):
        land_buyer = LandBuyer.objects.create(
            user=self.user,
            address='123 Test Street'
        )
        self.assertIsNone(land_buyer.lawyer)

    def test_land_buyer_unique_user(self):
        LandBuyer.objects.create(
            user=self.user,
            address='123 Test Street'
        )
        with self.assertRaises(IntegrityError):
            LandBuyer.objects.create(
                user=self.user,
                address='456 Another Street'
            )

    def test_land_buyer_address_max_length(self):
        max_length = LandBuyer._meta.get_field('address').max_length
        self.assertEqual(max_length, 30)