import datetime
import json
import pyqtgraph as pg

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import fav_stocks_config_path, FIRST_DAY_YEAR, \
    FIRST_DAY_MONTH, FIRST_DAY_DAY
from db.models import AStockIndex
from strategies.alligator import Alligator, AlligatorBacktest, AlligatorInfo
from strategies.boll import BOLL, BOLLBacktest, BOLLInfo
from strategies.bottom_break_up import BottomBreakUp, BottomBreakUpBacktest, \
    BottomBreakUpInfo
from strategies.kdj import KDJ, KDJBacktest, KDJInfo
from strategies.lucky_duck_head import LuckyDuckHead, LuckyDuckHeadBacktest, \
    LuckyDuckHeadInfo
from strategies.macd import MACD, MACDBacktest, MACDInfo
from strategies.rsi import RSI, RSIBacktest, RSIInfo
from strategies.triple_golden_cross import TripleGoldenCross, \
    TripleGoldenCrossBacktest, TripleGoldenCrossInfo
from strategies.wr import WR, WRBacktest, WRInfo


class Backtest(QWidget):
    fav_stock_changed_signal = Signal()

    def __init__(self, parent=None):
        super(Backtest, self).__init__(parent)
        self.setWindowTitle('回测')

        self.fav_stocks = None
        self.backtest_thread = None
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

        self.progress_bar = QProgressBar()

        self.op_group_box = QGroupBox()
        op_g_box = QGridLayout()
        self.start_date_label = QLabel('起始日期')
        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setMinimumDate(QDate(FIRST_DAY_YEAR, FIRST_DAY_MONTH,
                                             FIRST_DAY_DAY))
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-365))
        self.start_date.setDate(QDate(FIRST_DAY_YEAR, FIRST_DAY_MONTH,
                                      FIRST_DAY_DAY))

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

        self.btn_backtest = QPushButton('批量回测')
        self.btn_stop_backtest = QPushButton('停止回测')
        self.btn_stop_backtest.setDisabled(True)

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
        op_g_box.addWidget(self.btn_stop_backtest, 1, 7)
        self.op_group_box.setLayout(op_g_box)

        result_h_box = QHBoxLayout()
        self.table = QTableWidget()
        headers = ['代码', '股票', '胜率', '收益率', '最大回撤率']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setMinimumWidth(370)
        self.table.setMaximumWidth(500)

        left_v_box = QVBoxLayout()
        left_v_box.addWidget(self.table)

        self.k_plt = pg.PlotWidget(enableMenu=False)
        self.k_plt.hideAxis('bottom')
        self.k_plt.plotItem.setMouseEnabled(y=False)
        self.info_label = pg.TextItem()
        result_h_box.addLayout(left_v_box)
        result_h_box.addWidget(self.k_plt)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addWidget(self.op_group_box)
        main_v_box.addLayout(result_h_box)

        self.setLayout(main_v_box)

        self.btn_backtest.clicked.connect(self.on_backtest)
        self.btn_stop_backtest.clicked.connect(self.on_stop_backtest)
        self.table.customContextMenuRequested.connect(self.open_ops_menu)
        self.table.itemSelectionChanged.connect(self.on_row_changed)
        self.k_move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved,
                                          rateLimit=60,
                                          slot=self.emit_backtest_info)

    def enable_all(self):
        self.btn_backtest.setEnabled(True)
        self.btn_stop_backtest.setDisabled(True)
        self.backtest_fav_check.setEnabled(True)
        self.backtest_all_check.setEnabled(True)
        self.start_date.setEnabled(True)
        self.end_date.setEnabled(True)

    def disable_all(self):
        self.btn_backtest.setDisabled(True)
        self.btn_stop_backtest.setEnabled(True)
        self.backtest_fav_check.setDisabled(True)
        self.backtest_all_check.setDisabled(True)
        self.start_date.setDisabled(True)
        self.end_date.setDisabled(True)

    def set_progress_bar(self, value, code, name, wpct, _return, max_drawdown):
        self.progress_bar.setValue(value)
        if value == 100:
            self.enable_all()
        else:
            wpct_str = str(round(wpct, 2))
            return_str = str(round(_return, 2))
            max_drawdown_str = str(round(max_drawdown, 2))
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(wpct_str))
            self.table.setItem(row, 3, QTableWidgetItem(return_str))
            self.table.setItem(row, 4, QTableWidgetItem(max_drawdown_str))

    def on_option_change(self):
        check = self.sender()
        if check.isChecked():
            if check.text() == '自选股':
                self.backtest_option = 'fav'
            elif check.text() == '全部股票':
                self.backtest_option = 'all'

    def on_stop_backtest(self):
        self.backtest_thread.terminate()
        self.enable_all()

    def on_backtest(self):
        self.disable_all()

        rows = self.table.rowCount()
        for i in reversed(range(rows)):
            self.table.removeRow(i)

        stocks = []
        if self.backtest_option == 'fav':
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
        elif self.backtest_option == 'all':
            rows = AStockIndex.select()
            for row in rows:
                stocks.append({'code': row.code, 'name': row.name})

        if self.current_strategy_name is None:
            QMessageBox.warning(self, '警告', '请选择一个策略进行回测',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.enable_all()
            return

        s_date = self.start_date.date().toString('yyyy-MM-dd')
        e_date = self.end_date.date().toString('yyyy-MM-dd')
        init_money = float(self.init_money_input.text()) * 10000
        fee = float(self.fee_input.text()) / 10000
        pass_fee = float(self.pass_fee_input.text()) / 10000
        tax = float(self.tax_input.text()) / 1000
        # NEW STRATEGIES #
        alligator_info = AlligatorInfo()
        boll_info = BOLLInfo()
        bottom_break_up_info = BottomBreakUpInfo()
        kdj_info = KDJInfo()
        lucky_duck_head_info = LuckyDuckHeadInfo()
        macd_info = MACDInfo()
        rsi_info = RSIInfo()
        triple_golden_cross_info = TripleGoldenCrossInfo()
        wr_info = WRInfo()
        if self.current_strategy_name == alligator_info.name:
            self.backtest_thread = AlligatorBacktest(stocks, s_date, e_date,
                                                     init_money, fee,
                                                     pass_fee, tax)
        elif self.current_strategy_name == boll_info.name:
            self.backtest_thread = BOLLBacktest(stocks, s_date, e_date,
                                                init_money, fee,
                                                pass_fee, tax)
        elif self.current_strategy_name == bottom_break_up_info.name:
            self.backtest_thread = BottomBreakUpBacktest(stocks, s_date, e_date,
                                                         init_money, fee,
                                                         pass_fee, tax)
        elif self.current_strategy_name == kdj_info.name:
            self.backtest_thread = KDJBacktest(stocks, s_date, e_date,
                                               init_money, fee,
                                               pass_fee, tax)
        elif self.current_strategy_name == lucky_duck_head_info.name:
            self.backtest_thread = LuckyDuckHeadBacktest(stocks, s_date, e_date,
                                                         init_money, fee,
                                                         pass_fee, tax)
        elif self.current_strategy_name == macd_info.name:
            self.backtest_thread = MACDBacktest(stocks, s_date, e_date,
                                                init_money, fee,
                                                pass_fee, tax)
        elif self.current_strategy_name == rsi_info.name:
            self.backtest_thread = RSIBacktest(stocks, s_date, e_date,
                                               init_money, fee,
                                               pass_fee, tax)
        elif self.current_strategy_name == triple_golden_cross_info.name:
            self.backtest_thread = TripleGoldenCrossBacktest(stocks, s_date,
                                                             e_date,
                                                             init_money, fee,
                                                             pass_fee, tax)
        elif self.current_strategy_name == wr_info.name:
            self.backtest_thread = WRBacktest(stocks, s_date, e_date,
                                              init_money, fee,
                                              pass_fee, tax)
        else:
            QMessageBox.warning(self, '警告', '该策略不支持回测，请换一个',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.enable_all()
            return
        self.backtest_thread.progress_signal.connect(
            self.set_progress_bar)
        self.backtest_thread.start()

    def on_row_changed(self):
        row = self.table.currentRow()
        if row == -1:
            return
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
        s_date = self.start_date.date().toString('yyyy-MM-dd')
        e_date = self.end_date.date().toString('yyyy-MM-dd')
        s_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
        e_date = datetime.datetime.strptime(e_date, '%Y-%m-%d')
        init_money = float(self.init_money_input.text()) * 10000
        fee = float(self.fee_input.text()) / 10000
        pass_fee = float(self.pass_fee_input.text()) / 10000
        tax = float(self.tax_input.text()) / 1000
        # NEW STRATEGIES #
        alligator_info = AlligatorInfo()
        boll_info = BOLLInfo()
        bottom_break_up_info = BottomBreakUpInfo()
        kdj_info = KDJInfo()
        lucky_duck_head_info = LuckyDuckHeadInfo()
        macd_info = MACDInfo()
        rsi_info = RSIInfo()
        triple_golden_cross_info = TripleGoldenCrossInfo()
        wr_info = WRInfo()
        if self.current_strategy_name == alligator_info.name:
            backtest = Alligator()
        elif self.current_strategy_name == boll_info.name:
            backtest = BOLL()
        elif self.current_strategy_name == bottom_break_up_info.name:
            backtest = BottomBreakUp()
        elif self.current_strategy_name == kdj_info.name:
            backtest = KDJ()
        elif self.current_strategy_name == lucky_duck_head_info.name:
            backtest = LuckyDuckHead()
        elif self.current_strategy_name == macd_info.name:
            backtest = MACD()
        elif self.current_strategy_name == rsi_info.name:
            backtest = RSI()
        elif self.current_strategy_name == triple_golden_cross_info.name:
            backtest = TripleGoldenCross()
        elif self.current_strategy_name == wr_info.name:
            backtest = WR()
        wpct, _return, max_drawdown, \
        self.opens, self.closes, self.highs, self.lows, \
        self.volumes, self.dates, \
        opening_index_slices, opening_price_slices, \
        closing_index_slices, closing_price_slices = \
            backtest.backtest(self.current_code, s_date, e_date,
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

    def emit_backtest_info(self, event):
        pos = event[0]
        if self.k_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.k_plt.plotItem.vb.mapSceneToView(pos)
            index = int(mouse_point.x())
            if self.closes is not None and -1 < index < len(self.closes):
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

    def open_ops_menu(self, position):
        pop_menu = QMenu()
        fav_action = QAction('加入自选', self)
        pop_menu.addAction(fav_action)

        fav_action.triggered.connect(self.on_fav)
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Backtest()
    main.show()
    sys.exit(app.exec_())
