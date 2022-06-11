import datetime
import hashlib
import json
from flask import Flask, jsonify


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        """Creates new block after mining."""
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)

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
