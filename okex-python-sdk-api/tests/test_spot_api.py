import json
import os

from okex.spot_api import SpotAPI


def load_json_config(json_config_file_name: str, encoding: str = 'utf-8') -> dict:
    json_config_file_path = os.path.join(os.path.dirname(__file__), json_config_file_name)
    with open(json_config_file_path, encoding=encoding) as f:
        return json.load(f)


class TestSpotApi:
    def setup_class(self):
        secret = load_json_config("secret.json")['okex_volume']
        self.spot_api = SpotAPI(secret['api_key'], secret['api_secret_key'], secret['passphrase'])

    def test_trade_fee(self):
        trade_fee = self.spot_api.get_trade_fee(1)
        print(trade_fee)
        assert 'maker' in trade_fee
        assert 'taker' in trade_fee
        trade_fee = self.spot_api.get_trade_fee(instrument_id='BTC_USDT')
        print(trade_fee)
        assert 'maker' in trade_fee
        assert 'taker' in trade_fee
