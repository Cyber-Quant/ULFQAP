import json
import pyqtgraph as pg

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import fav_stocks_config_path, DEFAULT_K_LIMIT
from db.models import AStockInfo
from strategies.base import get_latest_n_desc_data
from strategies.boll import BOLL, BOLLInfo
from strategies.dual_ma import DualMA, DualMAInfo
from strategies.kdj import KDJ, KDJInfo
from strategies.macd import MACD, MACDInfo
from strategies.rsi import RSI, RSIInfo
from strategies.turtle import Turtle, TurtleInfo
from strategies.volume_increase import VolumeIncreaseInfo
from strategies.wr import WR, WRInfo


class Backtest(QWidget):
    def __init__(self, parent=None):
        super(Backtest, self).__init__(parent)
        self.setWindowTitle('回测')

        self.backtest_option = 'fav'
        self.current_strategy_name = None
        self.current_code = None
        self.current_name = None
        self.opens = None
        self.closes = None
        self.highs = None
        self.lows = None
        self.volumes = None
        self.dates = None
        self.k_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.k_h_line = pg.InfiniteLine(angle=0, movable=False)

        self.op_group_box = QGroupBox()
        op_g_box = QGridLayout()
        self.start_date_label = QLabel('起始日期')
        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-1))
        self.start_date.setDate(QDate.currentDate().addDays(-365))

        self.end_date_label = QLabel('结束日期')
        self.end_date = QDateTimeEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.end_date.setMaximumDate(QDate.currentDate().addDays(0))
        self.end_date.setDate(QDate.currentDate())

        double_validator = QDoubleValidator()
        self.init_money_label = QLabel('初始资金(万)')
        self.init_money_input = QLineEdit()
        self.init_money_input.setValidator(double_validator)
        self.init_money_input.setText('10')

        self.fee_label = QLabel('手续费(万分)')
        self.fee_input = QLineEdit()
        self.fee_input.setValidator(double_validator)
        self.fee_input.setText('2.5')

        self.pass_fee_label = QLabel('过户费(万分)')
        self.pass_fee_input = QLineEdit()
        self.pass_fee_input.setValidator(double_validator)
        self.pass_fee_input.setText('0.2')

        self.tax_label = QLabel('印花税(千分)')
        self.tax_input = QLineEdit()
        self.tax_input.setValidator(double_validator)
        self.tax_input.setText('1')

        self.backtest_fav_check = QRadioButton('自选股')
        self.backtest_fav_check.setChecked(True)
        self.backtest_all_check = QRadioButton('全部股票')

        self.option_group = QButtonGroup()
        self.option_group.addButton(self.backtest_fav_check)
        self.option_group.addButton(self.backtest_all_check)
        self.backtest_fav_check.toggled.connect(self.on_option_change)
        self.backtest_all_check.toggled.connect(self.on_option_change)

        self.btn_backtest = QPushButton('开始回测')

        op_g_box.addWidget(self.start_date_label, 0, 0)
        op_g_box.addWidget(self.start_date, 1, 0)
        op_g_box.addWidget(self.end_date_label, 0, 1)
        op_g_box.addWidget(self.end_date, 1, 1)
        op_g_box.addWidget(self.init_money_label, 0, 2)
        op_g_box.addWidget(self.init_money_input, 1, 2)
        op_g_box.addWidget(self.fee_label, 0, 3)
        op_g_box.addWidget(self.fee_input, 1, 3)
        op_g_box.addWidget(self.pass_fee_label, 0, 4)
        op_g_box.addWidget(self.pass_fee_input, 1, 4)
        op_g_box.addWidget(self.tax_label, 0, 5)
        op_g_box.addWidget(self.tax_input, 1, 5)
        op_g_box.addWidget(self.backtest_fav_check, 0, 6)
        op_g_box.addWidget(self.backtest_all_check, 1, 6)
        op_g_box.addWidget(self.btn_backtest, 0, 7)
        self.op_group_box.setLayout(op_g_box)

        result_h_box = QHBoxLayout()
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
        self.table.setMinimumWidth(220)
        self.table.setMaximumWidth(250)
        self.info = QTextBrowser()
        self.info.setMinimumWidth(220)
        self.info.setMaximumWidth(250)

        left_v_box = QVBoxLayout()
        left_v_box.addWidget(self.table)
        left_v_box.addWidget(self.info)

        self.k_plt = pg.PlotWidget(enableMenu=False)
        self.k_plt.hideAxis('bottom')
        self.k_plt.plotItem.setMouseEnabled(y=False)
        self.info_label = pg.TextItem()
        result_h_box.addLayout(left_v_box)
        result_h_box.addWidget(self.k_plt)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.op_group_box)
        main_v_box.addLayout(result_h_box)

        self.setLayout(main_v_box)

        self.btn_backtest.clicked.connect(self.on_backtest)
        self.table.itemSelectionChanged.connect(self.on_row_changed)
        self.k_move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved,
                                          rateLimit=60,
                                          slot=self.emit_backtest_info)

    def on_option_change(self):
        check = self.sender()
        if check.isChecked():
            if check.text() == '自选股':
                self.backtest_option = 'fav'
            elif check.text() == '全部股票':
                self.backtest_option = 'all'

    def on_backtest(self):
        if self.backtest_option == 'fav':
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
        elif self.backtest_option == 'all':
            stocks = []
            rows = AStockInfo.select()
            for row in rows:
                if row.type == 1:
                    stocks.append({'code': row.code, 'name': row.name})

        for stock in stocks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(stock['code']))
            self.table.setItem(row, 1, QTableWidgetItem(stock['name']))

    def on_row_changed(self):
        row = self.table.currentRow()
        self.current_code = self.table.item(row, 0).text()
        self.current_name = self.table.item(row, 1).text()
        if self.current_strategy_name is not None:
            self.backtest(self.current_code, self.current_strategy_name)

    def set_code(self, code, name):
        self.current_code = code
        self.current_name = name
        if self.current_strategy_name is not None:
            self.backtest(self.current_code, self.current_strategy_name)

    def set_strategy(self, strategy_name):
        self.current_strategy_name = strategy_name
        if self.current_code is not None:
            self.backtest(self.current_code, self.current_strategy_name)

    def backtest(self, code, strategy_name):
        self.k_plt.plotItem.clear()
        self.opens = []
        self.closes = []
        self.highs = []
        self.lows = []
        self.volumes = []
        self.dates = []

        self.current_code = code
        self.current_strategy_name = strategy_name
        if self.current_code is None or self.current_strategy_name is None:
            return
        init_money = float(self.init_money_input.text()) * 10000
        fee = float(self.fee_input.text()) / 10000
        pass_fee = float(self.pass_fee_input.text()) / 10000
        tax = float(self.tax_input.text()) / 1000
        # NEW STRATEGIES #
        boll_info = BOLLInfo()
        dual_ma_info = DualMAInfo()
        kdj_info = KDJInfo()
        macd_info = MACDInfo()
        rsi_info = RSIInfo()
        turtle_info = TurtleInfo()
        wr_info = WRInfo()
        if self.current_strategy_name == boll_info.name:
            backtest = BOLL()
        elif self.current_strategy_name == dual_ma_info.name:
            backtest = DualMA()
        elif self.current_strategy_name == kdj_info.name:
            backtest = KDJ()
        elif self.current_strategy_name == macd_info.name:
            backtest = MACD()
        elif self.current_strategy_name == rsi_info.name:
            backtest = RSI()
        elif self.current_strategy_name == turtle_info.name:
            backtest = Turtle()
        elif self.current_strategy_name == wr_info.name:
            backtest = WR()
        _return, max_drawdown, \
        self.opens, self.closes, self.highs, self.lows, \
        self.volumes, self.dates, \
        opening_index_slices, opening_price_slices, \
        closing_index_slices, closing_price_slices = \
            backtest.backtest(self.current_code,
                              init_money, fee, pass_fee, tax)

        for i, obj in enumerate(opening_price_slices):
            if opening_price_slices[i][-1] > opening_price_slices[i][0]:
                pen_color = 'r'
                brush_color = (255, 0, 0, 100)
            else:
                pen_color = 'g'
                brush_color = (0, 255, 0, 100)
            self.k_plt.plot(x=opening_index_slices[i],
                            y=opening_price_slices[i],
                            pen=pen_color, fillLevel=0,
                            fillBrush=brush_color)
        y_min = min(self.closes)
        y_max = max(self.closes)
        self.k_plt.plot(y=self.closes, pen='w')
        self.k_plt.showGrid(True, True)
        self.k_plt.setYRange(y_min, y_max)
        self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
        self.k_plt.addItem(self.k_h_line, ignoreBounds=True)
        self.k_plt.addItem(self.info_label)

        self.info.setText(self.current_strategy_name)
        self.info.append(self.current_code + ' ' + self.current_name)
        self.info.append('收益率: ' + str(_return))
        self.info.append('最大回撤: ' + str(max_drawdown))

    def emit_backtest_info(self, event):
        pos = event[0]
        if self.k_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.k_plt.plotItem.vb.mapSceneToView(pos)
            index = int(mouse_point.x())
            if -1 < index < len(self.closes):
                self.info_label.setHtml(
                    "<p style='color:white'><strong>日期：{0}</strong></p>"
                    "<p style='color:white'>开盘：{1}</p>"
                    "<p style='color:white'>最高：{2}</p>"
                    "<p style='color:white'>最低：{3}</p>"
                    "<p style='color:white'>收盘：{4}</p>"
                    "<p style='color:white'>成交量：{5}</p>".format(
                        self.dates[index], self.opens[index], self.highs[index],
                        self.lows[index], self.closes[index],
                        self.volumes[index]))
                self.info_label.setPos(mouse_point.x(), mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.k_h_line.setPos(mouse_point.y())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Backtest()
    main.show()
    sys.exit(app.exec_())
