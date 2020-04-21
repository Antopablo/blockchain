import hashlib
import json
from time import time
from uuid import uuid4

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

    @property
    def last_block(self):
        return self.chain[-1]