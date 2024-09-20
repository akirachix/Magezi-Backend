import hashlib
import json
from time import time

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions  
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []  
        self.current_transactions = []  
        self.create_block(previous_hash='1')  

    def create_block(self, previous_hash):
        block = Block(len(self.chain) + 1, time(), self.current_transactions, previous_hash)
        self.current_transactions = []  
        self.chain.append(block)  
        return block

    def add_transaction(self, transaction):
        transaction_date = transaction['timestamp'].split('T')[0]
        for t in self.current_transactions:
         existing_date = t['timestamp'].split('T')[0]
         if t['amount'] == transaction['amount'] and existing_date == transaction_date:
            return "Transaction with the same amount on this date already exists."


        self.current_transactions.append(transaction)
        return self.last_block.index + 1  

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None 

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.hash != current_block.calculate_hash():
                return False

        return True

    def is_valid(self):
        return "Valid blockchain" if self.validate_chain() else "Blockchain has been tampered with!"
