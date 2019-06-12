import jwt
import uuid
import hashlib
import requests
from urllib.parse import urlencode


class UpBitKey(object):
    accessKey = None
    secretKey = None


class UpBit(UpBitKey):
    # __instance = None

    # @classmethod
    # def __getInstance(cls):
    #     return  cls.__instance
    #
    # @classmethod
    # def instance(cls):
    #     cls.__instance = cls()
    #     cls.instance = cls.__instance
    #     return  cls.__instance

    @staticmethod
    def instance(access_key, secret_key):
        UpBitKey.accessKey = access_key
        UpBitKey.secretKey = secret_key

    @staticmethod
    def GetMarket():
        url = "https://api.upbit.com/v1/market/all"
        return UpBit.HttpRequest(url);

    @staticmethod
    def GetAccount():
        url = "https://api.upbit.com/v1/accounts"

    @staticmethod
    def GetOrderBook(markets):
        url = "https://api.upbit.com/v1/orderbook"
        param = ','.join(markets)
        UpBit.CallApiWithParam(url,param,)


    @staticmethod
    def OrderBook(order):
        url = "https://api.upbit.com/v1/market/all"


    @staticmethod
    def CallApiNoParam(url, method='GET'):
        try:
            token = UpBit.NoParameterRequest()
            res = requests.request(method, url)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(e)
            pass
        except requests.exceptions.HTTPError as e:
            print(e)
            pass

    @staticmethod
    def CallApiWithParam(url, body, method='GET'):
        try:
            token = UpBit.WithParameterRequest(body)
            res = requests.request(method, url)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(e)
            pass
        except requests.exceptions.HTTPError as e:
            print(e)
            pass

    @classmethod
    def NoParameterRequest(cls):
        payload = {
            'access_key': UpBit.accessKey,
            'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, UpBit.secretKey).decode('utf8')
        authorization_token = 'Bearer {}'.format(jwt_token)

        return authorization_token

    @staticmethod
    def WithParameterRequest(queryDic):
        hash = hashlib.sha512()
        hash.update(urlencode(queryDic).encode())
        query_hash = hash.hexdigest()

        payload = {
            'access_key': UpBit.accessKey,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }
        jwt_token = jwt.encode(payload, UpBit.secretKey).decode('utf8')
        authorization_token = 'Bearer {}'.format(jwt_token)
        return authorization_token
