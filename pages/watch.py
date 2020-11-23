import easyquotation
import json
import os
import pyqtgraph as pg
import time

from notifypy import Notify
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from conf.conf import fav_stocks_config_path, apply_rules_config_path, \
    bundle_dir
from rules.boll import BOLL, BOLLInfo
from rules.custom_watch import CustomWatch
from rules.turtle import Turtle, TurtleInfo, TurtleWatch


def gen_time_slices():
    times = []
    m = 9
    for i in range(0, 30):
        x = m * 100 + 30 + i
        x = '0' + str(x)
        times.append(x)

    m = 10
    for i in range(0, 60):
        x = m * 100 + i
        x = str(x)
        times.append(x)

    m = 11
    for i in range(0, 31):
        x = m * 100 + i
        x = str(x)
        times.append(x)

    m = 13
    for i in range(0, 60):
        x = m * 100 + i
        x = str(x)
        times.append(x)

    m = 14
    for i in range(0, 60):
        x = m * 100 + i
        times.append(x)

    times.append(1500)
    return times


class Watch(QWidget):
    kline_info_signal = Signal(str, float, int)

    def __init__(self, parent=None):
        super(Watch, self).__init__(parent)
        self.setWindowTitle('自选股')

        if not apply_rules_config_path.exists():
            self.watch_rules = []
        else:
            with open(apply_rules_config_path, 'r', encoding='utf-8') as f:
                self.watch_rules = json.load(f)

        # TODO make rules plugin
        # NEW RULES #
        self.boll_watch_thread = None
        self.turtle_watch_thread = None
        self.custom_watch_thread = None
        self.boll_info = BOLLInfo()
        self.turtle_info = TurtleInfo()

        self.kline_data = []
        self.times = gen_time_slices()
        self.v_line = pg.InfiniteLine(angle=90, movable=False, )
        self.h_line = pg.InfiniteLine(angle=0, movable=False, )

        self.current_kline_code = None
        self.current_indicatrix_name = None

        self.top_widget = QWidget()
        top_h_box = QHBoxLayout()

        op_v_box = QVBoxLayout()
        self.btn_watch = QPushButton('开始盯盘')
        self.btn_stop_watch = QPushButton('停止')
        self.btn_stop_watch.setDisabled(True)
        op_v_box.addWidget(self.btn_watch)
        op_v_box.addWidget(self.btn_stop_watch)

        self.info_group_box = QGroupBox()
        info_h_box = QHBoxLayout()
        self.time_label = QLabel('时间')
        self.time_input = QLineEdit()
        self.time_input.setDisabled(True)
        self.price_label = QLabel('价格')
        self.price_input = QLineEdit()
        self.price_input.setDisabled(True)
        self.volume_label = QLabel('成交量')
        self.volume_input = QLineEdit()
        self.volume_input.setDisabled(True)
        info_h_box.addWidget(self.time_label)
        info_h_box.addWidget(self.time_input)
        info_h_box.addWidget(self.price_label)
        info_h_box.addWidget(self.price_input)
        info_h_box.addWidget(self.volume_label)
        info_h_box.addWidget(self.volume_input)
        self.info_group_box.setLayout(info_h_box)
        top_h_box.addLayout(op_v_box)
        top_h_box.addStretch()
        top_h_box.addWidget(self.info_group_box)
        self.top_widget.setLayout(top_h_box)
        self.top_widget.setMaximumHeight(100)

        self.k_plt = pg.PlotWidget(enableMenu=False)
        self.k_plt.plotItem.setMouseEnabled(y=False)
        self.k_plt.hideAxis('bottom')

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.top_widget)
        main_v_box.addWidget(self.k_plt)

        self.setLayout(main_v_box)

        self.btn_watch.clicked.connect(self.on_watch)
        self.btn_stop_watch.clicked.connect(self.on_stop_watch)
        self.move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved,
                                        rateLimit=60, slot=self.emit_kline_info)
        self.kline_info_signal.connect(self.on_kline_info_changed)

    def notify_up(self, rule_name, code, name, up, price):
        self._notify(rule_name, code, name, 'up', up, price)

    def notify_down(self, rule_name, code, name, down, price):
        self._notify(rule_name, code, name, 'down', down, price)

    def _notify(self, rule_name, code, name, flag, base, price):
        title = rule_name + ' ' + code + ' ' + name
        if flag == 'up':
            msg_op = '发出做多信号'
            base_line = '上轨'
            audio = (bundle_dir / 'media/up.wav').as_posix()
            icon = (bundle_dir / 'media/long.png').as_posix()
        else:
            msg_op = '发出做空信号'
            base_line = '下轨'
            audio = (bundle_dir / 'media/down.wav').as_posix()
            icon = (bundle_dir / 'media/short.png').as_posix()
        now = time.strftime('%H:%M:%S', time.localtime())
        msg = now + '价格:' + str(price) + '   ' \
              + msg_op + '   ' \
              + '突破' + base_line + ':' + str(base)

        notification = Notify()
        notification.title = title
        notification.message = msg
        notification.audio = audio
        notification.icon = icon
        notification.send()

    def on_watch(self):
        self.btn_watch.setDisabled(True)
        self.btn_stop_watch.setEnabled(True)

        with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
            fav_stocks = json.load(f)

        self.custom_watch_thread = CustomWatch()
        self.custom_watch_thread.up_signal.connect(self.notify_up)
        self.custom_watch_thread.down_signal.connect(self.notify_down)
        self.custom_watch_thread.start()

        for rule_name in self.watch_rules:
            # NEW RULES #
            if rule_name == self.turtle_info.name:
                self.turtle_watch_thread = TurtleWatch(fav_stocks)
                self.turtle_watch_thread.up_signal.connect(self.notify_up)
                self.turtle_watch_thread.down_signal.connect(self.notify_down)
                self.turtle_watch_thread.start()
            if rule_name == self.boll_info.name:
                self.boll_watch_thread = TurtleWatch(fav_stocks)
                self.boll_watch_thread.up_signal.connect(self.notify_up)
                self.boll_watch_thread.down_signal.connect(self.notify_down)
                self.boll_watch_thread.start()

    def on_stop_watch(self):
        with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
            fav_stocks = json.load(f)
        if fav_stocks:
            self.custom_watch_thread.terminate()

        for rule_name in self.watch_rules:
            # NEW RULES #
            if rule_name == self.turtle_info.name and \
                    self.turtle_watch_thread is not None:
                self.turtle_watch_thread.terminate()
            if rule_name == self.boll_info.name and \
                    self.boll_watch_thread is not None:
                self.boll_watch_thread.terminate()

        self.btn_watch.setEnabled(True)
        self.btn_stop_watch.setDisabled(True)

    def draw_kline(self, code):
        self.current_kline_code = code
        if self.current_kline_code is None:
            return

        self.kline_data = []
        quotation = easyquotation.use('timekline')
        code = code[3:]
        # TODO: a new thread, fetch new data every minute.
        data = quotation.real([code], prefix=True)
        if code[0] == '6':
            prefix = 'sh'
        else:
            prefix = 'sz'
        top_key = prefix + code + '.js'
        for obj in data[top_key]['time_data']:
            item = {
                'time': obj[0],
                'price': float(obj[1]),
                'volume': int(obj[2])
            }
            self.kline_data.append(item)
        self._draw_kline()

    def _draw_kline(self):
        self.k_plt.plotItem.clear()
        prices = []
        volumes = []
        for item in self.kline_data:
            prices.append(item['price'])
            volumes.append(item['volume'])
        y_min = min(prices)
        y_max = max(prices)
        axis = zip(range(len(self.times)), self.times)
        self.k_plt.getAxis('bottom').setTicks([axis])
        self.k_plt.plot(prices, pen='y')
        self.k_plt.showGrid(True, True)
        self.k_plt.setYRange(y_min, y_max)
        self.k_plt.addItem(self.v_line, ignoreBounds=True)
        self.k_plt.addItem(self.h_line, ignoreBounds=True)

    def emit_kline_info(self, event):
        pos = event[0]
        if self.k_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.k_plt.plotItem.vb.mapSceneToView(pos)
            index = int(mouse_point.x())
            if -1 < index < len(self.kline_data):
                self.kline_info_signal.emit(self.kline_data[index]['time'],
                                            self.kline_data[index]['price'],
                                            self.kline_data[index]['volume'])

    def on_kline_info_changed(self, _time, price, volume):
        self.time_input.setText(_time)
        self.price_input.setText(str(price))
        self.volume_input.setText(str(volume))

    def draw_indicatrix(self, rule_name):
        self.current_indicatrix_name = rule_name
        if self.current_kline_code is None or \
                self.current_indicatrix_name is None:
            return

        # NEW RULES #
        if self.current_indicatrix_name == self.turtle_info.name:
            turtle = Turtle()
            up = turtle.calc_up(self.current_kline_code)
            down = turtle.calc_down(self.current_kline_code)

            ups = [up] * 240
            downs = [down] * 240
            data = [ups, downs]
            pen_colors = ['r', 'b']
        elif self.current_indicatrix_name == self.boll_info.name:
            boll = BOLL()
            up = boll.calc_up(self.current_kline_code)
            down = boll.calc_down(self.current_kline_code)
            middle = boll.calc_middle(self.current_kline_code)

            ups = [up] * 240
            downs = [down] * 240
            middles = [middle] * 240
            data = [ups, downs, middles]
            pen_colors = ['r', 'b', 'w']
        else:
            data = []
            pen_colors = []
        self.draw_lines(data, pen_colors)

    def draw_lines(self, data, pen_colors):
        for i, _data in enumerate(data):
            self._draw_line(_data, pen_colors[i])

    def _draw_line(self, data, pen_color):
        self.k_plt.plot(data, pen=pen_color)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Watch()
    main.show()
    sys.exit(app.exec_())
