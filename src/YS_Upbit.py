import json
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from src.TelegramBotApi import TelegramApi
from src.UpbitAPI import UpBit, UpBitUtil, UpBitKey


class FileHandler(PatternMatchingEventHandler):
    isFirstevent = 1

    def FileParsing(self, event):
        if event.event_type == "modified" and (self.isFirstevent % 2 == 1):
            # 이벤트 중복 발생 필터링을 위한 조건절
            # 첫번째 이벤트는 처리하고 그 다음 이벤트는 무시한다.
            self.isFirstevent += 1

            fileName = event.src_path
            try:
                f = open(fileName, 'r', encoding='cp949')
                beforeLine = ""
                lastLine = ""
                while True:
                    line = f.readline()
                    if len(line) == 0:
                        print('beforeLine : [', beforeLine, '] lastLien : [', lastLine, ']')
                        # 시그널 신호 example
                        # 2019 - 06 - 04 22: 15:00 Buy SymbolName: 비트코인/KRW_업비트 MarketPosition: 1 Price: 9827000.00
                        # lastLine = '2019-06-04 22:15:00 Buy SymbolName: 비트코인/KRW_업비트 MarketPosition: 1 Price: 9827000.00'
                        lastLine = " ".join(lastLine.split())
                        signal = lastLine.split(' ')

                        # lastLine 기준으로 매매 신호를 파싱하여

                        # 심볼 이름 에 따른 마켓코드 획득
                        symbolName = signal[4]  # '비트코인/KRW_업비트'
                        symbolName = symbolName.rstrip('_업비트')
                        marketCode = UpBitKey.marketDic[symbolName]

                        # 매수 인지 매도인지 파악하고
                        side = 'bid' if signal[2] == 'Buy' else 'ask'

                        # 주문 수량
                        volume = signal[6]

                        # 주문 가격
                        # 추후 주문 수량에 맞춰 주문가격에 대한 호가 변경 로직이 필요함
                        # 현재는 시장가 주문으로서 price 데이터는 null 이여야함
                        price = signal[-1]  # signal[8] 째 데이터가 주문가격임.

                        # 주문타입
                        # 일단 시장가로 측정
                        ord_type = 'price' if side == 'bid' else 'market'

                        orders = dict()
                        orders['market'] = marketCode
                        orders['side'] = side
                        orders['volume'] = volume
                        if ord_type == 'limit' or ord_type == 'price':
                            orders['price'] = price
                        orders['ord_type'] = ord_type

                        UpBit.Order(orders)

                        # if response['state'] == 'wait':
                        #     # 업비트 매매 주문 처리
                        #     UpBitUtil.nonSignedOrderbooks.put(response)
                        #     # 텔레그램 봇으로 매매 상태 날리기
                        #     TelegramApi.SendMessage(f"[ 주문대기 상태 ] 종목 : {marketCode} , 매수/매도 : {side} , "
                        #                             f"주문수량 : {volume}")
                        # else:
                        #     {}
                        TelegramApi.SendMessage(f"[ 주문메시지 발생 ] 종목 : {marketCode} , 매수/매도 : {side} , "
                                                f"주문수량 : {volume}")

                        break
                    beforeLine = lastLine
                    lastLine = line
            except Exception as e:
                print(e)
                pass
            finally:
                f.close()

    def on_modified(self, event):
        self.FileParsing(event)


if __name__ == "__main__":
    pattenrs = ["*.txt", "*.text"]
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    dirPath = os.getcwd()
    with open(dirPath + '\src\config.cf') as json_file:
        json_config_data = json.load(json_file)

    UpBit.instance(json_config_data['UpBitAccessKey'], json_config_data['UpBitSecretKey'])
    TelegramApi.instance(json_config_data['TelegramApiToken'], json_config_data['TelegramChatId'])

    a = UpBit.GetAccount()

    event_handler = FileHandler(pattenrs)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
