import requests

class TelegramKey():
    baseUri = None
    telegramChatId = None
    isInit = False

class TelegramApi(TelegramKey):
    @staticmethod
    def instance(telegramToken , telegramChatId):
        TelegramKey.baseUri = 'https://api.telegram.org/bot' + telegramToken + '/'
        TelegramKey.telegramChatId = telegramChatId
    @staticmethod
    def SendMessage(message):
        if TelegramKey.isInit == True:
            try:
                uri = TelegramKey.baseUri + "sendMessage"
                params = { 'chat_id' : TelegramKey.telegramChatId , 'text' : message }
                requests.get(uri,params)
            except requests.exceptions.RequestException as e:
                print(e)
                pass
        else:
            raise Exception('텔레그램 Init 이 되지 않았습니다')

