import json
import pyqtgraph as pg

from pyqtgraph.dockarea import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import fav_stocks_config_path, apply_strategies_config_path, \
    DEFAULT_K_LIMIT
from db.models import AStockInfo
from strategies.base import get_latest_n_desc_data
from strategies.boll import BOLL, BOLLChoose, BOLLInfo
from strategies.dual_ma import DualMA, DualMAChoose, DualMAInfo
from strategies.kdj import KDJ, KDJChoose, KDJInfo
from strategies.macd import MACD, MACDChoose, MACDInfo
from strategies.rsi import RSI, RSIChoose, RSIInfo
from strategies.turtle import Turtle, TurtleChoose, TurtleInfo
from strategies.volume_increase import VolumeIncreaseChoose, VolumeIncreaseInfo
from strategies.wr import WR, WRChoose, WRInfo
from utils.candlestick import CandlestickItem
from utils.custom_add_dialog import CustomAddDialog


# TODO: separate common plot widget from this page and watch page
class Choose(QWidget):
    fav_stock_changed_signal = Signal()
    kline_info_signal = Signal(str, float, float, float, float, int)

    def __init__(self, parent=None):
        super(Choose, self).__init__(parent)
        self.setWindowTitle('选股')

        self.fav_stocks = []

        self.stocks_to_be_chosen = []
        self.stocks_pre_chose = []
        self.apply_strategies = []

        self.kline_data = []
        self.k_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.k_h_line = pg.InfiniteLine(angle=0, movable=False)
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
        self.current_kline_period = 'd'

        self.choose_thread = None
        # TODO: make strategies plugin
        # NEW STRATEGIES #
        self.dual_ma_info = DualMAInfo()
        self.volume_increase_info = VolumeIncreaseInfo()
        self.wr_info = WRInfo()
        self.turtle_info = TurtleInfo()
        self.boll_info = BOLLInfo()
        self.macd_info = MACDInfo()
        self.kdj_info = KDJInfo()
        self.rsi_info = RSIInfo()

        op_v_box = QVBoxLayout()
        self.re_search_check = QCheckBox('从结果中再选')
        self.btn_choose = QPushButton('策略选股')
        self.btn_stop_choose = QPushButton('停止')
        self.btn_stop_choose.setDisabled(True)
        op_v_box.addWidget(self.re_search_check)
        op_v_box.addWidget(self.btn_choose)
        op_v_box.addWidget(self.btn_stop_choose)

        self.filter_group_box = QGroupBox()
        choose_v_box = QVBoxLayout()
        choose_v_box.addLayout(op_v_box)
        self.filter_group_box.setLayout(choose_v_box)

        self.progress_bar = QProgressBar()

        self.table = QTableWidget()
        headers = ['代码', '名称']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        left_v_box = QVBoxLayout()
        left_v_box.setContentsMargins(0, 0, 0, 0)
        left_v_box.addWidget(self.filter_group_box)
        left_v_box.addWidget(self.table)

        self.left_widget = QWidget()
        self.left_widget.setLayout(left_v_box)
        self.left_widget.setMinimumWidth(220)
        self.left_widget.setMaximumWidth(250)

        info_g_box = QGridLayout()
        self.date_label = QLabel('日期')
        self.date_input = QLineEdit()
        self.date_input.setDisabled(True)
        self.open_label = QLabel('开')
        self.open_input = QLineEdit()
        self.open_input.setDisabled(True)
        self.close_label = QLabel('收')
        self.close_input = QLineEdit()
        self.close_input.setDisabled(True)
        self.high_label = QLabel('高')
        self.high_input = QLineEdit()
        self.high_input.setDisabled(True)
        self.low_label = QLabel('低')
        self.low_input = QLineEdit()
        self.low_input.setDisabled(True)
        self.volume_label = QLabel('成交量')
        self.volume_input = QLineEdit()
        self.volume_input.setDisabled(True)
        info_g_box.addWidget(self.date_label, 0, 0)
        info_g_box.addWidget(self.date_input, 0, 1)
        info_g_box.addWidget(self.volume_label, 1, 0)
        info_g_box.addWidget(self.volume_input, 1, 1)
        info_g_box.addWidget(self.open_label, 0, 2)
        info_g_box.addWidget(self.open_input, 0, 3)
        info_g_box.addWidget(self.close_label, 1, 2)
        info_g_box.addWidget(self.close_input, 1, 3)
        info_g_box.addWidget(self.high_label, 0, 4)
        info_g_box.addWidget(self.high_input, 0, 5)
        info_g_box.addWidget(self.low_label, 1, 4)
        info_g_box.addWidget(self.low_input, 1, 5)

        self.info_widget = QGroupBox()
        self.info_widget.setLayout(info_g_box)

        self.day_check = QRadioButton('日')
        self.day_check.setChecked(True)
        self.week_check = QRadioButton('周')
        self.month_check = QRadioButton('月')
        self.day_check.toggled.connect(self.on_period_change)
        self.week_check.toggled.connect(self.on_period_change)
        self.month_check.toggled.connect(self.on_period_change)

        self.period_widget = QGroupBox()
        period_g_box = QGridLayout()
        period_g_box.addWidget(self.day_check, 0, 0)
        period_g_box.addWidget(self.week_check, 0, 1)
        period_g_box.addWidget(self.month_check, 0, 2)
        period_g_box.setContentsMargins(0, 0, 0, 0)
        self.period_widget.setLayout(period_g_box)

        self.period_group = QButtonGroup()
        self.period_group.addButton(self.day_check)
        self.period_group.addButton(self.week_check)
        self.period_group.addButton(self.month_check)

        info_h_box = QHBoxLayout()
        info_h_box.addWidget(self.period_widget)
        info_h_box.addWidget(self.info_widget)

        right_v_box = QVBoxLayout()
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

        right_v_box.addLayout(info_h_box)
        right_v_box.addWidget(self.plt_area)

        bottom_h_box = QHBoxLayout()
        bottom_h_box.addWidget(self.left_widget)
        bottom_h_box.addLayout(right_v_box)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addLayout(bottom_h_box)
        self.setLayout(main_v_box)

        self.btn_choose.clicked.connect(self.on_choose)
        self.btn_stop_choose.clicked.connect(self.on_stop_choose)
        self.table.customContextMenuRequested.connect(self.open_pool_ops_menu)
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
        self.table.itemSelectionChanged.connect(self.on_row_changed)
        self.kline_info_signal.connect(self.on_kline_info_changed)

    def on_period_change(self):
        check = self.sender()
        if check.isChecked():
            if check.text() == '日':
                self.current_kline_period = 'd'
            elif check.text() == '周':
                self.current_kline_period = 'w'
            elif check.text() == '月':
                self.current_kline_period = 'm'
        self.re_render_all_plots(self.current_kline_code)

    def on_row_changed(self):
        row = self.table.currentRow()
        code = self.table.item(row, 0).text()
        self.render_all_plots(code)
        self.re_draw_indicatrix(self.current_indicatrix_name)

    def re_render_all_plots(self, code):
        if code is None:
            return
        else:
            self.current_kline_code = code
            self.render_all_plots(code)

    def render_all_plots(self, code):
        self.current_kline_code = code
        if self.current_kline_code is None:
            return

        self.kline_data = []
        data = get_latest_n_desc_data(code, DEFAULT_K_LIMIT,
                                      period=self.current_kline_period)
        _open = []
        _close = []
        _high = []
        _low = []
        for item in data[::-1]:
            _open.append(item.open)
            _close.append(item.close)
            _high.append(item.high)
            _low.append(item.low)

        _macd = MACD()
        macd, dif, dea = _macd.calc_macd(_close)

        _kdj = KDJ()
        k, d, j = _kdj.calc_kdj(_close, _high, _low)

        _rsi = RSI()
        fast_rsi, slow_rsi = _rsi.calc_rsi(_close)

        _wr = WR()
        wr = _wr.calc_williams(_close, _high, _low)

        for i, item in enumerate(data[::-1]):
            obj = {
                'id': i,
                'date': item.date.strftime('%Y-%m-%d'),
                'code': item.code,
                'open': item.open,
                'close': item.close,
                'high': item.high,
                'low': item.low,
                'volume': item.volume,
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
            self.kline_data.append(obj)
        self._render_all_plots()

    def _render_all_plots(self):
        self.k_plt.plotItem.clear()
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

        axis = zip(range(len(k_axis)), k_axis)
        item = CandlestickItem(k_data)
        y_min = min(lows)
        y_max = max(highs)
        self.k_plt.getAxis('bottom').setTicks([axis])
        self.k_plt.addItem(item)
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

    def _emit_info(self, mouse_point):
        index = int(mouse_point.x())
        if -1 < index < len(self.kline_data):
            volume = int(self.kline_data[index]['volume'] / 100)
            self.info_label.setHtml(
                "<p style='color:white'><strong>日期：{0}</strong></p>"
                "<p style='color:white'>开盘：{1}</p>"
                "<p style='color:white'>最高：{2}</p>"
                "<p style='color:white'>最低：{3}</p>"
                "<p style='color:white'>收盘：{4}</p>"
                "<p style='color:white'>成交量：{5}</p>".format(
                    self.kline_data[index]['date'],
                    self.kline_data[index]['open'],
                    self.kline_data[index]['high'],
                    self.kline_data[index]['low'],
                    self.kline_data[index]['close'],
                    volume))
            self.info_label.setPos(mouse_point.x(), mouse_point.y())
            self.kline_info_signal.emit(self.kline_data[index]['date'],
                                        self.kline_data[index]['open'],
                                        self.kline_data[index]['close'],
                                        self.kline_data[index]['high'],
                                        self.kline_data[index]['low'],
                                        volume)

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

    def on_kline_info_changed(self, date, _open, close, high, low, volume):
        self.date_input.setText(date)
        self.open_input.setText(str(_open))
        self.close_input.setText(str(close))
        self.high_input.setText(str(high))
        self.low_input.setText(str(low))
        self.volume_input.setText(str(volume))

    def re_draw_indicatrix(self, name):
        self.current_indicatrix_name = name
        if self.current_kline_code is None:
            return
        self.draw_indicatrix(name)

    def draw_indicatrix(self, strategy_name):
        self.current_indicatrix_name = strategy_name
        if self.current_kline_code is None or \
                self.current_indicatrix_name is None:
            return

        # NEW STRATEGIES #
        if self.current_indicatrix_name == self.dual_ma_info.name:
            dual_ma = DualMA()
            short_period_mas = dual_ma.calc_short_period_ma(
                self.current_kline_code)
            long_period_mas = dual_ma.calc_long_period_ma(
                self.current_kline_code)
            data = [short_period_mas, long_period_mas]
            pen_colors = ['r', 'b']
        elif self.current_indicatrix_name == self.turtle_info.name:
            turtle = Turtle()
            ups = turtle.calc_batch_up(self.current_kline_code)
            downs = turtle.calc_batch_down(self.current_kline_code)
            data = [ups, downs]
            pen_colors = ['r', 'b']
        elif self.current_indicatrix_name == self.boll_info.name:
            boll = BOLL()
            ups = boll.calc_batch_up(self.current_kline_code)
            middles = boll.calc_batch_middle(self.current_kline_code)
            downs = boll.calc_batch_down(self.current_kline_code)
            data = [ups, middles, downs]
            pen_colors = ['r', 'w', 'b']
        else:
            data = []
            pen_colors = []
        self.draw_lines(data, pen_colors)

    def draw_lines(self, data, pen_colors):
        for i, _data in enumerate(data):
            self._draw_line(_data, pen_colors[i])

    def _draw_line(self, data, pen_color):
        self.k_plt.plot(data, pen=pen_color)

    def disable_all(self):
        self.re_search_check.setDisabled(True)
        self.btn_choose.setDisabled(True)
        self.btn_stop_choose.setEnabled(True)

    def enable_all(self):
        self.re_search_check.setEnabled(True)
        self.btn_choose.setEnabled(True)
        self.btn_stop_choose.setDisabled(True)

    def set_progress_bar(self, value, code, name):
        self.progress_bar.setValue(value)
        if value == 100:
            self.enable_all()
        else:
            stock = {
                'code': code,
                'name': name
            }
            self.stocks_pre_chose.append(stock)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))

    def on_choose(self):
        self.disable_all()

        rows = self.table.rowCount()
        for i in reversed(range(rows)):
            self.table.removeRow(i)

        if self.re_search_check.isChecked():
            self.stocks_to_be_chosen = self.stocks_pre_chose.copy()
            self.stocks_pre_chose.clear()
        else:
            self.stocks_to_be_chosen.clear()
            stocks = AStockInfo.select()
            for stock in stocks:
                if stock.status != 0 and stock.type == 1:
                    _stock = {
                        'code': stock.code,
                        'name': stock.name
                    }
                    self.stocks_to_be_chosen.append(_stock)

        if not apply_strategies_config_path.exists():
            QMessageBox.warning(self, '警告', '请先选择一个策略',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.enable_all()
        else:
            with open(apply_strategies_config_path, 'r', encoding='utf-8') as f:
                self.apply_strategies = json.load(f)
            if len(self.apply_strategies) == 0:
                QMessageBox.warning(self, '警告', '请先选择一个策略',
                                    QMessageBox.Ok, QMessageBox.Ok)
                self.enable_all()
            elif len(self.apply_strategies) == 1:
                # NEW STRATEGIES #
                if self.apply_strategies[0] == self.dual_ma_info.name:
                    self.choose_thread = DualMAChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.volume_increase_info.name:
                    self.choose_thread = VolumeIncreaseChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.wr_info.name:
                    self.choose_thread = WRChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.turtle_info.name:
                    self.choose_thread = TurtleChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.boll_info.name:
                    self.choose_thread = BOLLChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.macd_info.name:
                    self.choose_thread = MACDChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.kdj_info.name:
                    self.choose_thread = KDJChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.rsi_info.name:
                    self.choose_thread = RSIChoose(self.stocks_to_be_chosen)
                self.choose_thread.progress_signal.connect(
                    self.set_progress_bar)
                self.choose_thread.start()
            else:
                QMessageBox.warning(self, '警告', '一次只能使用一个策略选股',
                                    QMessageBox.Ok, QMessageBox.Ok)
                self.enable_all()

    def on_stop_choose(self):
        self.choose_thread.terminate()
        self.enable_all()

    def open_pool_ops_menu(self, position):
        pop_menu = QMenu()
        fav_action = QAction('加入自选', self)
        un_fav_action = QAction('删除自选', self)
        remove_action = QAction('删除', self)
        custom_add_action = QAction('手动加入预选池', self)
        pop_menu.addAction(fav_action)
        pop_menu.addAction(un_fav_action)
        pop_menu.addSeparator()
        pop_menu.addAction(remove_action)
        pop_menu.addSeparator()
        pop_menu.addAction(custom_add_action)

        custom_add_action.triggered.connect(self.on_custom_add)
        fav_action.triggered.connect(self.on_fav)
        un_fav_action.triggered.connect(self.on_un_fav)
        remove_action.triggered.connect(self.on_remove)
        pop_menu.exec_(self.table.mapToGlobal(position))

    def on_fav(self):
        if not fav_stocks_config_path.exists():
            self.fav_stocks = []
        else:
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                self.fav_stocks = json.load(f)

        rows = self.table.selectedIndexes()
        for row in rows:
            fav = {
                'code': self.table.item(row.row(), 0).text(),
                'name': self.table.item(row.row(), 1).text()
            }
            if fav not in self.fav_stocks:
                self.fav_stocks.append(fav)

        with open(fav_stocks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.fav_stocks, f, indent=4, ensure_ascii=False)
        self.fav_stock_changed_signal.emit()

    def on_un_fav(self):
        if not fav_stocks_config_path.exists():
            self.fav_stocks = []
        else:
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                self.fav_stocks = json.load(f)

        rows = self.table.selectedIndexes()
        rows_to_un_fav = []
        for row in rows:
            if row.row() not in rows_to_un_fav:
                rows_to_un_fav.append(row.row())
                stock = {
                    'code': self.table.item(row.row(), 0).text(),
                    'name': self.table.item(row.row(), 1).text()
                }
                if stock in self.fav_stocks:
                    self.fav_stocks.remove(stock)

        with open(fav_stocks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.fav_stocks, f, indent=4, ensure_ascii=False)
        self.fav_stock_changed_signal.emit()

    def on_remove(self):
        if not fav_stocks_config_path.exists():
            self.fav_stocks = []
        else:
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                self.fav_stocks = json.load(f)

        rows = self.table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                stock = {
                    'code': self.table.item(row.row(), 0).text(),
                    'name': self.table.item(row.row(), 1).text()
                }
                if stock in self.fav_stocks:
                    self.fav_stocks.remove(stock)
                if stock in self.stocks_pre_chose:
                    self.stocks_pre_chose.remove(stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.table.removeRow(row_idx)

        with open(fav_stocks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.fav_stocks, f, indent=4, ensure_ascii=False)
        self.fav_stock_changed_signal.emit()

    def on_custom_add(self):
        custom_add_dlg = CustomAddDialog(self)
        custom_add_dlg.show()
        custom_add_dlg.add_custom_stock_signal.connect(self.add_custom_item)
        custom_add_dlg.exec_()

    def add_custom_item(self, code, name):
        stock = {
            'code': code,
            'name': name
        }
        self.stocks_pre_chose.append(stock)
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setItem(row_idx, 0, QTableWidgetItem(code))
        self.table.setItem(row_idx, 1, QTableWidgetItem(name))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Choose()
    main.show()
    sys.exit(app.exec_())
