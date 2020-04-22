import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Creation du 1er block
        self.new_block(previous_hash=1, proof=100)

    #############################################################################
        
    def new_block(self, proof, previous_hash=None):
        """
        Creer un nouveau block dans la blockchain
        :param proof: <int> la preuve donnée par l'algoryhme de Preuve De Travail
        :param previous_hash: (Optional) <str> Hash du block précédent
        :return: <dict> Nouveau block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset la liste des transactions actuelle
        self.current_transactions = []

        self.chain.append(block)
        return block
    
    #############################################################################

    def new_transaction(self, sender, recipient, amount):
        """
        Créer une nouvelle transaction qui ira dans le prochain block miné
        :param sender: <str> Adresse de l'envoyeur
        :param recipient: <str> Adresse de reception
        :param amount: <int> Quantité
        :return: <int> L'index du block qui garde la transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    #############################################################################

    def proof_of_work(self, last_proof):
        """
        Algorithme de Preuve De Travail simple:
        - Trouve un nombre p' dont le hash(pp') termine par 4 zéros, où p est le p' précédent
        - p est la précédente preuve, et p' est la nouvelle preuve
        :param last_proof: <int>
        :return: <int>
        """ 

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

     #############################################################################
   
    @property
    def last_block(self):
        return self.chain[-1]

    #############################################################################


    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """

        #Il faut être sur que le Dictionnaire soit ordonné, sinon nous aurons des hashs improbable
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    #############################################################################

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valider la preuve: Est-ce que hash(last_proof, proof) termine par 4 zéros ?
        :param last_proof: <int> Preuve précédente
        :param proof: <int> Preuve actuelle
        :return: <bool> True si correcte, False si non correcte.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    #############################################################################


# Instanciation de notre noeud
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Génération d'une unique adresse globale pour ce noeud
node_identifier = str(uuid4()).replace('-','')

#Instanciation de la blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():


    # Nous faisons fonctionner l'algo de la Preuve De Travail pour avoir la prochaine preuve
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Nous devons recevoir une récompense pour avoir trouver la preuve
    # l'envoyeur est "0" ce qui signifie que ce node a miné un nouveau coin

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    # Créer le nouveau block en l'ajoutant dans la chaine
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Nouveau bloc créé",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Vérifie que les champs obligatoires sont présents
    required = ['sender', 'recipient', 'amount']
    if not all (k in values for k in required):
        return "Missing values", 400

    # Créer une nouvelle transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction sera ajouté au bloc {index}'}

    return jsonify(response),201
    

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'lenght':len(blockchain.chain)
    }
    return jsonify(response),200
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)