from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Transactions, Agreements
from users.models import CustomUser
from django.utils import timezone
from datetime import datetime

class TransactionsModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(first_name='John', last_name='Doe')

        # Include required fields for the agreement
        self.agreement = Agreements.objects.create(
            date_created='2023-01-01',
            terms_and_conditions='Sample terms',
            contract_duration=12,  # Assuming contract_duration is an integer
            agreed_amount=1000.0,  # Assuming agreed_amount is a float or integer
            penalties_interest_rate=5.0,  # Assuming penalties_interest_rate is a float
            down_payment=200.0  # Assuming down_payment is a float
        )

    def test_create_valid_transaction(self):
        naive_date = datetime(2023, 1, 1, 12, 0)
        aware_date = timezone.make_aware(naive_date)  # Convert naive datetime to aware datetime
        transaction = Transactions.objects.create(
            unique_code='TX123',
            amount=100.0,
            date=aware_date,  # Use timezone-aware datetime
            status='Pending',
            agreement=self.agreement,
            seller=self.user,
            buyer=self.user,
            lawyer=self.user
        )
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.status, 'Pending')

    def test_hash_generation(self):
        naive_date = datetime(2023, 1, 1, 12, 0)
        aware_date = timezone.make_aware(naive_date)  # Convert naive datetime to aware datetime
        transaction = Transactions.objects.create(
            unique_code='TX123',
            amount=100.0,
            date=aware_date,  # Use timezone-aware datetime
            status='Pending',
            agreement=self.agreement
        )
        expected_hash = transaction.generate_hash()
        self.assertIsNotNone(expected_hash)
        self.assertEqual(len(expected_hash), 64)  # SHA-256 hash length

    def test_transaction_with_invalid_agreement(self):
        naive_date = datetime(2023, 1, 1, 12, 0)
        aware_date = timezone.make_aware(naive_date)  # Convert naive datetime to aware datetime
        with self.assertRaises(ValidationError):
            Transactions.objects.create(
                unique_code='TX124',
                amount=100.0,
                date=aware_date,  # Use timezone-aware datetime
                status='Pending',
                agreement_id=9999,  # Non-existent ID
                seller=self.user,
                buyer=self.user,
                lawyer=self.user
            )

    def test_duplicate_transaction(self):
        naive_date = datetime(2023, 1, 1, 12, 0)
        aware_date = timezone.make_aware(naive_date)  # Convert naive datetime to aware datetime
        Transactions.objects.create(
            unique_code='TX125',
            amount=100.0,
            date=aware_date,  # Use timezone-aware datetime
            status='Pending',
            agreement=self.agreement,
            seller=self.user,
            buyer=self.user,
            lawyer=self.user
        )
        with self.assertRaises(ValidationError):
            Transactions.objects.create(
                unique_code='TX125',  # Same unique code
                amount=100.0,
                date=aware_date,  # Use timezone-aware datetime
                status='Pending',
                agreement=self.agreement,
                seller=self.user,
                buyer=self.user,
                lawyer=self.user
            )
