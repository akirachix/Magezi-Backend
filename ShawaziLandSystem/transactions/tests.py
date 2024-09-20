from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from agreements.models import Agreements
from .models import Transactions

class TransactionsModelTest(TestCase):

    def setUp(self):
        self.agreement = Agreements.objects.create(
            contract_duration=12,
            agreed_amount=1000,
            installment_schedule="Monthly",
            penalties_interest_rate=5,
            down_payment=0,
        )

    def test_create_transaction(self):
        transaction = Transactions.objects.create(
            unique_code="abc123",
            amount=100.0,
            date=timezone.now(), 
            status='Pending',
            agreement=self.agreement
        )
        self.assertIsNotNone(transaction.id)
        self.assertEqual(transaction.unique_code, "abc123")
        self.assertEqual(transaction.amount, 100.0)

    def test_duplicate_transaction(self):
        Transactions.objects.create(
            unique_code="abc123",
            amount=100.0,
            date=timezone.now(),  
            status='Pending',
            agreement=self.agreement
        )

        existing_transactions = Transactions.objects.filter(agreement=self.agreement)
        print("Existing Transactions before duplicate check:", existing_transactions)

        duplicate_transaction = Transactions(
            unique_code="abc123",
            amount=100.0,
            date=existing_transactions.first().date,  
            status='Pending',
            agreement=self.agreement
        )

        with self.assertRaises(ValidationError) as context:
            duplicate_transaction.clean() 

        self.assertIn("This transaction has already been recorded.", str(context.exception))

    def test_invalid_agreement(self):
        transaction = Transactions(
            unique_code="xyz789",
            amount=200.0,
            date=timezone.now(),
            status='Pending',
            agreement_id=999  
        )
        
        with self.assertRaises(ValidationError) as context:
            transaction.clean()  

        self.assertIn("No agreement found with ID 999", str(context.exception))

    def test_previous_hash_assignment(self):
        transaction1 = Transactions.objects.create(
            unique_code="first",
            amount=50.0,
            date=timezone.now(),
            status='Pending',
            agreement=self.agreement
        )
        
        transaction2 = Transactions.objects.create(
            unique_code="second",
            amount=75.0,
            date=timezone.now(),
            status='Pending',
            agreement=self.agreement
        )

        self.assertEqual(transaction2.previous_hash, transaction1.current_hash)

    def test_transaction_history_update(self):
        transaction = Transactions.objects.create(
            unique_code="abc123",
            amount=100.0,
            date=timezone.now(),
            status='Pending',
            agreement=self.agreement
        )

       
        self.assertEqual(len(self.agreement.transactions_history), 1)
        self.assertEqual(self.agreement.transactions_history[0]['amount'], 100.0)

