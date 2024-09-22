from django.db import IntegrityError
from django.test import TestCase
from agreements.models import Agreements
from landDetails.models import LandDetails
from transactions.models import Transactions
from users.models import CustomUser

class TransactionsModelTest(TestCase):
    def setUp(self):
        # Adjust these fields to match your actual LandDetails model
        self.land_details = LandDetails.objects.create(
            title='Plot 123',  # Adjust field name
            size='500 acres',  # Adjust field name
            value=500000  # Adjust field name and value
        )

        self.seller = CustomUser.objects.create_user(
            phone_number='+254700000001',
            first_name='John',
            last_name='Doe',
            password='password123'
        )

        self.buyer = CustomUser.objects.create_user(
            phone_number='+254700000002',
            first_name='Jane',
            last_name='Smith',
            password='password123'
        )

        self.lawyer = CustomUser.objects.create_user(
            phone_number='+254700000003',
            first_name='Lawyer',
            last_name='Law',
            password='password123'
        )

        self.agreement = Agreements.objects.create(
            name='Agreement 001',  # Adjust the fields to match your Agreements model
            description='Land sale agreement',  # Adjust this as per your actual model fields
            is_active=True
        )

    def test_successful_transaction_creation(self):
        transaction = Transactions.objects.create(
            unique_code='TX123456789',
            amount=150000,
            date='2024-09-20 10:00:00',
            agreement_id=self.agreement,
            LandDetail=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer
        )
        self.assertEqual(transaction.unique_code, 'TX123456789')
        self.assertEqual(transaction.amount, 150000)
        self.assertEqual(transaction.agreement_id, self.agreement)
        self.assertEqual(transaction.LandDetail, self.land_details)
        self.assertEqual(transaction.seller, self.seller)
        self.assertEqual(transaction.buyer, self.buyer)
        self.assertEqual(transaction.lawyer, self.lawyer)
        self.assertEqual(transaction.status, 'Pending')

    def test_invalid_agreement(self):
        with self.assertRaises(IntegrityError):
            Transactions.objects.create(
                unique_code='TX987654321',
                amount=150000,
                date='2024-09-20 10:00:00',
                agreement_id=None,  # Invalid agreement, should raise an IntegrityError
                LandDetail=self.land_details,
                seller=self.seller,
                buyer=self.buyer,
                lawyer=self.lawyer
            )

    def test_invalid_hash_length(self):
        transaction = Transactions.objects.create(
            unique_code='TX987654321',
            amount=150000,
            date='2024-09-20 10:00:00',
            agreement_id=self.agreement,
            LandDetail=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer
        )
        transaction.current_hash = 'short'  # Invalid hash length

        with self.assertRaises(ValidationError):
            transaction.full_clean()  # ValidationError will be raised if the hash length is invalid

    def test_previous_hash_set_correctly(self):
        # Create the first transaction
        first_transaction = Transactions.objects.create(
            unique_code='TX111',
            amount=150000,
            date='2024-09-20 10:00:00',
            agreement_id=self.agreement,
            LandDetail=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer
        )

        # Create the second transaction; it should set the previous hash
        second_transaction = Transactions.objects.create(
            unique_code='TX222',
            amount=250000,
            date='2024-09-21 10:00:00',
            agreement_id=self.agreement,
            LandDetail=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer
        )

        # Ensure the second transaction has the correct previous hash
        self.assertEqual(second_transaction.previous_hash, first_transaction.current_hash)





























# from django.test import TestCase
# from django.core.exceptions import ValidationError
# from agreements.models import Agreements
# from landDetails.models import LandDetails
# from users.models import CustomUser
# from transactions.models import Transactions
# from datetime import datetime

# class TransactionsModelTest(TestCase):

#     def setUp(self):
#         """Set up test data for Transactions model."""
#         # Create test users
#         self.buyer = CustomUser.objects.create_user(username='buyer', password='password123')
#         self.seller = CustomUser.objects.create_user(username='seller', password='password456')
#         self.lawyer = CustomUser.objects.create_user(username='lawyer', password='password789')

#         # Create a test agreement
#         self.agreement = Agreements.objects.create(
#             buyer=self.buyer,
#             seller=self.seller,
#             is_active=True
#         )

#         # Create a test land detail
#         self.land_detail = LandDetails.objects.create(
#             address="123 Test St"
#         )

#     # Happy Cases
#     def test_create_transaction_happy_case(self):
#         """Test creating a valid transaction (happy case)."""
#         transaction = Transactions.objects.create(
#             unique_code="TX12345",
#             amount=10000.00,
#             date=datetime.now(),
#             status="Approved",
#             agreement=self.agreement,
#             LandDetail=self.land_detail,
#             seller=self.seller,
#             buyer=self.buyer,
#             lawyer=self.lawyer
#         )

#         # Check that the transaction is created correctly
#         self.assertEqual(transaction.unique_code, "TX12345")
#         self.assertEqual(transaction.amount, 10000.00)
#         self.assertEqual(transaction.status, "Approved")
#         self.assertEqual(transaction.agreement, self.agreement)
#         self.assertEqual(transaction.seller, self.seller)
#         self.assertEqual(transaction.buyer, self.buyer)
#         self.assertEqual(transaction.lawyer, self.lawyer)

#     def test_previous_and_current_hash_happy_case(self):
#         """Test that previous and current hashes are generated and linked correctly (happy case)."""
#         transaction1 = Transactions.objects.create(
#             unique_code="TX12345",
#             amount=10000.00,
#             date=datetime.now(),
#             status="Approved",
#             agreement=self.agreement,
#             LandDetail=self.land_detail,
#             seller=self.seller,
#             buyer=self.buyer,
#             lawyer=self.lawyer
#         )

#         transaction2 = Transactions.objects.create(
#             unique_code="TX12346",
#             amount=5000.00,
#             date=datetime.now(),
#             status="Approved",
#             agreement=self.agreement,
#             LandDetail=self.land_detail,
#             seller=self.seller,
#             buyer=self.buyer,
#             lawyer=self.lawyer
#         )

#         # Check that the previous hash in transaction2 matches transaction1's current hash
#         self.assertEqual(transaction2.previous_hash, transaction1.current_hash)

#     # Unhappy Cases
#     def test_create_transaction_with_invalid_agreement_unhappy_case(self):
#         """Test creating a transaction with an invalid agreement (unhappy case)."""
#         with self.assertRaises(ValidationError):
#             Transactions.objects.create(
#                 unique_code="TX12347",
#                 amount=10000.00,
#                 date=datetime.now(),
#                 status="Approved",
#                 agreement=None,  # Invalid agreement
#                 LandDetail=self.land_detail,
#                 seller=self.seller,
#                 buyer=self.buyer,
#                 lawyer=self.lawyer
#             )

#     def test_duplicate_transaction_unhappy_case(self):
#         """Test creating a duplicate transaction (unhappy case)."""
#         transaction = Transactions.objects.create(
#             unique_code="TX12348",
#             amount=10000.00,
#             date=datetime.now(),
#             status="Approved",
#             agreement=self.agreement,
#             LandDetail=self.land_detail,
#             seller=self.seller,
#             buyer=self.buyer,
#             lawyer=self.lawyer
#         )

#         with self.assertRaises(ValidationError):
#             # Try to create the same transaction again
#             Transactions.objects.create(
#                 unique_code="TX12348",  # Same unique code
#                 amount=10000.00,         # Same amount
#                 date=transaction.date,   # Same date
#                 status="Approved",
#                 agreement=self.agreement,
#                 LandDetail=self.land_detail,
#                 seller=self.seller,
#                 buyer=self.buyer,
#                 lawyer=self.lawyer
#             )

#     def test_create_transaction_missing_fields_unhappy_case(self):
#         """Test creating a transaction with missing mandatory fields (unhappy case)."""
#         with self.assertRaises(ValidationError):
#             Transactions.objects.create(
#                 unique_code="",
#                 amount=10000.00,
#                 date=datetime.now(),
#                 status="Approved",
#                 agreement=self.agreement,
#                 LandDetail=self.land_detail,
#                 seller=self.seller,
#                 buyer=None,  # Missing buyer
#                 lawyer=self.lawyer
#             )
