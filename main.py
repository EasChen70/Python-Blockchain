import flask
import hashlib
from time import time

class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #Create genesis block
        self.new_block(previous_hash=1, proof=100)
    def new_block(self, proof, previous_hash=None):
        #Block structure, timestamp, list of transactions, proof, hash of prev block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'hash': previous_hash,
        }
        #Reset current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    #self, sender, recipient, amount
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        pass

    @property
    def last_block(self):
        #last index
        return self.chain[-1]
