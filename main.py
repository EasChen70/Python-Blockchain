from flask import Flask, jsonify, request
import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #Create genesis block
        self.new_block(previous_hash=1, proof=100)
        #set() is idempotent, meaning no matter how many times a specific node is added, it appears exactly once
        self.nodes = set()

    def register_node(self, address):
        #Add new node to list of nodes, takes address of node
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            #check if hash is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            #check if proof of work is correct
            if not self.validate_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        return True

    def consensus_algo(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                #check length
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
            #replace if found
            if new_chain:
                self.chain = new_chain
                return True
            
        return False

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
        #SHA-256 hash
        hash_obj = hashlib.sha256()
        #Order dictionary 
        block_string = json.dumps(block, sort_keys=True).encode()
        #Update hash object
        hash_obj.update(block_string)
        
        return hash_obj.hexdigest()

    @property
    def last_block(self):
        #last index
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        #Algorithm:
         #find a number 'p`' such that hash(x`) contains y amount of zeros, where p is the previous p`
         #p is the previous proof and p` is the new proof
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
             proof += 1
        return proof 

    @staticmethod
    def validate_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        #if last y amount of zeros is valid return.
        return guess_hash[:4] == "0000"

#instantiate Node
app = Flask(__name__)
    
node_identifier = str(uuid4()).replace('-','')

#instantiate Blockchain
blockchain = Blockchain()

@app.route('/mine', methods = ['GET'])
def mine():
    #Run Proof Of Work Algorithm
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #reward for finding proof
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    #forge new block
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Created",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['hash']
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    values = request.get_json()
    #verify information is present
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201 #status code for created

@app.route('/chain', methods = ['GET']) 
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    #200 http status ok
    return jsonify(response), 200

@app.route('/nodes/register', methods = ['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error, invalid list of Nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.consensus_algo()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
