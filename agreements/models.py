from django.db import models
from landDetails.models import LandDetails
from datetime import datetime
import hashlib
import json
from land_buyers.models import LandBuyer
from land_sellers.models import LandSeller
from lawyers.models import Lawyer
from decimal import Decimal
from django.core.exceptions import ValidationError
from transactions.blockchain import Blockchain
from users.models import CustomUser

class Agreements(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    parcel_number= models.ForeignKey(LandDetails,on_delete=models.CASCADE, null=True,blank=True,related_name='agreements' )
    seller = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name='agreements_as_seller')
    buyer = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name='agreements_as_buyer')
    lawyer = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name='agreements_as_lawyer')
    date_created = models.DateField(auto_now_add=True)
    contract_duration = models.PositiveSmallIntegerField()
    agreed_amount = models.PositiveIntegerField()
    down_payment = models.PositiveIntegerField()
    installment_schedule = models.TextField()
    penalties_interest_rate = models.PositiveIntegerField()
    buyer_agreed = models.BooleanField(default=False)
    seller_agreed = models.BooleanField(default=False)
    terms_and_conditions = models.TextField(default="No terms and conditions provided.")
    transaction_count = models.PositiveIntegerField(default=0)
    remaining_amount = models.PositiveIntegerField(default=0)
    total_amount_made = models.PositiveIntegerField(default=0)
    agreement_hash = models.CharField(max_length=64, blank=True)
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    transactions_history = models.JSONField(default=list, blank=True)

    blockchain = Blockchain()
    
    def generate_hash(self, transaction_data):
        transaction_string = json.dumps(transaction_data, sort_keys=True).encode()
        return hashlib.sha256(transaction_string).hexdigest()
    
    def remaining_amount(self):
        return self.agreed_amount - self.down_payment
    
    def update_on_transaction(self, transaction_amount):
        self.transaction_count += 1
        self.total_amount_made +=transaction_amount
        self.remaining_amount = self.agreed_amount - self.total_amount_made
        transaction_data = {
            'amount': transaction_amount,
            'timestamp': datetime.now().isoformat(),
            'transaction_count': self.transaction_count,
        }

        previous_hash = None
        if self.transactions_history:
            previous_transaction = self.transactions_history[-1]
            previous_hash = previous_transaction['current_hash']
        current_hash = self.generate_hash(transaction_data)
        transaction_data['current_hash'] = current_hash
        transaction_data['previous_hash'] = previous_hash
        self.save()

        self.transactions_history.append(transaction_data)
        self.save(update_fields=['transactions_history'])
        self.add_transaction_to_blockchain(transaction_data)

    def add_transaction_to_blockchain(self, transaction):
        self.blockchain.add_transaction(transaction)

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
    
    def save(self, *args, **kwargs):
        if not self.parcel_number:
            raise ValidationError("Parcel number is required.")
        
        super().save(*args, **kwargs)

        if not self.agreement_hash:
            self.agreement_hash = self.generate_agreement_hash()
            super().save(update_fields=['agreement_hash'])

    def clean(self):
        if not self.parcel_number:
            raise ValidationError("Parcel number is required.")
        if self.agreed_amount <= 0:
            raise ValidationError("Agreed amount must be greater than zero.")
        if self.down_payment < 0:
            raise ValidationError("Down payment cannot be negative.")        

    def __str__(self):
                return f"Agreement ID: {self.id}, Amount: {self.agreed_amount}, Created: {self.date_created}"









