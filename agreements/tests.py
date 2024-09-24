from unittest.mock import MagicMock
from django.test import TestCase
from .models import Agreements
import hashlib
import json
from datetime import datetime
class AgreementsModelTest(TestCase):
    def setUp(self):
        """Set up a test Agreement with fixed data."""
        self.agreement = Agreements.objects.create(
            date_created=datetime.now().date(),
            contract_duration=12,
            agreed_amount=100000,
            installment_schedule='Monthly',
            penalties_interest_rate=5,
            down_payment=20000,
        )
        self.agreement.save()
    def generate_agreement_hash(self):
        if not self.pk:
            raise ValueError("Agreement must be saved before generating a hash.")
        agreement_data = {
            'date_created': self.date_created.isoformat(),
            'contract_duration': self.contract_duration,
            'agreed_amount': self.agreed_amount,
            'installment_schedule': self.installment_schedule,
            'penalties_interest_rate': self.penalties_interest_rate,
            'down_payment': self.down_payment,
            'buyer_agreed': self.buyer_agreed,
            'seller_agreed': self.seller_agreed,
            'unique_id': self.pk,
            'terms_and_conditions': self.terms_and_conditions,
            'timestamp': datetime.now().isoformat(),
        }
        return hashlib.sha256(json.dumps(agreement_data, sort_keys=True).encode()).hexdigest()
    def test_update_on_transaction(self):
        """Test that updating on transaction updates fields correctly."""
        self.agreement.blockchain = MagicMock()
        transaction_amount = 5000
        self.agreement.update_on_transaction(transaction_amount)
        self.agreement.refresh_from_db()
        expected_transaction_count = 1
        expected_total_amount_made = 5000
        expected_remaining_amount = self.agreement.agreed_amount - expected_total_amount_made
        self.assertEqual(self.agreement.transaction_count, expected_transaction_count)
        self.assertEqual(self.agreement.total_amount_made, expected_total_amount_made)
        self.assertEqual(self.agreement.remaining_amount, expected_remaining_amount)
        self.assertTrue(self.agreement.transactions_history)
        self.assertEqual(len(self.agreement.transactions_history), expected_transaction_count)
        self.agreement.blockchain.add_transaction.assert_called_once()