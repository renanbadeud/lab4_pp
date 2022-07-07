import hashlib

import attr
class Challenge:
    def __init__(self, transactionID, challenge, clientID=-1, seed=""):
        self.transactionID = transactionID
        self.challenge = challenge
        self.clientID = clientID
        self.seed = seed
    
    def hash_seed(seed):
        a = hashlib.sha1(seed.encode())
        
        b = a.hexdigest()
        print
        return str(bin(int(b, 16)))[2:]

    def check_seed(self, seed):
        if self.clientID != -1:
            return False 
        encoded_str = seed.encode()
        hash_obj = hashlib.sha1(encoded_str)
        hash = hash_obj.hexdigest()
        x=bin(int(hash, base=16))[2:].zfill(160)
        return x.startswith("0"*int(self.challenge))
    
    def get_winner(self):
        return self.clientID

    def encode_challenge(self):
        return str(self.transactionID)+ "/" + str(self.challenge)
    
    def encode_result(self):
        return str(self.transactionID)+ "/" + str(self.clientID)+ "/" + str(self.seed)
   
    def encode_seed(self):
        return str(self.clientID) + "/" + str(self.transactionID)+ "/" + str(self.seed)
