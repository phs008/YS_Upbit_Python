import jwt
import uuid
import hashlib
from urllib.parse import urlencode

class UpBit:
    accessKey = ""
    secretKey = ""
    def __init__(self,access_key , secret_key):
        accessKey = access_key
        secretKey = secret_key






    def NoParameter(self):
        payload = {
            'access_key' : self.accessKey,
            'nonce' : str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload,self.secretKey).decode('utf8')
        authorization_token = 'Bearer {}'.format(jwt_token)
        return  authorization_token

    def WithParameter(self,queryDic):
        hash = hashlib.sha512()
        hash.update(urlencode(queryDic).encode())
        query_hash = hash.hexdigest()

        payload = {
            'access_key': self.accessKey,
            'nonce': str(uuid.uuid4()),
            'query_hash' : query_hash,
            'query_hash_alg' : 'SHA512',
        }
        jwt_token = jwt.encode(payload, self.secretKey).decode('utf8')
        authorization_token = 'Bearer {}'.format(jwt_token)
        return authorization_token