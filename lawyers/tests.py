# okay



from django.test import TestCase

# Create your tests here.
from django.db import IntegrityError
from users.models import CustomUser
from lawyers.models import Lawyer

class LawyerModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+254700000000',
            first_name='John',
            last_name='Smith',
            password='testpassword'
        )

    def test_create_lawyer(self):
        lawyer = Lawyer.objects.create(
            user=self.user,
            firm='Test Law Firm'
        )
        self.assertEqual(Lawyer.objects.count(), 1)
        self.assertEqual(str(lawyer), 'John - Smith')

    def test_lawyer_unique_user(self):
        Lawyer.objects.create(
            user=self.user,
            firm='Test Law Firm'
        )
        with self.assertRaises(IntegrityError):
            Lawyer.objects.create(
                user=self.user,
                firm='Another Law Firm'
            )

    def test_lawyer_firm_max_length(self):
        max_length = Lawyer._meta.get_field('firm').max_length
        self.assertEqual(max_length, 25)