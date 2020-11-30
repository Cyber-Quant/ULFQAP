import json
import pyqtgraph as pg
import time

from notifypy import Notify
from pyqtgraph.dockarea import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from apis.k_charts import fetch_tencent_minute_k, fetch_sina_minute_k
from conf.conf import fav_stocks_config_path, apply_strategies_config_path, \
    bundle_dir
from strategies.boll import BOLL, BOLLInfo, BOLLWatch
from strategies.custom_watch import CustomWatch
from strategies.kdj import KDJ
from strategies.macd import MACD
from strategies.rsi import RSI
from strategies.wr import WR
from utils.candlestick import CandlestickItem


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


# TODO: separate common plot widget from this page and choose page
class Watch(QWidget):
    kline_info_signal = Signal(str, float, int)

    def __init__(self, parent=None):
        super(Watch, self).__init__(parent)
        self.setWindowTitle('自选股')

        if not apply_strategies_config_path.exists():
            self.watch_strategies = []
        else:
            with open(apply_strategies_config_path, 'r', encoding='utf-8') as f:
                self.watch_strategies = json.load(f)

        self.current_kline_period = '1'

        # TODO: make strategies plugin
        # NEW STRATEGIES #
        self.boll_watch_thread = None
        self.custom_watch_thread = None
        self.boll_info = BOLLInfo()

        self.kline_data = []
        self.times = gen_time_slices()
        self.k_v_line = pg.InfiniteLine(angle=90, movable=False, )
        self.k_h_line = pg.InfiniteLine(angle=0, movable=False, )
        self.vol_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.vol_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.macd_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.macd_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.kdj_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.kdj_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.rsi_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.rsi_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.wr_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.wr_h_line = pg.InfiniteLine(angle=0, movable=False)

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

        self.plt_area = DockArea()

        self.dock_k = Dock('K')
        self.k_plt = pg.PlotWidget(enableMenu=False)
        self.k_plt.plotItem.setMouseEnabled(y=False)
        self.k_plt.hideAxis('bottom')
        self.info_label = pg.TextItem()
        self.plt_area.addDock(self.dock_k, 'bottom')
        self.dock_k.addWidget(self.k_plt)

        index_height = 70

        self.dock_vol = Dock('Volume')
        self.vol_plt = pg.PlotWidget(enableMenu=False)
        self.vol_plt.plotItem.setMouseEnabled(y=False)
        self.vol_plt.hideAxis('bottom')
        self.vol_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_vol, 'bottom', self.dock_k)
        self.dock_vol.addWidget(self.vol_plt)
        self.dock_vol.setFixedHeight(index_height)

        self.dock_macd = Dock('MACD')
        self.macd_plt = pg.PlotWidget(enableMenu=False)
        self.macd_plt.plotItem.setMouseEnabled(y=False)
        self.macd_plt.hideAxis('bottom')
        self.macd_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_macd, 'bottom', self.dock_vol)
        self.dock_macd.addWidget(self.macd_plt)
        self.dock_macd.setFixedHeight(index_height)

        self.dock_kdj = Dock('KDJ')
        self.kdj_plt = pg.PlotWidget(enableMenu=False)
        self.kdj_plt.plotItem.setMouseEnabled(y=False)
        self.kdj_plt.hideAxis('bottom')
        self.kdj_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_kdj, 'bottom', self.dock_macd)
        self.dock_kdj.addWidget(self.kdj_plt)
        self.dock_kdj.setFixedHeight(index_height)

        self.dock_rsi = Dock('RSI')
        self.rsi_plt = pg.PlotWidget(enableMenu=False)
        self.rsi_plt.plotItem.setMouseEnabled(y=False)
        self.rsi_plt.hideAxis('bottom')
        self.rsi_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_rsi, 'bottom', self.dock_kdj)
        self.dock_rsi.addWidget(self.rsi_plt)
        self.dock_rsi.setFixedHeight(index_height)

        self.dock_wr = Dock('WR')
        self.wr_plt = pg.PlotWidget(enableMenu=False)
        self.wr_plt.plotItem.setMouseEnabled(y=False)
        self.wr_plt.hideAxis('bottom')
        self.wr_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_wr, 'bottom', self.dock_rsi)
        self.dock_wr.addWidget(self.wr_plt)
        self.dock_wr.setFixedHeight(index_height)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.top_widget)
        main_v_box.addWidget(self.plt_area)

        self.setLayout(main_v_box)

        self.btn_watch.clicked.connect(self.on_watch)
        self.btn_stop_watch.clicked.connect(self.on_stop_watch)
        self.k_move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved,
                                          rateLimit=60,
                                          slot=self.kline_emit_info)
        self.vol_move_slot = pg.SignalProxy(self.vol_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.vol_emit_info)
        self.macd_move_slot = pg.SignalProxy(
            self.macd_plt.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.macd_emit_info)
        self.kdj_move_slot = pg.SignalProxy(self.kdj_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.kdj_emit_info)
        self.rsi_move_slot = pg.SignalProxy(self.rsi_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.rsi_emit_info)
        self.wr_move_slot = pg.SignalProxy(self.wr_plt.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self.wr_emit_info)
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
        # self.re_render_all_plots(self.current_kline_code)
        self.render_all_plots(self.current_kline_code)

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

        self.btn_watch.setEnabled(True)
        self.btn_stop_watch.setDisabled(True)

    def render_all_plots(self, code):
        self.current_kline_code = code
        if self.current_kline_code is None:
            return

        self.kline_data = []
        if self.current_kline_period == '1':
            self.kline_data = fetch_tencent_minute_k(code)
        else:
            data = fetch_sina_minute_k(self.current_kline_code,
                                       self.current_kline_period)
            _open = []
            _close = []
            _high = []
            _low = []
            for item in data:
                _open.append(item['open'])
                _close.append(item['close'])
                _high.append(item['high'])
                _low.append(item['low'])

            _macd = MACD()
            macd, dif, dea = _macd.calc_macd(_close)

            _kdj = KDJ()
            k, d, j = _kdj.calc_kdj(_close, _high, _low)

            _rsi = RSI()
            fast_rsi, slow_rsi = _rsi.calc_rsi(_close)

            _wr = WR()
            wr = _wr.calc_williams(_close, _high, _low)

            for i, item in enumerate(data):
                obj = {
                    'id': i,
                    'date': item['day'],
                    'open': item['open'],
                    'close': item['close'],
                    'high': item['high'],
                    'low': item['low'],
                    'volume': item['volume'],
                    'dif': dif[i],
                    'dea': dea[i],
                    'macd': macd[i],
                    'k': k[i],
                    'd': d[i],
                    'j': j[i],
                    'slow_rsi': slow_rsi[i],
                    'fast_rsi': fast_rsi[i],
                    'wr': wr[i]
                }
                if self.current_kline_period != '60':
                    obj['ma_price'] = item['ma_price']
                    obj['ma_volume'] = item['ma_volume']
                self.kline_data.append(obj)
        self._render_all_plots()

    def _render_all_plots(self):
        self.k_plt.plotItem.clear()
        if self.current_kline_period == '1':
            self.vol_plt.plotItem.clear()
            self.kdj_plt.plotItem.clear()
            self.macd_plt.plotItem.clear()
            self.rsi_plt.plotItem.clear()
            self.wr_plt.plotItem.clear()

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
            self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
            self.k_plt.addItem(self.k_h_line, ignoreBounds=True)
            self.k_plt.addItem(self.info_label)
        else:
            uni_index = []

            k_data = []
            lows = []
            highs = []
            k_axis = []

            volumes = []

            difs = []
            deas = []
            red_macds = []
            green_macds = []
            red_macds_index = []
            green_macds_index = []

            k = []
            d = []
            j = []

            slow_rsis = []
            fast_rsis = []

            wrs = []

            for item in self.kline_data:
                uni_index.append(item['id'])

                (i, _open, close, high, low) = (
                    item['id'], item['open'], item['close'], item['high'],
                    item['low'])
                k_data.append((i, _open, close, high, low))
                lows.append(item['low'])
                highs.append(item['high'])
                k_axis.append(item['date'])

                volumes.append(item['volume'])

                difs.append(item['dif'])
                deas.append(item['dea'])
                if item['macd'] >= 0:
                    red_macds.append(item['macd'])
                    red_macds_index.append(item['id'])
                else:
                    green_macds.append(item['macd'])
                    green_macds_index.append(item['id'])

                k.append(item['k'])
                d.append(item['d'])
                j.append(item['j'])

                slow_rsis.append(item['slow_rsi'])
                fast_rsis.append(item['fast_rsi'])

                wrs.append(item['wr'])

            if self.current_kline_period != '60':
                ma_prices = []
                ma_volumes = []
                for item in self.kline_data:
                    ma_prices.append(item['ma_price'])
                    ma_volumes.append(item['ma_volume'])
                self.k_plt.plot(ma_prices, pen='y')

            axis = zip(range(len(self.times)), self.times)
            item = CandlestickItem(k_data)
            y_min = min(lows)
            y_max = max(highs)
            self.k_plt.addItem(item)
            self.k_plt.getAxis('bottom').setTicks([axis])
            self.k_plt.showGrid(True, True)
            self.k_plt.setYRange(y_min, y_max)
            self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
            self.k_plt.addItem(self.k_h_line, ignoreBounds=True)
            self.k_plt.addItem(self.info_label)

            uni_width = (k_data[1][0] - k_data[0][0]) / 3.0

            self.vol_plt.plotItem.clear()
            volume_bar = pg.BarGraphItem(x=uni_index, height=volumes,
                                         width=uni_width,
                                         pen='b')
            self.vol_plt.addItem(volume_bar)
            self.vol_plt.addItem(self.vol_v_line, ignoreBounds=True)
            self.vol_plt.addItem(self.vol_h_line, ignoreBounds=True)

            self.macd_plt.plotItem.clear()
            red_macd_bar = pg.BarGraphItem(x=red_macds_index, height=red_macds,
                                           width=uni_width,
                                           pen='r')
            green_macd_bar = pg.BarGraphItem(x=green_macds_index,
                                             height=green_macds,
                                             width=uni_width,
                                             pen='g')
            self.macd_plt.addItem(red_macd_bar)
            self.macd_plt.addItem(green_macd_bar)
            self.macd_plt.plot(difs, pen='w')
            self.macd_plt.plot(deas, pen='y')
            self.macd_plt.addItem(self.macd_v_line, ignoreBounds=True)
            self.macd_plt.addItem(self.macd_h_line, ignoreBounds=True)

            self.kdj_plt.plotItem.clear()
            self.kdj_plt.plot(k, pen='r')
            self.kdj_plt.plot(d, pen='b')
            self.kdj_plt.plot(j, pen='y')
            self.kdj_plt.addItem(self.kdj_v_line, ignoreBounds=True)
            self.kdj_plt.addItem(self.kdj_h_line, ignoreBounds=True)

            self.rsi_plt.plotItem.clear()
            self.rsi_plt.plot(slow_rsis, pen='b')
            self.rsi_plt.plot(fast_rsis, pen='y')
            self.rsi_plt.addItem(self.rsi_v_line, ignoreBounds=True)
            self.rsi_plt.addItem(self.rsi_h_line, ignoreBounds=True)

            self.wr_plt.plotItem.clear()
            self.wr_plt.plot(wrs, pen='w')
            self.wr_plt.addItem(self.wr_v_line, ignoreBounds=True)
            self.wr_plt.addItem(self.wr_h_line, ignoreBounds=True)

        self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
        self.k_plt.addItem(self.k_h_line, ignoreBounds=True)

    def kline_emit_info(self, event):
        pos = event[0]
        if self.k_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.k_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.k_v_line.setPos(mouse_point.x())
            self.k_h_line.setPos(mouse_point.y())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def vol_emit_info(self, event):
        pos = event[0]
        if self.vol_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.vol_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.vol_v_line.setPos(mouse_point.x())
            self.vol_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def macd_emit_info(self, event):
        pos = event[0]
        if self.macd_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.macd_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.macd_v_line.setPos(mouse_point.x())
            self.macd_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def kdj_emit_info(self, event):
        pos = event[0]
        if self.kdj_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.kdj_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.kdj_v_line.setPos(mouse_point.x())
            self.kdj_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def rsi_emit_info(self, event):
        pos = event[0]
        if self.rsi_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.rsi_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.rsi_v_line.setPos(mouse_point.x())
            self.rsi_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def wr_emit_info(self, event):
        pos = event[0]
        if self.wr_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.wr_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.wr_v_line.setPos(mouse_point.x())
            self.wr_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())

    def _emit_info(self, mouse_point):
        index = int(mouse_point.x())
        if -1 < index < len(self.kline_data):
            if self.current_kline_period == '1':
                self.info_label.setHtml(
                    "<p style='color:white'><strong>日期：{0}</strong></p>"
                    "<p style='color:white'>价格：{1}</p>"
                    "<p style='color:white'>量：{2}</p>".format(
                        self.kline_data[index]['time'],
                        self.kline_data[index]['price'],
                        self.kline_data[index]['volume']))
                self.kline_info_signal.emit(self.kline_data[index]['time'],
                                            self.kline_data[index]['price'],
                                            self.kline_data[index]['volume'])
            else:
                self.info_label.setHtml(
                    "<p style='color:white'><strong>日期：{0}</strong></p>"
                    "<p style='color:white'>开：{1}</p>"
                    "<p style='color:white'>收：{2}</p>"
                    "<p style='color:white'>高：{3}</p>"
                    "<p style='color:white'>低：{4}</p>"
                    "<p style='color:white'>量：{5}</p>".format(
                        self.kline_data[index]['date'],
                        self.kline_data[index]['open'],
                        self.kline_data[index]['close'],
                        self.kline_data[index]['high'],
                        self.kline_data[index]['low'],
                        self.kline_data[index]['volume']))
                self.kline_info_signal.emit(self.kline_data[index]['date'],
                                            self.kline_data[index]['close'],
                                            self.kline_data[index]['volume'])
            self.info_label.setPos(mouse_point.x(), mouse_point.y())

    def on_kline_info_changed(self, _time, price, volume):
        self.time_input.setText(_time)
        self.price_input.setText(str(price))
        self.volume_input.setText(str(volume))

    def draw_indicatrix(self, strategy_name):
        self.current_indicatrix_name = strategy_name
        if self.current_kline_code is None or \
                self.current_indicatrix_name is None:
            return

        # NEW STRATEGIES #
        if self.current_indicatrix_name == self.boll_info.name:
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
