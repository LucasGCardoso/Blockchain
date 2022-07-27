"""The second version of the blockchain, adding the coin."""
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        """Creates new block after mining."""
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        """Gets previous block."""
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        """Searches and returns the nounce."""
        # new_proof is the nounce number
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                break
            new_proof += 1
        return new_proof

    def hash(self, block):
        """Encodes the block to a sha256 hash."""
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain=None):
        """Checks if the chain is valid. """
        if(chain is None):
            chain = self.chain
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]

            # Verify the previous hashes
            if block['previous_hash'] != self.hash(previous_block):
                return False

            # Verify if the block hash is valid, as well as the proof of work.
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            previous_block = block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        """Adds a transaction to a new block.

        Args:
            sender (str): The sender of the transaction
            receiver (str): The entity that will recevie the coins.
            amount (float): The amount of coins that will be sent.

        Returns:
            int: The index of the block that the transaction will be added to.
        """
        self.transactions.append(
            {'sender': sender,
             'receiver': receiver,
             'amount': amount}
        )
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        # EX: parsed url will be an object with sheme = http and netloc = 127.0.0.1:5000
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        """Replaces the chain if a bigger chain is found. Consensus Protocol.

        Returns:
            bool: Wheter the chain was replaced or not.
        """
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain is not None:
            self.chain = longest_chain
            return True
        return False


app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    # Gather the previous block info.
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = blockchain.hash(previous_block)
    # Call the method to mine (search for the correct nounce).
    proof = blockchain.proof_of_work(previous_proof)
    blockchain.add_transaction(sender=node_address, receiver='Lucas', amount=1)
    # Creates a new block in the blockchain after finding the nounce.
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'You just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}

    # Returns the response with some info and the HTTP Code 200.
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    if(blockchain.is_chain_valid()):
        return jsonify({'message': 'The chain is Valid'}), 200
    return jsonify({'message': 'The chain is Invalid'}), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'The transaction is invalid. Missing elements.', 400
    index = blockchain.add_transaction(
        json['sender'], json['receiver'], json['amount'])
    return jsonify({'message': f'Transaction will be added to block {index}'}), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if(nodes is None):
        return 'List of nodes is empty. No nodes passed.', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes were connected.',
                'nodes': list(blockchain.nodes),
                'total_nodes': len(list(blockchain.nodes))}
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    if(blockchain.replace_chain()):
        return jsonify({'message': 'Chain was replaced.', 'chain': blockchain.chain}), 200
    return jsonify({'message': 'Bigger chain not found. Chain was not replaced.', 'chain': blockchain.chain}), 200


app.run(host='0.0.0.0', port=5001)
