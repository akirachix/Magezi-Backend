from django.test import TestCase
from agreements.models import Agreements
from users.models import CustomUser
from landDetails.models import LandDetails
from django.core.exceptions import ValidationError
from django.utils import timezone

class AgreementsModelTest(TestCase):

    def setUp(self):
        # Create users
        self.seller = CustomUser.objects.create_user(
            email='seller@example.com', 
            password='password123',
            phone_number='+254700000001',
            first_name='John',
            last_name='Doe'
        )
        self.buyer = CustomUser.objects.create_user(
            email='buyer@example.com', 
            password='password123',
            phone_number='+254700000002',
            first_name='Jane',
            last_name='Smith'
        )
        self.lawyer = CustomUser.objects.create_user(
            email='lawyer@example.com', 
            password='password123',
            phone_number='+254700000003',
            first_name='Emily',
            last_name='Johnson'
        )
        # Create land details with required fields
        self.land_details = LandDetails.objects.create(
            parcel_number='P123456',
            latitude=1.2921,  # Example latitude
            longitude=36.8219,  # Example longitude
            date_acquired=timezone.now()  # Example date
        )

    def test_create_valid_agreement(self):
        """Happy case: Create an agreement with valid data."""
        agreement = Agreements.objects.create(
            parcel_number=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer,
            agreed_amount=100000,
            down_payment=20000,
            total_amount_made=20000,
            contract_duration=12,
            installment_schedule="Monthly installments",
            penalties_interest_rate=5
        )
        # Check remaining amount
        self.assertEqual(agreement.remaining_amount, 80000)

    def test_create_invalid_agreement_no_agreed_amount(self):
        """Unhappy case: Try to create an agreement with invalid agreed amount."""
        with self.assertRaises(ValidationError):
            agreement = Agreements(
                parcel_number=self.land_details,
                seller=self.seller,
                buyer=self.buyer,
                lawyer=self.lawyer,
                agreed_amount=-100,  # Invalid agreed amount
                down_payment=0,
                contract_duration=12,
                installment_schedule="Monthly installments",
                penalties_interest_rate=5
            )
            agreement.clean()  # Trigger validation

    def test_create_invalid_agreement_no_parcel_number(self):
        """Unhappy case: Try to create an agreement without a parcel number."""
        with self.assertRaises(ValidationError):
            agreement = Agreements(
                seller=self.seller,
                buyer=self.buyer,
                lawyer=self.lawyer,
                agreed_amount=100000,
                down_payment=20000,
                contract_duration=12,
                installment_schedule="Monthly installments",
                penalties_interest_rate=5
            )
            agreement.clean()  # Trigger validation

    def test_create_invalid_agreement_no_seller(self):
        """Unhappy case: Try to create an agreement without a seller."""
        agreement = Agreements.objects.create(
            parcel_number=self.land_details,
            buyer=self.buyer,
            lawyer=self.lawyer,
            agreed_amount=100000,
            down_payment=20000,
            total_amount_made=20000,
            contract_duration=12,
            installment_schedule="Monthly installments",
            penalties_interest_rate=5
        )
        self.assertIsNone(agreement.seller)

    def test_transaction_update(self):
        """Test that transactions are correctly updating the agreement."""
        agreement = Agreements.objects.create(
            parcel_number=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer,
            agreed_amount=100000,
            down_payment=20000,
            total_amount_made=20000,
            contract_duration=12,
            installment_schedule="Monthly installments",
            penalties_interest_rate=5
        )
        # Perform transaction update
        agreement.update_on_transaction(10000)
        
        # Check if transaction count and total amount made are updated correctly
        self.assertEqual(agreement.transaction_count, 1)
        self.assertEqual(agreement.total_amount_made, 30000)
        self.assertEqual(agreement.remaining_amount, 70000.00)

    def test_invalid_down_payment(self):
        """Unhappy case: Try to create an agreement with negative down payment."""
        with self.assertRaises(ValidationError):
            agreement = Agreements(
                parcel_number=self.land_details,
                seller=self.seller,
                buyer=self.buyer,
                lawyer=self.lawyer,
                agreed_amount=100000,
                down_payment=-5000,  # Invalid down payment
                contract_duration=12,
                installment_schedule="Monthly installments",
                penalties_interest_rate=5
            )
            agreement.clean()  # Trigger validation

    def test_generate_agreement_hash(self):
        """Test that agreement hash is generated correctly."""
        agreement = Agreements.objects.create(
            parcel_number=self.land_details,
            seller=self.seller,
            buyer=self.buyer,
            lawyer=self.lawyer,
            agreed_amount=100000,
            down_payment=20000,
            total_amount_made=20000,
            contract_duration=12,
            installment_schedule="Monthly installments",
            penalties_interest_rate=5
        )
        # Ensure agreement hash is generated
        self.assertIsNotNone(agreement.agreement_hash)
