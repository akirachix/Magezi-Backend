from django.db import models
from django.core.exceptions import ValidationError
from agreements.models import Agreements
from transactions.blockchain import Blockchain
import hashlib

class Transactions(models.Model):
    unique_code = models.CharField(max_length=50)
    amount = models.FloatField(default=0.00)
    date = models.DateTimeField(null=True, blank=True)  
    status = models.CharField(max_length=10, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    agreement = models.ForeignKey(
        'agreements.Agreements',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=False, 
        blank=False,
        limit_choices_to={'is_active': True}
    )
    blockchain = Blockchain()
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    current_hash = models.CharField(max_length=64, blank=True, null=True)

    def clean(self):
        if not Agreements.objects.filter(id=self.agreement_id).exists():
            raise ValidationError(f"No agreement found with ID {self.agreement_id}")

        print("Checking for existing transactions...")
        existing_transactions = Transactions.objects.filter(
            agreement=self.agreement,
            unique_code=self.unique_code,
            amount=self.amount,
            date=self.date
        )
        print("Existing Transactions:", existing_transactions)

        if existing_transactions.exists():
            raise ValidationError("This transaction has already been recorded.")

    def save(self, *args, **kwargs):
        self.clean()

        if self.agreement.transactions.exists():
            last_transaction = self.agreement.transactions.last()
            self.previous_hash = last_transaction.current_hash

        self.current_hash = self.generate_hash()

        super().save(*args, **kwargs)

        self.agreement.update_on_transaction(self.amount)

    def generate_hash(self):
        transaction_string = f"{self.unique_code}{self.amount}{self.date.isoformat() if self.date else ''}{self.status}{self.previous_hash or ''}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def add_to_transaction_history(self):
        transaction_data = {
            'amount': self.amount,
            'timestamp': self.date.isoformat() if self.date else None,
            'transaction_count': self.agreement.transactions.count() + 1,  
        }
        
        if not hasattr(self.agreement, 'transactions_history'):
            self.agreement.transactions_history = []
        self.agreement.transactions_history.append(transaction_data)
        self.agreement.save(update_fields=['transactions_history'])

