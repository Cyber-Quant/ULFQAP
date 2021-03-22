import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import fav_stocks_config_path, apply_strategies_config_path, \
    stock_pool_config_path
from db.models import AStockIndex
from strategies.alligator import AlligatorChoose, AlligatorInfo
from strategies.boll import BOLLChoose, BOLLInfo
from strategies.bottom_break_up import BottomBreakUpChoose, BottomBreakUpInfo
from strategies.common import get_stat_date, get_value_info
from strategies.kdj import KDJChoose, KDJInfo
from strategies.lucky_duck_head import LuckyDuckHeadChoose, LuckyDuckHeadInfo
from strategies.macd import MACDChoose, MACDInfo
from strategies.mcst import MCSTInfo
from strategies.percent_change import PercentChangeChoose, PercentChangeInfo
from strategies.rsi import RSIChoose, RSIInfo
from strategies.triple_golden_cross import TripleGoldenCrossChoose, \
    TripleGoldenCrossInfo
from strategies.turn_over import TurnOverChoose, TurnOverInfo
from strategies.volume_increase import VolumeIncreaseChoose, VolumeIncreaseInfo
from strategies.wr import WRChoose, WRInfo
from utils.custom_add_dialog import CustomAddDialog
from widgets.plots import Plots


class Choose(Plots):
    fav_stock_changed_signal = Signal()
    kline_info_signal = Signal(str, float, float, float, float, int)

    def __init__(self, parent=None):
        super(Choose, self).__init__(parent)
        self.setWindowTitle('选股')

        self.fav_stocks = []
        self.stock_pool = []

        self.stocks_to_be_chosen = []
        self.stocks_pre_chose = []
        self.apply_strategies = []

        self.current_kline_period = 'd'

        self.stat_date = get_stat_date()

        self.choose_thread = None
        # TODO: make strategies plugin
        # NEW STRATEGIES #
        self.alligator_info = AlligatorInfo()
        self.boll_info = BOLLInfo()
        self.bottom_break_up_info = BottomBreakUpInfo()
        self.kdj_info = KDJInfo()
        self.lucky_duck_head_info = LuckyDuckHeadInfo()
        self.macd_info = MACDInfo()
        self.mcst_info = MCSTInfo()
        self.percent_change_info = PercentChangeInfo()
        self.rsi_info = RSIInfo()
        self.triple_golden_cross_info = TripleGoldenCrossInfo()
        self.turn_over_info = TurnOverInfo()
        self.volume_increase_info = VolumeIncreaseInfo()
        self.wr_info = WRInfo()

        condition_v_box = QVBoxLayout()
        self.re_search_radio = QRadioButton('从结果中再选')
        self.pool_search_radio = QRadioButton('从股票池中选')
        self.all_search_radio = QRadioButton('从全部股票中选')
        self.all_search_radio.setChecked(True)
        condition_v_box.addWidget(self.re_search_radio)
        condition_v_box.addWidget(self.pool_search_radio)
        condition_v_box.addWidget(self.all_search_radio)

        op_v_box = QVBoxLayout()
        self.btn_choose = QPushButton('策略选股')
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
        self.volume_label = QLabel('量')
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

        basic_info_g_box = QGridLayout()
        self.roe_label = QLabel('ROE')
        self.roe_input = QLineEdit()
        self.roe_input.setDisabled(True)
        self.ito_label = QLabel('存货率')
        self.ito_input = QLineEdit()
        self.ito_input.setDisabled(True)
        self.artr_label = QLabel('应收帐款率')
        self.artr_input = QLineEdit()
        self.artr_input.setDisabled(True)
        self.dar_label = QLabel('资产负债率')
        self.dar_input = QLineEdit()
        self.dar_input.setDisabled(True)
        basic_info_g_box.addWidget(self.roe_label, 0, 6)
        basic_info_g_box.addWidget(self.roe_input, 0, 7)
        basic_info_g_box.addWidget(self.ito_label, 1, 6)
        basic_info_g_box.addWidget(self.ito_input, 1, 7)
        basic_info_g_box.addWidget(self.artr_label, 0, 8)
        basic_info_g_box.addWidget(self.artr_input, 0, 9)
        basic_info_g_box.addWidget(self.dar_label, 1, 8)
        basic_info_g_box.addWidget(self.dar_input, 1, 9)
        self.basic_info_widget = QGroupBox()
        self.basic_info_widget.setLayout(basic_info_g_box)

        self.day_radio = QRadioButton('日')
        self.day_radio.setChecked(True)
        self.week_radio = QRadioButton('周')
        self.month_radio = QRadioButton('月')
        self.day_radio.toggled.connect(self.on_period_change)
        self.week_radio.toggled.connect(self.on_period_change)
        self.month_radio.toggled.connect(self.on_period_change)

        self.period_widget = QGroupBox()
        period_g_box = QGridLayout()
        period_g_box.addWidget(self.day_radio, 0, 0)
        period_g_box.addWidget(self.week_radio, 0, 1)
        period_g_box.addWidget(self.month_radio, 0, 2)
        period_g_box.setContentsMargins(0, 0, 0, 0)
        self.period_widget.setLayout(period_g_box)

        self.period_group = QButtonGroup()
        self.period_group.addButton(self.day_radio)
        self.period_group.addButton(self.week_radio)
        self.period_group.addButton(self.month_radio)

        info_h_box = QHBoxLayout()
        info_h_box.addWidget(self.period_widget)
        info_h_box.addWidget(self.basic_info_widget)
        info_h_box.addWidget(self.info_widget)

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
        if row == -1:
            return
        code = self.table.item(row, 0).text()
        self.render_all_plots(code)
        self.re_draw_indicators(self.current_indicator_name)
        self.display_basic_info(code)

    def display_basic_info(self, code):
        _, _, roe, ltv, ito, artr, dar = get_value_info(
            code, self.stat_date)
        self._display_basic_info(roe, ito, artr, dar)

    def _display_basic_info(self, roe, ito, artr, dar):
        self.roe_input.setText(str(roe))
        self.ito_input.setText(str(ito))
        self.artr_input.setText(str(artr))
        self.dar_input.setText(str(dar))

    def on_kline_info_changed(self, date, _open, close, high, low, volume):
        self.date_input.setText(date)
        self.open_input.setText(str(_open))
        self.close_input.setText(str(close))
        self.high_input.setText(str(high))
        self.low_input.setText(str(low))
        self.volume_input.setText(str(volume))

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
            if not stock_pool_config_path.exists():
                self.stock_pool = []
            else:
                with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                    self.stock_pool = json.load(f)
            self.stocks_to_be_chosen = self.stock_pool.copy()
        else:
            self.stocks_to_be_chosen.clear()
            stocks = AStockIndex.select()
            for stock in stocks:
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
                if self.apply_strategies[0] == self.alligator_info.name:
                    self.choose_thread = AlligatorChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.boll_info.name:
                    self.choose_thread = BOLLChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.bottom_break_up_info.name:
                    self.choose_thread = BottomBreakUpChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.kdj_info.name:
                    self.choose_thread = KDJChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.lucky_duck_head_info.name:
                    self.choose_thread = LuckyDuckHeadChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.macd_info.name:
                    self.choose_thread = MACDChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.percent_change_info.name:
                    self.choose_thread = PercentChangeChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.rsi_info.name:
                    self.choose_thread = RSIChoose(self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == \
                        self.triple_golden_cross_info.name:
                    self.choose_thread = TripleGoldenCrossChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.turn_over_info.name:
                    self.choose_thread = TurnOverChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.volume_increase_info.name:
                    self.choose_thread = VolumeIncreaseChoose(
                        self.stocks_to_be_chosen)
                elif self.apply_strategies[0] == self.wr_info.name:
                    self.choose_thread = WRChoose(self.stocks_to_be_chosen)
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
