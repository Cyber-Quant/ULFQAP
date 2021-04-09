import json

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from conf.conf import factor_pool_config_path
from db.models import AStockIndex
from strategies.alligator import AlligatorChoose, AlligatorConfig, AlligatorInfo
from strategies.boll import BOLLChoose, BOLLConfig, BOLLInfo
from strategies.bottom_break_up import BottomBreakUpChoose, \
    BottomBreakUpConfig, BottomBreakUpInfo
from strategies.kdj import KDJChoose, KDJConfig, KDJInfo
from strategies.lucky_duck_head import LuckyDuckHeadChoose, \
    LuckyDuckHeadConfig, LuckyDuckHeadInfo
from strategies.macd import MACDChoose, MACDConfig, MACDInfo
from strategies.rsi import RSIChoose, RSIConfig, RSIInfo
from strategies.triple_golden_cross import TripleGoldenCrossChoose, \
    TripleGoldenCrossConfig, TripleGoldenCrossInfo
from widgets.plots import Plots


class Shape(Plots):
    def __init__(self, parent=None):
        super(Shape, self).__init__(parent)
        self.setWindowTitle('形态选股')

        self.factor_pool = []

        self.stocks_to_be_chosen = []
        self.stocks_pre_chose = []
        self.apply_strategies = []

        self.current_kline_period = 'd'
        self.choose_thread = None

        # NEW STRATEGIES #
        self.triple_golden_cross_info = TripleGoldenCrossInfo()
        self.lucky_duck_head_info = LuckyDuckHeadInfo()
        self.bottom_break_up_info = BottomBreakUpInfo()
        self.alligator_info = AlligatorInfo()
        self.boll_info = BOLLInfo()
        self.macd_info = MACDInfo()
        self.kdj_info = KDJInfo()
        self.rsi_info = RSIInfo()
        self.strategies = [
            self.triple_golden_cross_info.name,
            self.lucky_duck_head_info.name,
            self.bottom_break_up_info.name,
            self.alligator_info.name,
            self.boll_info.name,
            self.kdj_info.name,
            self.macd_info.name,
            self.rsi_info.name
        ]

        # TODO: make strategies plugin
        # NEW STRATEGIES #
        self.alligator_info = AlligatorInfo()
        self.boll_info = BOLLInfo()
        self.bottom_break_up_info = BottomBreakUpInfo()
        self.kdj_info = KDJInfo()
        self.lucky_duck_head_info = LuckyDuckHeadInfo()
        self.macd_info = MACDInfo()
        self.rsi_info = RSIInfo()
        self.triple_golden_cross_info = TripleGoldenCrossInfo()

        condition_v_box = QVBoxLayout()
        self.re_search_radio = QRadioButton('结果池')
        self.pool_search_radio = QRadioButton('股票池')
        self.all_search_radio = QRadioButton('全部股票')
        self.all_search_radio.setChecked(True)
        condition_v_box.addWidget(self.re_search_radio)
        condition_v_box.addWidget(self.pool_search_radio)
        condition_v_box.addWidget(self.all_search_radio)

        op_v_box = QVBoxLayout()
        self.btn_choose = QPushButton('选股')
        self.btn_stop_choose = QPushButton('停止')
        self.btn_stop_choose.setDisabled(True)
        op_v_box.addWidget(self.btn_choose)
        op_v_box.addWidget(self.btn_stop_choose)

        op_h_box = QHBoxLayout()
        op_h_box.addLayout(condition_v_box)
        op_h_box.addLayout(op_v_box)

        self.filter_group_box = QGroupBox()
        choose_v_box = QVBoxLayout()
        choose_v_box.addLayout(op_h_box)
        self.filter_group_box.setLayout(choose_v_box)

        self.progress_bar = QProgressBar()

        self.strategy_table = QTableWidget()
        self.strategy_table.setColumnCount(1)
        self.strategy_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.strategy_table.horizontalHeader().setVisible(False)
        self.strategy_table.verticalHeader().setVisible(False)
        self.strategy_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.strategy_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.strategy_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.strategy_table.setSortingEnabled(True)
        self.strategy_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.strategy_table.customContextMenuRequested.connect(
            self.open_strategy_table_menu)
        self.strategy_table.itemSelectionChanged.connect(
            self.on_row_changed)
        self.strategy_table.setRowCount(len(self.strategies))

        for i, strategy in enumerate(self.strategies):
            item_name = QTableWidgetItem(self.strategies[i])
            item_name.setTextAlignment(Qt.AlignCenter)
            self.strategy_table.setItem(i, 0, item_name)

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
        left_v_box.addWidget(self.strategy_table)
        left_v_box.addWidget(self.table)

        self.left_widget = QWidget()
        self.left_widget.setLayout(left_v_box)
        self.left_widget.setMinimumWidth(220)
        self.left_widget.setMaximumWidth(250)

        self.m1_radio = QRadioButton('1分')
        self.m5_radio = QRadioButton('5分')
        self.m15_radio = QRadioButton('15分')
        self.m30_radio = QRadioButton('30分')
        self.hour_radio = QRadioButton('60分')
        self.day_radio = QRadioButton('日')
        self.day_radio.setChecked(True)
        self.week_radio = QRadioButton('周')
        self.month_radio = QRadioButton('月')
        self.m1_radio.toggled.connect(self.on_period_change)
        self.m5_radio.toggled.connect(self.on_period_change)
        self.m15_radio.toggled.connect(self.on_period_change)
        self.m30_radio.toggled.connect(self.on_period_change)
        self.hour_radio.toggled.connect(self.on_period_change)
        self.day_radio.toggled.connect(self.on_period_change)
        self.week_radio.toggled.connect(self.on_period_change)
        self.month_radio.toggled.connect(self.on_period_change)

        self.period_widget = QGroupBox()
        period_g_box = QGridLayout()
        period_g_box.addWidget(self.m1_radio, 0, 0)
        period_g_box.addWidget(self.m5_radio, 0, 1)
        period_g_box.addWidget(self.m15_radio, 0, 2)
        period_g_box.addWidget(self.m30_radio, 0, 3)
        period_g_box.addWidget(self.hour_radio, 0, 4)
        period_g_box.addWidget(self.day_radio, 0, 5)
        period_g_box.addWidget(self.week_radio, 0, 6)
        period_g_box.addWidget(self.month_radio, 0, 7)
        period_g_box.setContentsMargins(0, 0, 0, 0)
        self.period_widget.setLayout(period_g_box)

        self.period_group = QButtonGroup()
        self.period_group.addButton(self.m1_radio)
        self.period_group.addButton(self.m5_radio)
        self.period_group.addButton(self.m15_radio)
        self.period_group.addButton(self.m30_radio)
        self.period_group.addButton(self.hour_radio)
        self.period_group.addButton(self.day_radio)
        self.period_group.addButton(self.week_radio)
        self.period_group.addButton(self.month_radio)

        info_h_box = QHBoxLayout()
        info_h_box.addWidget(self.period_widget)

        right_v_box = QVBoxLayout()

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
        self.table.itemSelectionChanged.connect(self.on_row_changed)

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
            elif check.text() == '60分':
                self.current_kline_period = '60'
            if check.text() == '日':
                self.current_kline_period = 'd'
            elif check.text() == '周':
                self.current_kline_period = 'w'
            elif check.text() == '月':
                self.current_kline_period = 'm'
        self.re_render_all_plots(self.current_kline_code)

    def on_row_changed(self):
        row = self.table.currentRow()
        if row == -1:
            return
        code = self.table.item(row, 0).text()
        row = self.strategy_table.currentRow()
        if row == -1:
            return
        strategy = self.strategy_table.item(row, 0).text()
        self.render_all_plots(code)
        self.re_draw_indicators(strategy)

    def disable_all(self):
        self.re_search_radio.setDisabled(True)
        self.btn_choose.setDisabled(True)
        self.btn_stop_choose.setEnabled(True)

    def enable_all(self):
        self.re_search_radio.setEnabled(True)
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

        if self.re_search_radio.isChecked():
            self.stocks_to_be_chosen = self.stocks_pre_chose.copy()
            self.stocks_pre_chose.clear()
        elif self.pool_search_radio.isChecked():
            if not factor_pool_config_path.exists():
                self.factor_pool = []
            else:
                with open(factor_pool_config_path, 'r', encoding='utf-8') as f:
                    self.factor_pool = json.load(f)
            self.stocks_to_be_chosen = self.factor_pool.copy()
        else:
            self.stocks_to_be_chosen.clear()
            stocks = AStockIndex.select()
            for stock in stocks:
                _stock = {
                    'code': stock.code,
                    'name': stock.name
                }
                self.stocks_to_be_chosen.append(_stock)

        row = self.strategy_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, '警告', '请先选择一个策略',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.enable_all()
        else:
            strategy = self.strategy_table.item(row, 0).text()
            # NEW STRATEGIES #
            if strategy == self.alligator_info.name:
                self.choose_thread = AlligatorChoose(
                    self.stocks_to_be_chosen)
            elif strategy == self.boll_info.name:
                self.choose_thread = BOLLChoose(self.stocks_to_be_chosen)
            elif strategy == self.bottom_break_up_info.name:
                self.choose_thread = BottomBreakUpChoose(
                    self.stocks_to_be_chosen)
            elif strategy == self.kdj_info.name:
                self.choose_thread = KDJChoose(self.stocks_to_be_chosen)
            elif strategy == self.lucky_duck_head_info.name:
                self.choose_thread = LuckyDuckHeadChoose(
                    self.stocks_to_be_chosen)
            elif strategy == self.macd_info.name:
                self.choose_thread = MACDChoose(self.stocks_to_be_chosen)
            elif strategy == self.rsi_info.name:
                self.choose_thread = RSIChoose(self.stocks_to_be_chosen)
            elif strategy == \
                    self.triple_golden_cross_info.name:
                self.choose_thread = TripleGoldenCrossChoose(
                    self.stocks_to_be_chosen)

            self.choose_thread.progress_signal.connect(
                self.set_progress_bar)
            self.choose_thread.start()

    def on_stop_choose(self):
        self.choose_thread.terminate()
        self.enable_all()

    def open_pool_ops_menu(self, position):
        pop_menu = QMenu()
        remove_action = QAction('删除', self)
        pop_menu.addAction(remove_action)

        remove_action.triggered.connect(self.on_remove)
        pop_menu.exec_(self.table.mapToGlobal(position))

    def on_remove(self):
        rows = self.table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                stock = {
                    'code': self.table.item(row.row(), 0).text(),
                    'name': self.table.item(row.row(), 1).text()
                }
                if stock in self.stocks_pre_chose:
                    self.stocks_pre_chose.remove(stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.table.removeRow(row_idx)

    def open_strategy_table_menu(self, pos):
        pop_menu = QMenu()
        setting_action = QAction('详情/设置', self)
        pop_menu.addAction(setting_action)

        setting_action.triggered.connect(self.on_strategy_setting)
        pop_menu.exec_(self.strategy_table.mapToGlobal(pos))

    def on_strategy_setting(self):
        row = self.strategy_table.currentIndex().row()
        name = self.strategy_table.item(row, 1).text()
        # NEW STRATEGIES #
        if name == self.triple_golden_cross_info.name:
            cfg_dlg = TripleGoldenCrossConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.lucky_duck_head_info.name:
            cfg_dlg = LuckyDuckHeadConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.bottom_break_up_info.name:
            cfg_dlg = BottomBreakUpConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.alligator_info.name:
            cfg_dlg = AlligatorConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.boll_info.name:
            cfg_dlg = BOLLConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.kdj_info.name:
            cfg_dlg = KDJConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.macd_info.name:
            cfg_dlg = MACDConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.rsi_info.name:
            cfg_dlg = RSIConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Shape()
    main.show()
    sys.exit(app.exec_())
