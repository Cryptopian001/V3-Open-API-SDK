import logging
from time import sleep

from okex.okexwebsocket import OkexWebsocket

logging.basicConfig(
    format='%(asctime)s - %(name)s %(levelname)s: %(message)s',
    level=logging.INFO)


def test_public():
    ws = OkexWebsocket(OkexWebsocket.URL)
    ws.subscribe_public('spot/depth5:CVT-USDT', lambda msg: print(msg))
    ws.connect()
    sleep(10)
