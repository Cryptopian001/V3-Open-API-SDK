import json
import logging
import time
import zlib  # 压缩相关的库
from collections import defaultdict
from threading import Thread
from typing import Dict

import websocket

from okex import utils


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


class OkexWebsocket(object):
    URL: str = 'wss://real.OKEx.com:8443/ws/v3'
    ws: websocket.WebSocketApp

    def __init__(self, url, api_key=None, api_secret_key=None, passphrase=None):
        self.url = url
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.passphrase = passphrase
        self.thread = None
        self.public_handlers: Dict[str, list] = defaultdict(lambda: [])
        self.private_handlers: Dict[str, list] = defaultdict(lambda: [])
        self.exiting = False
        self.logger = logging.getLogger(__name__)

    def login(self):
        timestamp = time.time()
        sign = utils.signature(timestamp, 'GET', '/users/self/verify', None, self.api_secret_key)
        self.ws.send(json.dumps({'op': 'login', 'args': [self.api_key, self.passphrase, str(timestamp), sign]}))

    def subscribe_public(self, topic, handler):
        current_handlers = self.public_handlers[topic]
        if handler not in current_handlers:
            self.public_handlers[topic].append(handler)

    def subscribe_private(self, topic, handler):
        current_handlers = self.private_handlers[topic]
        if handler not in current_handlers:
            self.private_handlers[topic].append(handler)

    def on_close(self, handler):
        self.public_handlers['on_close'].append(handler)

    def connect(self):
        self.ws = websocket.WebSocketApp(url=self.url,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error)
        if not self.thread:
            self.thread = Thread(target=self.ws.run_forever)
            self.thread.start()
        else:
            self.ws.run_forever()

    def __on_open(self):
        self.logger.info("OKEx websocket connected...")
        self.ws.send("ping")
        self.__sub_topics(list(self.public_handlers.keys()))
        if self.api_key:
            self.login()

    @staticmethod
    def match_topic(msgs, topic):
        table = msgs['table']
        if topic.startswith(table):
            data = msgs['data'][0]
            if table == 'spot/account':
                return topic == f"{table}:{data['currency']}"
            if table in ['spot/order', 'spot/trade', 'spot/depth5']:
                return topic == f"{table}:{data['instrument_id']}"
            return True
        return False

    def __on_message(self, message):
        inflated = inflate(message).decode('utf-8')  # 将okex发来的数据解压
        if inflated == 'pong':  # 判断推送来的消息类型：如果是服务器的心跳
            self.ws.send("ping")
            return
        msgs = json.loads(inflated)
        if "event" in msgs:
            if msgs['event'] == 'login':
                self.__sub_topics(list(self.private_handlers.keys()))
            elif msgs['event'] == 'subscribe':
                self.logger.info(f"OKEx channel: {msgs['channel']} subscribed.")
        elif "table" in msgs:
            for topic, handlers in self.public_handlers.items():
                if self.match_topic(msgs, topic):
                    for handler in handlers:
                        handler(msgs)
        else:
            self.logger.info(msgs)

    def __sub_topics(self, topics):
        self.ws.send(json.dumps({"op": "subscribe", "args": topics}))

    def __on_close(self):
        if self.exiting:
            return
        self.logger.warning('OKEx websocket closed, reconnecting...')
        on_close_handlers = self.public_handlers['on_close']
        if on_close_handlers:
            for handler in on_close_handlers:
                handler()
        self.connect()

    def __on_error(self, error):
        self.logger.exception('OKEx websocket error, closing...' + str(error))
        if self.ws:
            self.ws.close()

    def exit(self):
        self.exiting = True
        self.ws.close()
