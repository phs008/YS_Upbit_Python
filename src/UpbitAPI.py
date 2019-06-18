import jwt
import uuid
import hashlib
import requests
import queue
from urllib.parse import urlencode


class UpBitKey():
    accessKey = None
    secretKey = None
    marketDic = dict()
    nonSignedOrderbooks = queue.Queue()


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
        response = UpBit.GetMarketCode()
        for marketData in response:
            marketname = marketData["market"]
            marketname = marketname.split('-')
            koreaname = marketData["korean_name"]
            UpBitKey.marketDic[f'{koreaname}/{marketname[0]}'] = marketData["market"]

    @staticmethod
    def GetMarketCode():
        url = "https://api.upbit.com/v1/market/all"
        res = requests.request('GET', url)
        return res.json()

    @staticmethod
    def GetOrderBook(markets):
        url = "https://api.upbit.com/v1/orderbook"
        if isinstance(markets, list):
            param = ','.join(markets)
        else:
            param = markets
        return UpBit.CallApiArrayParam(url, param)

    @staticmethod
    def GetAccount():
        url = "https://api.upbit.com/v1/accounts"
        return UpBit.CallApiNoParam(url)

    @staticmethod
    def GetChance():
        url = "https://api.upbit.com/v1/orders/chance"

    @staticmethod
    def GetTicker(markets):
        url = "https://api.upbit.com/v1/ticker"
        param = ','.join(markets)
        return UpBit.CallApiArrayParam(url, param)

    @staticmethod
    def Order(orders):
        """
        Upbit 주문 API
        :param market: 마켓 코드
        :param side: 주문종류 ( 매수 : bid , 매도 : ask )
        :param volume: 주문량
        :param price: 주문가격
        :param ord_type: 주문타입 ( 지정가 주문 : limit , 시장가 매수 주문 : price , 시장가 매도 주문 : market )
        :return: 주문 UUID
        """
        url = "https://api.upbit.com/v1/orders"

        result = UpBit.CallApiWithParam(url, orders, 'POST')
        return {'uuid': result['uuid'], 'status': result['state'], 'created_at': result['created_at']}

    @staticmethod
    def CallApiNoParam(url, method='GET'):
        try:
            token = UpBit.NoParameterRequest();
            headers = {'Authorization': token}
            res = requests.request(method, url, headers=headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(e)
            pass
        except requests.exceptions.HTTPError as e:
            print(e)
            pass

    @staticmethod
    def CallApiArrayParam(url, markets):
        try:
            queryString = {"markets": markets}
            res = requests.request("GET", url, params=queryString)
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
            headers = {'Authorization': token}
            res = requests.request(method, url, headers=headers, data=body)
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
    def WithParameterRequest(body):
        hash = hashlib.sha512()
        hash.update(urlencode(body).encode())
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


class UpBitUtil(UpBitKey):
    @staticmethod
    def GetPriceUnitInKRWMarket(orderPrice):
        if orderPrice >= 2000000:
            return orderPrice + 1000
        elif orderPrice < 2000000 & orderPrice >= 1000000:
            return orderPrice + 500
        elif orderPrice < 1000000 & orderPrice >= 500000:
            return orderPrice + 500
        elif orderPrice < 500000 & orderPrice >= 100000:
            return orderPrice + 50
        elif orderPrice < 100000 & orderPrice >= 10000:
            return orderPrice + 10
        elif orderPrice < 10000 & orderPrice >= 1000:
            return orderPrice + 5
        elif orderPrice < 1000 & orderPrice >= 100:
            return orderPrice + 1
        elif orderPrice < 100 & orderPrice >= 10:
            return orderPrice + 0.1
        elif orderPrice < 10:
            return orderPrice + 0.01

    @staticmethod
    def WaitNonSigned():
        while True:
            if UpBitKey.nonSignedOrderbooks.qsize() > 0:
                nonSignedBook = UpBitKey.nonSignedOrderbooks.put()
