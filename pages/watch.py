import json
import time

from notifypy import Notify
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from conf.conf import fav_stocks_config_path, apply_strategies_config_path, \
    bundle_dir
from strategies.boll import BOLLInfo, BOLLWatch
from strategies.dual_line import DualLineInfo
from strategies.custom_watch import CustomWatch
from strategies.mcst import MCSTInfo
from strategies.turtle import TurtleInfo, TurtleWatch
from widgets.plots import Plots


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


class Watch(Plots):
    kline_info_signal = Signal(str, float, float, float, float, int)

    def __init__(self, parent=None):
        super(Watch, self).__init__(parent)
        self.setWindowTitle('自选股')

        if not apply_strategies_config_path.exists():
            self.watch_strategies = []
        else:
            with open(apply_strategies_config_path, 'r', encoding='utf-8') as f:
                self.watch_strategies = json.load(f)

        self.current_kline_period = '1'
        self.times = gen_time_slices()

        # TODO: make strategies plugin
        # NEW STRATEGIES #
        self.boll_watch_thread = None
        self.custom_watch_thread = None
        self.turtle_watch_thread = None
        self.boll_info = BOLLInfo()
        self.dual_line_info = DualLineInfo()
        self.turtle_info = TurtleInfo()
        self.mcst_info = MCSTInfo()

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

        self.m1_check = QRadioButton('1分')
        self.m1_check.setChecked(True)
        self.m5_check = QRadioButton('5分')
        self.m15_check = QRadioButton('15分')
        self.m30_check = QRadioButton('30分')
        self.hour_check = QRadioButton('时')
        self.m1_check.toggled.connect(self.on_period_change)
        self.m5_check.toggled.connect(self.on_period_change)
        self.m15_check.toggled.connect(self.on_period_change)
        self.m30_check.toggled.connect(self.on_period_change)
        self.hour_check.toggled.connect(self.on_period_change)

        self.period_widget = QGroupBox()
        period_g_box = QGridLayout()
        period_g_box.addWidget(self.m1_check, 0, 0)
        period_g_box.addWidget(self.m5_check, 0, 1)
        period_g_box.addWidget(self.m15_check, 0, 2)
        period_g_box.addWidget(self.m30_check, 1, 0)
        period_g_box.addWidget(self.hour_check, 1, 1)
        period_g_box.setContentsMargins(0, 0, 0, 0)
        self.period_widget.setLayout(period_g_box)

        self.period_group = QButtonGroup()
        self.period_group.addButton(self.m1_check)
        self.period_group.addButton(self.m5_check)
        self.period_group.addButton(self.m15_check)
        self.period_group.addButton(self.m30_check)
        self.period_group.addButton(self.hour_check)

        top_h_box.addLayout(op_v_box)
        top_h_box.addWidget(self.period_widget)
        top_h_box.addStretch()
        top_h_box.addWidget(self.info_group_box)

        self.top_widget.setLayout(top_h_box)
        self.top_widget.setMaximumHeight(100)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.top_widget)
        main_v_box.addWidget(self.plt_area)

        self.setLayout(main_v_box)

        self.btn_watch.clicked.connect(self.on_watch)
        self.btn_stop_watch.clicked.connect(self.on_stop_watch)
        self.kline_info_signal.connect(self.on_kline_info_changed)

    def on_period_change(self):
        check = self.sender()
        if check.isChecked():
            if check.text() == '1分':
                self.current_kline_period = '1'
            elif check.text() == '5分':
                self.current_kline_period = '5'
            elif check.text() == '15分':
                self.current_kline_period = '15'
            elif check.text() == '30分':
                self.current_kline_period = '30'
            elif check.text() == '时':
                self.current_kline_period = '60'
        self.re_render_all_plots(self.current_kline_code)

    def notify_up(self, strategy_name, code, name, up, price):
        self._notify(strategy_name, code, name, 'up', up, price)

    def notify_down(self, strategy_name, code, name, down, price):
        self._notify(strategy_name, code, name, 'down', down, price)

    def _notify(self, strategy_name, code, name, flag, base, price):
        title = strategy_name + ' ' + code + ' ' + name
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

        for strategy_name in self.watch_strategies:
            # NEW STRATEGIES #
            if strategy_name == self.boll_info.name:
                self.boll_watch_thread = BOLLWatch(fav_stocks)
                self.boll_watch_thread.up_signal.connect(self.notify_up)
                self.boll_watch_thread.down_signal.connect(self.notify_down)
                self.boll_watch_thread.start()
            if strategy_name == self.turtle_info.name:
                self.turtle_watch_thread = TurtleWatch(fav_stocks)
                self.turtle_watch_thread.up_signal.connect(self.notify_up)
                self.turtle_watch_thread.down_signal.connect(self.notify_down)
                self.turtle_watch_thread.start()

    def on_stop_watch(self):
        with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
            fav_stocks = json.load(f)
        if fav_stocks:
            self.custom_watch_thread.terminate()

        for strategy_name in self.watch_strategies:
            # NEW STRATEGIES #
            if strategy_name == self.boll_info.name and \
                    self.boll_watch_thread is not None:
                self.boll_watch_thread.terminate()
            if strategy_name == self.turtle_info.name and \
                    self.turtle_watch_thread is not None:
                self.turtle_watch_thread.terminate()

        self.btn_watch.setEnabled(True)
        self.btn_stop_watch.setDisabled(True)

    def on_kline_info_changed(self, date, _open, close, high, low, volume):
        self.time_input.setText(date)
        self.price_input.setText(str(close))
        self.volume_input.setText(str(volume))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Watch()
    main.show()
    sys.exit(app.exec_())
