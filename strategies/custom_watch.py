import json
import time

from qtpy.QtCore import *

from apis.realtime_price import fetch_sina_realtime_price
from conf.conf import custom_watch_config_path


class CustomWatch(QThread):
    up_signal = Signal(str, str, float, float)
    down_signal = Signal(str, str, float, float)

    def __init__(self, parent=None):
        super(CustomWatch, self).__init__(parent)

        if not custom_watch_config_path.exists():
            self.custom_watch = []
        else:
            with open(custom_watch_config_path, 'r', encoding='utf-8') as f:
                self.custom_watch = json.load(f)

    def run(self):
        custom_watch_codes = []
        custom_watch_names = []
        custom_watch_ups = []
        custom_watch_downs = []
        for custom_watch in self.custom_watch:
            custom_watch_codes.append(custom_watch['code'])
            custom_watch_names.append(custom_watch['name'])
            custom_watch_ups.append(custom_watch['up'])
            custom_watch_downs.append(custom_watch['down'])

        pre_prices = []
        for i in range(len(self.custom_watch)):
            pre_prices.append(0.0)

        if not custom_watch_codes:
            return False

        while True:
            prices = fetch_sina_realtime_price(custom_watch_codes)
            for i, price in enumerate(prices):
                if pre_prices[i] <= custom_watch_ups[i] < price:
                    self.up_signal.emit(custom_watch_codes[i],
                                        custom_watch_names[i],
                                        custom_watch_ups[i], price)
                if pre_prices[i] >= custom_watch_downs[i] > price:
                    self.down_signal.emit(custom_watch_codes[i],
                                          custom_watch_names[i],
                                          custom_watch_downs[i], price)
                pre_prices[i] = price
            time.sleep(3)
