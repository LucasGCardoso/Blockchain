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
    
    def is_chain_valid(self):
        """Checks if the chain is valid. """
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


app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    # Gather the previous block info.
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    previous_hash = blockchain.hash(previous_block)
    # Call the method to mine (search for the correct nounce).
    proof = blockchain.proof_of_work(previous_proof)
    # Creates a new block in the blockchain after finding the nounce.
    block = blockchain.create_block(proof, previous_hash)

    response = {'message': 'You just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}

    # Returns the response with some info and the HTTP Code 200.
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    if(blockchain.is_chain_valid()):
        return jsonify({'Message': 'The chain is Valid'}), 200
    return jsonify({'Message': 'The chain is Invalid'}), 200

app.run(host='0.0.0.0', port=5000)

