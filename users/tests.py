from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from users.models import CustomUser

class CustomUserModelTests(TestCase):
    def setUp(self):
        self.phone_number = '+254113449867'
        self.first_name = 'Brenda'
        self.last_name = 'Khamali'
        self.password = 'khamali123'
    
    def test_create_user_with_valid_data(self):
        user = CustomUser.objects.create_user(
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password
        )

        self.assertEqual(user.phone_number, self.phone_number)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
    
    def test_create_superuser_with_valid_data(self):
        user = CustomUser.objects.create_superuser(
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, 'admin')
    
    def test_phone_number_validation_and_format(self):
        invalid_phone_number = '0700123456' 
        user = CustomUser(
            phone_number=invalid_phone_number,
            first_name=self.first_name,
            last_name=self.last_name
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()

        short_phone_number = '+25470' 
        user = CustomUser(
            phone_number=short_phone_number,
            first_name=self.first_name,
            last_name=self.last_name
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()

        long_phone_number = '+254700123456789' 
        user = CustomUser(
            phone_number=long_phone_number,
            first_name=self.first_name,
            last_name=self.last_name
        )
        
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_phone_number_uniquness(self):
        CustomUser.objects.create_user(
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password
        )
        
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                phone_number=self.phone_number,  
                first_name='Gloria',
                last_name='Nyaga',
                password='gloria123'
            )

    def test_is_phone_verified_default(self):
        user = CustomUser.objects.create_user(
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password
        )
        self.assertFalse(user.is_phone_verified)



