import datetime
import json

from pathlib import Path
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from conf.conf import factor_strategies_config_path, factor_pool_config_path
from strategies.factor import FactorChoose
from utils.factor_saveas_dialog import FactorSaveAsDialog


def condition_changed(text, widget):
    if '区间' in text:
        widget.setVisible(True)
    else:
        widget.setVisible(False)


class Factor(QWidget):
    def __init__(self, parent=None):
        super(Factor, self).__init__(parent)
        self.setWindowTitle('因子选股')

        self.factor_thread = None
        self.factor_pool = []

        self.progress_bar = QProgressBar()

        self.tabs = QTabWidget()
        self.tab_filter = QWidget()
        self.tab_sort = QWidget()
        self.tab_backtest = QWidget()
        self.tabs.addTab(self.tab_filter, '筛选')
        self.tabs.addTab(self.tab_sort, '排序')
        self.tabs.addTab(self.tab_backtest, '回测')

        int_validator = QIntValidator()

        filter_condition = ['大于', '小于', '区间', '等于',
                            '排名最小', '排名最大', '排名区间']
        filter_condition_gird_box = QGridLayout()
        self.filter_pe_group = QGroupBox()
        self.filter_pe_check = QCheckBox('PE')
        self.filter_pe_choose = QComboBox()
        self.filter_pe_choose.addItems(filter_condition)
        self.filter_pe_input = QLineEdit()
        self.filter_pe_input.setValidator(int_validator)
        self.filter_pe_input2 = QLineEdit()
        self.filter_pe_input2.setValidator(int_validator)
        self.filter_pe_input2.setVisible(False)
        filter_pe_h_box = QHBoxLayout()
        filter_pe_h_box.addWidget(self.filter_pe_check)
        filter_pe_h_box.addWidget(self.filter_pe_choose)
        filter_pe_h_box.addWidget(self.filter_pe_input)
        filter_pe_h_box.addWidget(self.filter_pe_input2)
        self.filter_pe_group.setLayout(filter_pe_h_box)
        self.filter_pe_choose.activated[str].connect(
            self.filter_pe_condition_changed)

        self.filter_roe_group = QGroupBox()
        self.filter_roe_check = QCheckBox('ROE')
        self.filter_roe_choose = QComboBox()
        self.filter_roe_choose.addItems(filter_condition)
        self.filter_roe_input = QLineEdit()
        self.filter_roe_input.setValidator(int_validator)
        self.filter_roe_input2 = QLineEdit()
        self.filter_roe_input2.setValidator(int_validator)
        self.filter_roe_input2.setVisible(False)
        filter_roe_h_box = QHBoxLayout()
        filter_roe_h_box.addWidget(self.filter_roe_check)
        filter_roe_h_box.addWidget(self.filter_roe_choose)
        filter_roe_h_box.addWidget(self.filter_roe_input)
        filter_roe_h_box.addWidget(self.filter_roe_input2)
        self.filter_roe_group.setLayout(filter_roe_h_box)
        self.filter_roe_choose.activated[str].connect(
            self.filter_roe_condition_changed)

        self.filter_cmv_group = QGroupBox()
        self.filter_cmv_check = QCheckBox('流通市值')
        self.filter_cmv_choose = QComboBox()
        self.filter_cmv_choose.addItems(filter_condition)
        self.filter_cmv_input = QLineEdit()
        self.filter_cmv_input.setValidator(int_validator)
        self.filter_cmv_input2 = QLineEdit()
        self.filter_cmv_input2.setValidator(int_validator)
        self.filter_cmv_input2.setVisible(False)
        filter_cmv_h_box = QHBoxLayout()
        filter_cmv_h_box.addWidget(self.filter_cmv_check)
        filter_cmv_h_box.addWidget(self.filter_cmv_choose)
        filter_cmv_h_box.addWidget(self.filter_cmv_input)
        filter_cmv_h_box.addWidget(self.filter_cmv_input2)
        self.filter_cmv_group.setLayout(filter_cmv_h_box)
        self.filter_cmv_choose.activated[str].connect(
            self.filter_cmv_condition_changed)

        self.filter_ito_group = QGroupBox()
        self.filter_ito_check = QCheckBox('存货率')
        self.filter_ito_choose = QComboBox()
        self.filter_ito_choose.addItems(filter_condition)
        self.filter_ito_input = QLineEdit()
        self.filter_ito_input.setValidator(int_validator)
        self.filter_ito_input2 = QLineEdit()
        self.filter_ito_input2.setValidator(int_validator)
        self.filter_ito_input2.setVisible(False)
        filter_ito_h_box = QHBoxLayout()
        filter_ito_h_box.addWidget(self.filter_ito_check)
        filter_ito_h_box.addWidget(self.filter_ito_choose)
        filter_ito_h_box.addWidget(self.filter_ito_input)
        filter_ito_h_box.addWidget(self.filter_ito_input2)
        self.filter_ito_group.setLayout(filter_ito_h_box)
        self.filter_ito_choose.activated[str].connect(
            self.filter_ito_condition_changed)

        self.filter_artr_group = QGroupBox()
        self.filter_artr_check = QCheckBox('应收帐款率')
        self.filter_artr_choose = QComboBox()
        self.filter_artr_choose.addItems(filter_condition)
        self.filter_artr_input = QLineEdit()
        self.filter_artr_input.setValidator(int_validator)
        self.filter_artr_input2 = QLineEdit()
        self.filter_artr_input2.setValidator(int_validator)
        self.filter_artr_input2.setVisible(False)
        filter_artr_h_box = QHBoxLayout()
        filter_artr_h_box.addWidget(self.filter_artr_check)
        filter_artr_h_box.addWidget(self.filter_artr_choose)
        filter_artr_h_box.addWidget(self.filter_artr_input)
        filter_artr_h_box.addWidget(self.filter_artr_input2)
        self.filter_artr_group.setLayout(filter_artr_h_box)
        self.filter_artr_choose.activated[str].connect(
            self.filter_artr_condition_changed)

        self.filter_dar_group = QGroupBox()
        self.filter_dar_check = QCheckBox('资产负债率')
        self.filter_dar_choose = QComboBox()
        self.filter_dar_choose.addItems(filter_condition)
        self.filter_dar_input = QLineEdit()
        self.filter_dar_input.setValidator(int_validator)
        self.filter_dar_input2 = QLineEdit()
        self.filter_dar_input2.setValidator(int_validator)
        self.filter_dar_input2.setVisible(False)
        filter_dar_h_box = QHBoxLayout()
        filter_dar_h_box.addWidget(self.filter_dar_check)
        filter_dar_h_box.addWidget(self.filter_dar_choose)
        filter_dar_h_box.addWidget(self.filter_dar_input)
        filter_dar_h_box.addWidget(self.filter_dar_input2)
        self.filter_dar_group.setLayout(filter_dar_h_box)
        self.filter_dar_choose.activated[str].connect(
            self.filter_dar_condition_changed)

        self.filter_ltv_group = QGroupBox()
        self.filter_ltv_check = QCheckBox('质押率')
        self.filter_ltv_check.setDisabled(True)
        self.filter_ltv_choose = QComboBox()
        self.filter_ltv_choose.addItems(filter_condition)
        self.filter_ltv_input = QLineEdit()
        self.filter_ltv_input.setValidator(int_validator)
        self.filter_ltv_input2 = QLineEdit()
        self.filter_ltv_input2.setValidator(int_validator)
        self.filter_ltv_input2.setVisible(False)
        filter_ltv_h_box = QHBoxLayout()
        filter_ltv_h_box.addWidget(self.filter_ltv_check)
        filter_ltv_h_box.addWidget(self.filter_ltv_choose)
        filter_ltv_h_box.addWidget(self.filter_ltv_input)
        filter_ltv_h_box.addWidget(self.filter_ltv_input2)
        self.filter_ltv_group.setLayout(filter_ltv_h_box)
        self.filter_ltv_choose.activated[str].connect(
            self.filter_ltv_condition_changed)

        self.filter_op_group = QGroupBox()
        self.filter_op_check = QCheckBox('开盘价')
        self.filter_op_choose = QComboBox()
        self.filter_op_choose.addItems(filter_condition)
        self.filter_op_input = QLineEdit()
        self.filter_op_input.setValidator(int_validator)
        self.filter_op_input2 = QLineEdit()
        self.filter_op_input2.setValidator(int_validator)
        self.filter_op_input2.setVisible(False)
        filter_op_h_box = QHBoxLayout()
        filter_op_h_box.addWidget(self.filter_op_check)
        filter_op_h_box.addWidget(self.filter_op_choose)
        filter_op_h_box.addWidget(self.filter_op_input)
        filter_op_h_box.addWidget(self.filter_op_input2)
        self.filter_op_group.setLayout(filter_op_h_box)
        self.filter_op_choose.activated[str].connect(
            self.filter_op_condition_changed)

        self.filter_last_turn_over_group = QGroupBox()
        self.filter_last_turn_over_check = QCheckBox('昨换手率')
        self.filter_last_turn_over_choose = QComboBox()
        self.filter_last_turn_over_choose.addItems(filter_condition)
        self.filter_last_turn_over_input = QLineEdit()
        self.filter_last_turn_over_input.setValidator(int_validator)
        self.filter_last_turn_over_input2 = QLineEdit()
        self.filter_last_turn_over_input2.setValidator(int_validator)
        self.filter_last_turn_over_input2.setVisible(False)
        filter_last_turn_over_h_box = QHBoxLayout()
        filter_last_turn_over_h_box.addWidget(self.filter_last_turn_over_check)
        filter_last_turn_over_h_box.addWidget(self.filter_last_turn_over_choose)
        filter_last_turn_over_h_box.addWidget(self.filter_last_turn_over_input)
        filter_last_turn_over_h_box.addWidget(self.filter_last_turn_over_input2)
        self.filter_last_turn_over_group.setLayout(filter_last_turn_over_h_box)
        self.filter_last_turn_over_choose.activated[str].connect(
            self.filter_last_turn_over_condition_changed)

        self.filter_last_percent_change_group = QGroupBox()
        self.filter_last_percent_change_check = QCheckBox('昨涨跌幅')
        self.filter_last_percent_change_choose = QComboBox()
        self.filter_last_percent_change_choose.addItems(filter_condition)
        self.filter_last_percent_change_input = QLineEdit()
        self.filter_last_percent_change_input.setValidator(int_validator)
        self.filter_last_percent_change_input2 = QLineEdit()
        self.filter_last_percent_change_input2.setValidator(int_validator)
        self.filter_last_percent_change_input2.setVisible(False)
        filter_last_percent_change_h_box = QHBoxLayout()
        filter_last_percent_change_h_box.addWidget(
            self.filter_last_percent_change_check)
        filter_last_percent_change_h_box.addWidget(
            self.filter_last_percent_change_choose)
        filter_last_percent_change_h_box.addWidget(
            self.filter_last_percent_change_input)
        filter_last_percent_change_h_box.addWidget(
            self.filter_last_percent_change_input2)
        self.filter_last_percent_change_group.setLayout(
            filter_last_percent_change_h_box)
        self.filter_last_percent_change_choose.activated[str].connect(
            self.filter_last_percent_change_condition_changed)

        filter_condition_gird_box.addWidget(self.filter_pe_group, 0, 0)
        filter_condition_gird_box.addWidget(self.filter_roe_group, 0, 1)
        filter_condition_gird_box.addWidget(self.filter_cmv_group, 0, 2)
        filter_condition_gird_box.addWidget(self.filter_ito_group, 0, 3)
        filter_condition_gird_box.addWidget(self.filter_artr_group, 1, 0)
        filter_condition_gird_box.addWidget(self.filter_dar_group, 1, 1)
        filter_condition_gird_box.addWidget(self.filter_ltv_group, 1, 2)
        filter_condition_gird_box.addWidget(self.filter_op_group, 1, 3)
        filter_condition_gird_box.addWidget(self.filter_last_turn_over_group,
                                            2, 0)
        filter_condition_gird_box.addWidget(
            self.filter_last_percent_change_group, 2, 1)

        self.tab_filter.setLayout(filter_condition_gird_box)

        sort_condition = ['从小到大', '从大到小']
        sort_condition_gird_box = QGridLayout()
        self.sort_pe_group = QGroupBox()
        self.sort_pe_check = QCheckBox('PE')
        self.sort_pe_choose = QComboBox()
        self.sort_pe_choose.addItems(sort_condition)
        self.sort_pe_input = QLineEdit()
        self.sort_pe_input.setPlaceholderText('1')
        self.sort_pe_input.setValidator(int_validator)
        sort_pe_h_box = QHBoxLayout()
        sort_pe_h_box.addWidget(self.sort_pe_check)
        sort_pe_h_box.addWidget(self.sort_pe_choose)
        sort_pe_h_box.addWidget(self.sort_pe_input)
        self.sort_pe_group.setLayout(sort_pe_h_box)

        self.sort_roe_group = QGroupBox()
        self.sort_roe_check = QCheckBox('ROE')
        self.sort_roe_choose = QComboBox()
        self.sort_roe_choose.addItems(sort_condition)
        self.sort_roe_input = QLineEdit()
        self.sort_roe_input.setPlaceholderText('1')
        self.sort_roe_input.setValidator(int_validator)
        sort_roe_h_box = QHBoxLayout()
        sort_roe_h_box.addWidget(self.sort_roe_check)
        sort_roe_h_box.addWidget(self.sort_roe_choose)
        sort_roe_h_box.addWidget(self.sort_roe_input)
        self.sort_roe_group.setLayout(sort_roe_h_box)

        self.sort_cmv_group = QGroupBox()
        self.sort_cmv_check = QCheckBox('流通市值')
        self.sort_cmv_choose = QComboBox()
        self.sort_cmv_choose.addItems(sort_condition)
        self.sort_cmv_input = QLineEdit()
        self.sort_cmv_input.setPlaceholderText('1')
        self.sort_cmv_input.setValidator(int_validator)
        sort_cmv_h_box = QHBoxLayout()
        sort_cmv_h_box.addWidget(self.sort_cmv_check)
        sort_cmv_h_box.addWidget(self.sort_cmv_choose)
        sort_cmv_h_box.addWidget(self.sort_cmv_input)
        self.sort_cmv_group.setLayout(sort_cmv_h_box)

        self.sort_ito_group = QGroupBox()
        self.sort_ito_check = QCheckBox('存货率')
        self.sort_ito_choose = QComboBox()
        self.sort_ito_choose.addItems(sort_condition)
        self.sort_ito_input = QLineEdit()
        self.sort_ito_input.setPlaceholderText('1')
        self.sort_ito_input.setValidator(int_validator)
        sort_ito_h_box = QHBoxLayout()
        sort_ito_h_box.addWidget(self.sort_ito_check)
        sort_ito_h_box.addWidget(self.sort_ito_choose)
        sort_ito_h_box.addWidget(self.sort_ito_input)
        self.sort_ito_group.setLayout(sort_ito_h_box)

        self.sort_artr_group = QGroupBox()
        self.sort_artr_check = QCheckBox('应收帐款率')
        self.sort_artr_choose = QComboBox()
        self.sort_artr_choose.addItems(sort_condition)
        self.sort_artr_input = QLineEdit()
        self.sort_artr_input.setPlaceholderText('1')
        self.sort_artr_input.setValidator(int_validator)
        sort_artr_h_box = QHBoxLayout()
        sort_artr_h_box.addWidget(self.sort_artr_check)
        sort_artr_h_box.addWidget(self.sort_artr_choose)
        sort_artr_h_box.addWidget(self.sort_artr_input)
        self.sort_artr_group.setLayout(sort_artr_h_box)

        self.sort_dar_group = QGroupBox()
        self.sort_dar_check = QCheckBox('资产负债率')
        self.sort_dar_choose = QComboBox()
        self.sort_dar_choose.addItems(sort_condition)
        self.sort_dar_input = QLineEdit()
        self.sort_dar_input.setPlaceholderText('1')
        self.sort_dar_input.setValidator(int_validator)
        sort_dar_h_box = QHBoxLayout()
        sort_dar_h_box.addWidget(self.sort_dar_check)
        sort_dar_h_box.addWidget(self.sort_dar_choose)
        sort_dar_h_box.addWidget(self.sort_dar_input)
        self.sort_dar_group.setLayout(sort_dar_h_box)

        self.sort_ltv_group = QGroupBox()
        self.sort_ltv_check = QCheckBox('质押率')
        self.sort_ltv_check.setDisabled(True)
        self.sort_ltv_choose = QComboBox()
        self.sort_ltv_choose.addItems(sort_condition)
        self.sort_ltv_input = QLineEdit()
        self.sort_ltv_input.setPlaceholderText('1')
        self.sort_ltv_input.setValidator(int_validator)
        sort_ltv_h_box = QHBoxLayout()
        sort_ltv_h_box.addWidget(self.sort_ltv_check)
        sort_ltv_h_box.addWidget(self.sort_ltv_choose)
        sort_ltv_h_box.addWidget(self.sort_ltv_input)
        self.sort_ltv_group.setLayout(sort_ltv_h_box)

        self.sort_op_group = QGroupBox()
        self.sort_op_check = QCheckBox('开盘价')
        self.sort_op_choose = QComboBox()
        self.sort_op_choose.addItems(sort_condition)
        self.sort_op_input = QLineEdit()
        self.sort_op_input.setPlaceholderText('1')
        self.sort_op_input.setValidator(int_validator)
        sort_op_h_box = QHBoxLayout()
        sort_op_h_box.addWidget(self.sort_op_check)
        sort_op_h_box.addWidget(self.sort_op_choose)
        sort_op_h_box.addWidget(self.sort_op_input)
        self.sort_op_group.setLayout(sort_op_h_box)

        self.sort_last_turn_over_group = QGroupBox()
        self.sort_last_turn_over_check = QCheckBox('昨换手率')
        self.sort_last_turn_over_choose = QComboBox()
        self.sort_last_turn_over_choose.addItems(sort_condition)
        self.sort_last_turn_over_input = QLineEdit()
        self.sort_last_turn_over_input.setPlaceholderText('1')
        self.sort_last_turn_over_input.setValidator(int_validator)
        sort_last_turn_over_h_box = QHBoxLayout()
        sort_last_turn_over_h_box.addWidget(self.sort_last_turn_over_check)
        sort_last_turn_over_h_box.addWidget(self.sort_last_turn_over_choose)
        sort_last_turn_over_h_box.addWidget(self.sort_last_turn_over_input)
        self.sort_last_turn_over_group.setLayout(sort_last_turn_over_h_box)

        self.sort_last_percent_change_group = QGroupBox()
        self.sort_last_percent_change_check = QCheckBox('昨涨跌幅')
        self.sort_last_percent_change_choose = QComboBox()
        self.sort_last_percent_change_choose.addItems(sort_condition)
        self.sort_last_percent_change_input = QLineEdit()
        self.sort_last_percent_change_input.setPlaceholderText('1')
        self.sort_last_percent_change_input.setValidator(int_validator)
        sort_last_percent_change_h_box = QHBoxLayout()
        sort_last_percent_change_h_box.addWidget(
            self.sort_last_percent_change_check)
        sort_last_percent_change_h_box.addWidget(
            self.sort_last_percent_change_choose)
        sort_last_percent_change_h_box.addWidget(
            self.sort_last_percent_change_input)
        self.sort_last_percent_change_group.setLayout(
            sort_last_percent_change_h_box)

        sort_condition_gird_box.addWidget(self.sort_pe_group, 0, 0)
        sort_condition_gird_box.addWidget(self.sort_roe_group, 0, 1)
        sort_condition_gird_box.addWidget(self.sort_cmv_group, 0, 2)
        sort_condition_gird_box.addWidget(self.sort_ito_group, 0, 3)
        sort_condition_gird_box.addWidget(self.sort_artr_group, 1, 0)
        sort_condition_gird_box.addWidget(self.sort_dar_group, 1, 1)
        sort_condition_gird_box.addWidget(self.sort_ltv_group, 1, 2)
        sort_condition_gird_box.addWidget(self.sort_op_group, 1, 3)
        sort_condition_gird_box.addWidget(self.sort_last_turn_over_group, 2, 0)
        sort_condition_gird_box.addWidget(self.sort_last_percent_change_group,
                                          2, 1)

        self.tab_sort.setLayout(sort_condition_gird_box)

        backtest_condition_gird_box = QGridLayout()
        self.per_stock_position_group = QGroupBox()
        self.per_stock_position_check = QCheckBox('个股仓位')
        self.per_stock_position_input = QLineEdit()
        self.per_stock_position_input.setPlaceholderText('点')
        self.per_stock_position_input.setValidator(int_validator)
        per_stock_position_h_box = QHBoxLayout()
        per_stock_position_h_box.addWidget(self.per_stock_position_check)
        per_stock_position_h_box.addWidget(self.per_stock_position_input)
        self.per_stock_position_group.setLayout(per_stock_position_h_box)

        self.adjust_period_group = QGroupBox()
        self.adjust_period_check = QCheckBox('调仓周期')
        self.adjust_period_input = QLineEdit()
        self.adjust_period_input.setPlaceholderText('天')
        self.adjust_period_input.setValidator(int_validator)
        adjust_period_h_box = QHBoxLayout()
        adjust_period_h_box.addWidget(self.adjust_period_check)
        adjust_period_h_box.addWidget(self.adjust_period_input)
        self.adjust_period_group.setLayout(adjust_period_h_box)

        self.adjust_price_group = QGroupBox()
        self.adjust_price_check = QCheckBox('调仓价格')
        self.adjust_price_choose = QComboBox()
        self.adjust_price_choose.addItems(['开盘价', '最高价', '最低价', '收盘价'])
        adjust_price_h_box = QHBoxLayout()
        adjust_price_h_box.addWidget(self.adjust_price_check)
        adjust_price_h_box.addWidget(self.adjust_price_choose)
        self.adjust_price_group.setLayout(adjust_price_h_box)

        self.score_group = QGroupBox()
        self.score_check = QCheckBox('卖出排名')
        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText('大于就卖')
        self.score_input.setValidator(int_validator)
        score_h_box = QHBoxLayout()
        score_h_box.addWidget(self.score_check)
        score_h_box.addWidget(self.score_input)
        self.score_group.setLayout(score_h_box)

        self.max_hold_days_group = QGroupBox()
        self.max_hold_days_check = QCheckBox('最大持股天数')
        self.max_hold_days_input = QLineEdit()
        self.max_hold_days_input.setPlaceholderText('超过就卖')
        self.max_hold_days_input.setValidator(int_validator)
        max_hold_days_h_box = QHBoxLayout()
        max_hold_days_h_box.addWidget(self.max_hold_days_check)
        max_hold_days_h_box.addWidget(self.max_hold_days_input)
        self.max_hold_days_group.setLayout(max_hold_days_h_box)

        self.take_profit_group = QGroupBox()
        self.take_profit_check = QCheckBox('止盈点数')
        self.take_profit_input = QLineEdit()
        self.take_profit_input.setValidator(int_validator)
        take_profit_h_box = QHBoxLayout()
        take_profit_h_box.addWidget(self.take_profit_check)
        take_profit_h_box.addWidget(self.take_profit_input)
        self.take_profit_group.setLayout(take_profit_h_box)

        self.stop_loss_group = QGroupBox()
        self.stop_loss_check = QCheckBox('止损点数')
        self.stop_loss_input = QLineEdit()
        self.stop_loss_input.setValidator(int_validator)
        stop_loss_h_box = QHBoxLayout()
        stop_loss_h_box.addWidget(self.stop_loss_check)
        stop_loss_h_box.addWidget(self.stop_loss_input)
        self.stop_loss_group.setLayout(stop_loss_h_box)

        self.max_drawdown_group = QGroupBox()
        self.max_drawdown_check = QCheckBox('最大回撤点数')
        self.max_drawdown_input = QLineEdit()
        self.max_drawdown_input.setPlaceholderText('达到就卖')
        self.max_drawdown_input.setValidator(int_validator)
        max_drawdown_h_box = QHBoxLayout()
        max_drawdown_h_box.addWidget(self.max_drawdown_check)
        max_drawdown_h_box.addWidget(self.max_drawdown_input)
        self.max_drawdown_group.setLayout(max_drawdown_h_box)

        self.limit_up_no_sell_group = QGroupBox()
        self.limit_up_no_sell_check = QCheckBox('涨停不卖')
        limit_up_no_sell_h_box = QHBoxLayout()
        limit_up_no_sell_h_box.addWidget(self.limit_up_no_sell_check)
        self.limit_up_no_sell_group.setLayout(limit_up_no_sell_h_box)

        self.min_hold_days_group = QGroupBox()
        self.min_hold_days_check = QCheckBox('最小持股天数')
        self.min_hold_days_input = QLineEdit()
        self.min_hold_days_input.setPlaceholderText('不足不卖')
        self.min_hold_days_input.setValidator(int_validator)
        min_hold_days_h_box = QHBoxLayout()
        min_hold_days_h_box.addWidget(self.min_hold_days_check)
        min_hold_days_h_box.addWidget(self.min_hold_days_input)
        self.min_hold_days_group.setLayout(min_hold_days_h_box)

        backtest_condition_gird_box.addWidget(self.per_stock_position_group, 0,
                                              0)
        backtest_condition_gird_box.addWidget(self.adjust_period_group, 0, 1)
        backtest_condition_gird_box.addWidget(self.adjust_price_group, 0, 2)
        backtest_condition_gird_box.addWidget(self.score_group, 0, 3)
        backtest_condition_gird_box.addWidget(self.max_hold_days_group, 0, 4)
        backtest_condition_gird_box.addWidget(self.take_profit_group, 1, 0)
        backtest_condition_gird_box.addWidget(self.stop_loss_group, 1, 1)
        backtest_condition_gird_box.addWidget(self.max_drawdown_group, 1, 2)
        backtest_condition_gird_box.addWidget(self.limit_up_no_sell_group, 1, 3)
        backtest_condition_gird_box.addWidget(self.min_hold_days_group,
                                              1, 4)

        self.tab_backtest.setLayout(backtest_condition_gird_box)

        upper_h_box = QHBoxLayout()
        op_v_box = QVBoxLayout()
        self.btn_search = QPushButton('筛选')
        self.btn_backtest = QPushButton('回测')
        self.btn_reset = QPushButton('重置')
        self.btn_save = QPushButton('保存')
        self.btn_saveas = QPushButton('另存为')
        op_v_box.addWidget(self.btn_search)
        op_v_box.addWidget(self.btn_backtest)
        op_v_box.addStretch()
        op_v_box.addWidget(self.btn_reset)
        op_v_box.addStretch()
        op_v_box.addWidget(self.btn_save)
        op_v_box.addWidget(self.btn_saveas)
        upper_h_box.addWidget(self.tabs)
        upper_h_box.addLayout(op_v_box)

        result_h_box = QHBoxLayout()

        self.strategy_table = QTableWidget()
        self.strategy_table.setColumnCount(1)
        self.strategy_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.strategy_table.horizontalHeader().setVisible(False)
        self.strategy_table.verticalHeader().setVisible(False)
        self.strategy_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.strategy_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.strategy_table.setSortingEnabled(True)
        self.strategy_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.strategy_table.setMinimumWidth(100)
        self.strategy_table.setMaximumWidth(150)

        self.table = QTableWidget()
        headers = ['代码', '股票', '得分', 'PE', 'ROE', '流通市值', '存货率',
                   '应收帐款率', '资产负债率', '质押率', '开盘价', '昨换手率',
                   '昨涨跌幅']
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
        self.table.setMinimumWidth(500)

        result_h_box.addWidget(self.strategy_table)
        result_h_box.addWidget(self.table)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addLayout(upper_h_box)
        main_v_box.addLayout(result_h_box)

        self.setLayout(main_v_box)

        self.btn_search.clicked.connect(self.on_search)
        self.btn_backtest.clicked.connect(self.on_backtest)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_saveas.clicked.connect(self.on_save_as)
        self.table.customContextMenuRequested.connect(self.open_ops_menu)
        self.strategy_table.customContextMenuRequested.connect(
            self.open_strategy_ops_menu)
        self.strategy_table.itemSelectionChanged.connect(
            self.on_strategy_row_changed)

        self.load_strategies_list()

    def load_strategies_list(self):
        for file in Path(factor_strategies_config_path).rglob('*.json'):
            row = self.strategy_table.rowCount()
            self.strategy_table.insertRow(row)
            self.strategy_table.setItem(row, 0, QTableWidgetItem(file.stem))

    def filter_pe_condition_changed(self, text):
        condition_changed(text, self.filter_pe_input2)

    def filter_roe_condition_changed(self, text):
        condition_changed(text, self.filter_roe_input2)

    def filter_cmv_condition_changed(self, text):
        condition_changed(text, self.filter_cmv_input2)

    def filter_ito_condition_changed(self, text):
        condition_changed(text, self.filter_ito_input2)

    def filter_artr_condition_changed(self, text):
        condition_changed(text, self.filter_artr_input2)

    def filter_dar_condition_changed(self, text):
        condition_changed(text, self.filter_dar_input2)

    def filter_ltv_condition_changed(self, text):
        condition_changed(text, self.filter_ltv_input2)

    def filter_op_condition_changed(self, text):
        condition_changed(text, self.filter_op_input2)

    def filter_last_turn_over_condition_changed(self, text):
        condition_changed(text, self.filter_last_turn_over_input2)

    def filter_last_percent_change_condition_changed(self, text):
        condition_changed(text, self.filter_last_percent_change_input2)

    def disable_all(self):
        self.btn_search.setDisabled(True)
        self.btn_backtest.setDisabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_save.setDisabled(True)
        self.btn_saveas.setDisabled(True)

    def enable_all(self):
        self.btn_search.setEnabled(True)
        self.btn_backtest.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.btn_saveas.setEnabled(True)

    def set_progress_bar(self, value, code, name, score, pe, roe, ito, artr,
                         dar, ltv, op, turn, pc):
        self.progress_bar.setValue(value)
        if value == 100:
            self.enable_all()
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(score)))
            self.table.setItem(row, 3, QTableWidgetItem(str(pe)))
            self.table.setItem(row, 4, QTableWidgetItem(str(roe)))
            self.table.setItem(row, 5, QTableWidgetItem(str(ito)))
            self.table.setItem(row, 6, QTableWidgetItem(str(artr)))
            self.table.setItem(row, 7, QTableWidgetItem(str(dar)))
            self.table.setItem(row, 8, QTableWidgetItem(str(ltv)))
            self.table.setItem(row, 9, QTableWidgetItem(str(op)))
            self.table.setItem(row, 10, QTableWidgetItem(str(turn)))
            self.table.setItem(row, 11, QTableWidgetItem(str(pc)))

    def on_search(self):
        strategy = self.get_current_strategy()
        self.disable_all()

        rows = self.table.rowCount()
        for i in reversed(range(rows)):
            self.table.removeRow(i)

        self.factor_thread = FactorChoose(strategy)
        self.factor_thread.progress_signal.connect(
            self.set_progress_bar)
        self.factor_thread.start()

    def on_backtest(self):
        pass

    def on_reset(self):
        self.filter_pe_check.setChecked(False)
        self.filter_pe_choose.setCurrentIndex(0)
        self.filter_pe_input.clear()
        self.filter_pe_input2.clear()
        self.filter_pe_input2.setVisible(False)
        self.filter_roe_check.setChecked(False)
        self.filter_roe_choose.setCurrentIndex(0)
        self.filter_roe_input.clear()
        self.filter_roe_input2.clear()
        self.filter_roe_input2.setVisible(False)
        self.filter_cmv_check.setChecked(False)
        self.filter_cmv_choose.setCurrentIndex(0)
        self.filter_cmv_input.clear()
        self.filter_cmv_input2.clear()
        self.filter_cmv_input2.setVisible(False)
        self.filter_ito_check.setChecked(False)
        self.filter_ito_choose.setCurrentIndex(0)
        self.filter_ito_input.clear()
        self.filter_ito_input2.clear()
        self.filter_ito_input2.setVisible(False)
        self.filter_artr_check.setChecked(False)
        self.filter_artr_choose.setCurrentIndex(0)
        self.filter_artr_input.clear()
        self.filter_artr_input2.clear()
        self.filter_artr_input2.setVisible(False)
        self.filter_dar_check.setChecked(False)
        self.filter_dar_choose.setCurrentIndex(0)
        self.filter_dar_input.clear()
        self.filter_dar_input2.clear()
        self.filter_dar_input2.setVisible(False)
        self.filter_ltv_check.setChecked(False)
        self.filter_ltv_choose.setCurrentIndex(0)
        self.filter_ltv_input.clear()
        self.filter_ltv_input2.clear()
        self.filter_ltv_input2.setVisible(False)
        self.filter_op_check.setChecked(False)
        self.filter_op_choose.setCurrentIndex(0)
        self.filter_op_input.clear()
        self.filter_op_input2.clear()
        self.filter_op_input2.setVisible(False)
        self.filter_last_turn_over_check.setChecked(False)
        self.filter_last_turn_over_choose.setCurrentIndex(0)
        self.filter_last_turn_over_input.clear()
        self.filter_last_turn_over_input2.clear()
        self.filter_last_turn_over_input2.setVisible(False)
        self.filter_last_percent_change_check.setChecked(False)
        self.filter_last_percent_change_choose.setCurrentIndex(0)
        self.filter_last_percent_change_input.clear()
        self.filter_last_percent_change_input2.clear()
        self.filter_last_percent_change_input2.setVisible(False)

        self.sort_pe_check.setChecked(False)
        self.sort_pe_choose.setCurrentIndex(0)
        self.sort_pe_input.clear()
        self.sort_roe_check.setChecked(False)
        self.sort_roe_choose.setCurrentIndex(0)
        self.sort_roe_input.clear()
        self.sort_cmv_check.setChecked(False)
        self.sort_cmv_choose.setCurrentIndex(0)
        self.sort_cmv_input.clear()
        self.sort_ito_check.setChecked(False)
        self.sort_ito_choose.setCurrentIndex(0)
        self.sort_ito_input.clear()
        self.sort_artr_check.setChecked(False)
        self.sort_artr_choose.setCurrentIndex(0)
        self.sort_artr_input.clear()
        self.sort_dar_check.setChecked(False)
        self.sort_dar_choose.setCurrentIndex(0)
        self.sort_dar_input.clear()
        self.sort_ltv_check.setChecked(False)
        self.sort_ltv_choose.setCurrentIndex(0)
        self.sort_ltv_input.clear()
        self.sort_op_check.setChecked(False)
        self.sort_op_choose.setCurrentIndex(0)
        self.sort_op_input.clear()
        self.sort_last_turn_over_check.setChecked(False)
        self.sort_last_turn_over_choose.setCurrentIndex(0)
        self.sort_last_turn_over_input.clear()
        self.sort_last_percent_change_check.setChecked(False)
        self.sort_last_percent_change_choose.setCurrentIndex(0)
        self.sort_last_percent_change_input.clear()

        self.per_stock_position_check.setChecked(False)
        self.per_stock_position_input.clear()
        self.adjust_period_check.setChecked(False)
        self.adjust_period_input.clear()
        self.adjust_price_check.setChecked(False)
        self.adjust_price_choose.setCurrentIndex(0)
        self.score_check.setChecked(False)
        self.score_input.clear()
        self.max_hold_days_check.setChecked(False)
        self.max_hold_days_input.clear()
        self.take_profit_check.setChecked(False)
        self.take_profit_input.clear()
        self.stop_loss_check.setChecked(False)
        self.stop_loss_input.clear()
        self.max_drawdown_check.setChecked(False)
        self.max_drawdown_input.clear()
        self.limit_up_no_sell_check.setChecked(False)
        self.min_hold_days_check.setChecked(False)
        self.min_hold_days_input.clear()

        self.on_strategy_row_changed()

    def get_current_strategy(self):
        strategy = {}
        _filter = []
        sort = []
        backtest = {}

        item = {}
        if self.filter_pe_check.isChecked():
            item['key'] = 'PE'
            item['condition'] = self.filter_pe_choose.currentText()
            v = self.filter_pe_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', 'PE为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_pe_input2.isVisible():
                v2 = self.filter_pe_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', 'PE为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_roe_check.isChecked():
            item['key'] = 'ROE'
            item['condition'] = self.filter_roe_choose.currentText()
            v = self.filter_roe_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', 'ROE为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_roe_input2.isVisible():
                v2 = self.filter_roe_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', 'ROE为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_cmv_check.isChecked():
            item['key'] = '流通市值'
            item['condition'] = self.filter_cmv_choose.currentText()
            v = self.filter_cmv_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '流通市值为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_cmv_input2.isVisible():
                v2 = self.filter_cmv_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '流通市值为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_ito_check.isChecked():
            item['key'] = '存货率'
            item['condition'] = self.filter_ito_choose.currentText()
            v = self.filter_ito_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '存货率为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_ito_input2.isVisible():
                v2 = self.filter_ito_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '存货率为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_artr_check.isChecked():
            item['key'] = '应收帐款率'
            item['condition'] = self.filter_artr_choose.currentText()
            v = self.filter_artr_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '应收帐款率为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_artr_input2.isVisible():
                v2 = self.filter_artr_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '应收帐款率为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_dar_check.isChecked():
            item['key'] = '资产负债率'
            item['condition'] = self.filter_dar_choose.currentText()
            v = self.filter_dar_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '资产负债率为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_dar_input2.isVisible():
                v2 = self.filter_dar_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '资产负债率为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_ltv_check.isChecked():
            item['key'] = '质押率'
            item['condition'] = self.filter_ltv_choose.currentText()
            v = self.filter_ltv_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '质押率为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_ltv_input2.isVisible():
                v2 = self.filter_ltv_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '质押率为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_op_check.isChecked():
            item['key'] = '开盘价'
            item['condition'] = self.filter_op_choose.currentText()
            v = self.filter_op_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '开盘价为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_op_input2.isVisible():
                v2 = self.filter_op_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '开盘价为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_last_turn_over_check.isChecked():
            item['key'] = '昨换手率'
            item['condition'] = self.filter_last_turn_over_choose.currentText()
            v = self.filter_last_turn_over_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '昨换手率为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_last_turn_over_input2.isVisible():
                v2 = self.filter_last_turn_over_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '昨换手率为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        item = {}
        if self.filter_last_percent_change_check.isChecked():
            item['key'] = '昨涨跌幅'
            item['condition'] = \
                self.filter_last_percent_change_choose.currentText()
            v = self.filter_last_percent_change_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '昨涨跌幅为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            item['value'] = v
            if self.filter_last_percent_change_input2.isVisible():
                v2 = self.filter_last_percent_change_input2.text()
                if len(v2) == 0:
                    QMessageBox.warning(self, '警告', '昨涨跌幅为空',
                                        QMessageBox.Ok, QMessageBox.Ok)
                item['value2'] = v2
            _filter.append(item)
        strategy['filter'] = _filter

        item = {}
        if self.sort_pe_check.isChecked():
            item['key'] = 'PE'
            item['condition'] = self.sort_pe_choose.currentText()
            v = self.sort_pe_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_roe_check.isChecked():
            item['key'] = 'ROE'
            item['condition'] = self.sort_roe_choose.currentText()
            v = self.sort_roe_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_cmv_check.isChecked():
            item['key'] = '流通市值'
            item['condition'] = self.sort_cmv_choose.currentText()
            v = self.sort_cmv_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_ito_check.isChecked():
            item['key'] = '存货率'
            item['condition'] = self.sort_ito_choose.currentText()
            v = self.sort_ito_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_artr_check.isChecked():
            item['key'] = '应收帐款率'
            item['condition'] = self.sort_artr_choose.currentText()
            v = self.sort_artr_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_dar_check.isChecked():
            item['key'] = '资产负债率'
            item['condition'] = self.sort_dar_choose.currentText()
            v = self.sort_dar_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_ltv_check.isChecked():
            item['key'] = '质押率'
            item['condition'] = self.sort_ltv_choose.currentText()
            v = self.sort_ltv_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_op_check.isChecked():
            item['key'] = '开盘价'
            item['condition'] = self.sort_op_choose.currentText()
            v = self.sort_op_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_last_turn_over_check.isChecked():
            item['key'] = '昨换手率'
            item['condition'] = self.sort_last_turn_over_choose.currentText()
            v = self.sort_last_turn_over_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        item = {}
        if self.sort_last_percent_change_check.isChecked():
            item['key'] = '昨涨跌幅'
            item['condition'] = \
                self.sort_last_percent_change_choose.currentText()
            v = self.sort_last_percent_change_input.text()
            if len(v) == 0:
                item['value'] = '1'
            else:
                item['value'] = v
            sort.append(item)
        strategy['sort'] = sort

        if self.per_stock_position_check.isChecked():
            v = self.per_stock_position_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '个股仓位为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['per_stock_position'] = v
        if self.adjust_period_check.isChecked():
            v = self.adjust_period_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '调仓周期为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['adjust_period'] = v
        if self.adjust_price_check.isChecked():
            v = self.adjust_price_choose.currentText()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '调仓价格为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['adjust_price'] = v
        if self.score_check.isChecked():
            v = self.score_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '卖出排名为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['score'] = v
        if self.max_hold_days_check.isChecked():
            v = self.max_hold_days_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '最大持股天数为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['max_hold_days'] = v
        if self.take_profit_check.isChecked():
            v = self.take_profit_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '止盈为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['take_profit'] = v
        if self.stop_loss_check.isChecked():
            v = self.stop_loss_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '止损为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['stop_loss'] = v
        if self.max_drawdown_check.isChecked():
            v = self.max_drawdown_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '最大回撤为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['max_drawdown'] = v
        if self.limit_up_no_sell_check.isChecked():
            backtest['limit_up_no_sell'] = True
        else:
            backtest['limit_up_no_sell'] = False
        if self.min_hold_days_check.isChecked():
            v = self.min_hold_days_input.text()
            if len(v) == 0:
                QMessageBox.warning(self, '警告', '最小持股天数为空',
                                    QMessageBox.Ok, QMessageBox.Ok)
            backtest['min_hold_days'] = v
        strategy['backtest'] = backtest
        return strategy

    def on_save(self, strategy_name):
        if not strategy_name:
            row = self.strategy_table.currentRow()
            if row == -1:
                QMessageBox.warning(self, '警告', '请先选择一个策略',
                                    QMessageBox.Ok, QMessageBox.Ok)
                return False
            strategy_name = self.strategy_table.item(row, 0).text()
        strategy_file = Path(factor_strategies_config_path).joinpath(
            strategy_name).with_suffix('.json')

        strategy = self.get_current_strategy()
        strategy_list = []
        for file in Path(factor_strategies_config_path).rglob('*.json'):
            strategy_list.append(file.stem)
        if strategy_name not in strategy_list:
            row = self.strategy_table.rowCount()
            self.strategy_table.insertRow(row)
            self.strategy_table.setItem(row, 0, QTableWidgetItem(strategy_name))

        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=4, ensure_ascii=False)

    def on_save_as(self):
        dlg = FactorSaveAsDialog()
        dlg.show()
        dlg.factor_saveas_signal.connect(self.on_save)
        dlg.exec_()

    def fill_conditions(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            strategy = json.load(f)

            _filter = strategy['filter']
            for item in _filter:
                if item['key'] == 'PE':
                    self.filter_pe_check.setChecked(True)
                    self.filter_pe_choose.setCurrentText(item['condition'])
                    self.filter_pe_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_pe_input2.setVisible(True)
                        self.filter_pe_input2.setText(item['value2'])
                if item['key'] == 'ROE':
                    self.filter_roe_check.setChecked(True)
                    self.filter_roe_choose.setCurrentText(item['condition'])
                    self.filter_roe_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_roe_input2.setVisible(True)
                        self.filter_roe_input2.setText(item['value2'])
                if item['key'] == '流通市值':
                    self.filter_cmv_check.setChecked(True)
                    self.filter_cmv_choose.setCurrentText(item['condition'])
                    self.filter_cmv_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_cmv_input2.setVisible(True)
                        self.filter_cmv_input2.setText(item['value2'])
                if item['key'] == '存货率':
                    self.filter_ito_check.setChecked(True)
                    self.filter_ito_choose.setCurrentText(item['condition'])
                    self.filter_ito_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_ito_input2.setVisible(True)
                        self.filter_ito_input2.setText(item['value2'])
                if item['key'] == '应收帐款率':
                    self.filter_artr_check.setChecked(True)
                    self.filter_artr_choose.setCurrentText(item['condition'])
                    self.filter_artr_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_artr_input2.setVisible(True)
                        self.filter_artr_input2.setText(item['value2'])
                if item['key'] == '资产负债率':
                    self.filter_dar_check.setChecked(True)
                    self.filter_dar_choose.setCurrentText(item['condition'])
                    self.filter_dar_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_dar_input2.setVisible(True)
                        self.filter_dar_input2.setText(item['value2'])
                if item['key'] == '质押率':
                    self.filter_ltv_check.setChecked(True)
                    self.filter_ltv_choose.setCurrentText(item['condition'])
                    self.filter_ltv_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_ltv_input2.setVisible(True)
                        self.filter_ltv_input2.setText(item['value2'])
                if item['key'] == '开盘价':
                    self.filter_op_check.setChecked(True)
                    self.filter_op_choose.setCurrentText(item['condition'])
                    self.filter_op_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_op_input2.setVisible(True)
                        self.filter_op_input2.setText(item['value2'])
                if item['key'] == '昨换手率':
                    self.filter_last_turn_over_check.setChecked(True)
                    self.filter_last_turn_over_choose.setCurrentText(
                        item['condition'])
                    self.filter_last_turn_over_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_last_turn_over_input2.setVisible(True)
                        self.filter_last_turn_over_input2.setText(
                            item['value2'])
                if item['key'] == '昨涨跌幅':
                    self.filter_last_percent_change_check.setChecked(True)
                    self.filter_last_percent_change_choose.setCurrentText(
                        item['condition'])
                    self.filter_last_percent_change_input.setText(item['value'])
                    if 'value2' in item:
                        self.filter_last_percent_change_input2.setVisible(True)
                        self.filter_last_percent_change_input2.setText(
                            item['value2'])

            sort = strategy['sort']
            for item in sort:
                if item['key'] == 'PE':
                    self.sort_pe_check.setChecked(True)
                    self.sort_pe_choose.setCurrentText(item['condition'])
                    self.sort_pe_input.setText(item['value'])
                if item['key'] == 'ROE':
                    self.sort_roe_check.setChecked(True)
                    self.sort_roe_choose.setCurrentText(item['condition'])
                    self.sort_roe_input.setText(item['value'])
                if item['key'] == '流通市值':
                    self.sort_cmv_check.setChecked(True)
                    self.sort_cmv_choose.setCurrentText(item['condition'])
                    self.sort_cmv_input.setText(item['value'])
                if item['key'] == '存货率':
                    self.sort_ito_check.setChecked(True)
                    self.sort_ito_choose.setCurrentText(item['condition'])
                    self.sort_ito_input.setText(item['value'])
                if item['key'] == '应收帐款率':
                    self.sort_artr_check.setChecked(True)
                    self.sort_artr_choose.setCurrentText(item['condition'])
                    self.sort_artr_input.setText(item['value'])
                if item['key'] == '资产负债率':
                    self.sort_dar_check.setChecked(True)
                    self.sort_dar_choose.setCurrentText(item['condition'])
                    self.sort_dar_input.setText(item['value'])
                if item['key'] == '质押率':
                    self.sort_ltv_check.setChecked(True)
                    self.sort_ltv_choose.setCurrentText(item['condition'])
                    self.sort_ltv_input.setText(item['value'])
                if item['key'] == '开盘价':
                    self.sort_op_check.setChecked(True)
                    self.sort_op_choose.setCurrentText(item['condition'])
                    self.sort_op_input.setText(item['value'])
                if item['key'] == '昨换手率':
                    self.sort_last_turn_over_check.setChecked(True)
                    self.sort_last_turn_over_choose.setCurrentText(
                        item['condition'])
                    self.sort_last_turn_over_input.setText(item['value'])
                if item['key'] == '昨涨跌幅':
                    self.sort_last_percent_change_check.setChecked(True)
                    self.sort_last_percent_change_choose.setCurrentText(
                        item['condition'])
                    self.sort_last_percent_change_input.setText(item['value'])

            backtest = strategy['backtest']
            if 'per_stock_position' in backtest:
                self.per_stock_position_check.setChecked(True)
                self.per_stock_position_input.setText(
                    backtest['per_stock_position'])
            if 'adjust_period' in backtest:
                self.adjust_period_check.setChecked(True)
                self.adjust_period_input.setText(backtest['adjust_period'])
            if 'adjust_price' in backtest:
                self.adjust_price_check.setChecked(True)
                self.adjust_price_choose.setCurrentText(
                    backtest['adjust_price'])
            if 'score' in backtest:
                self.score_check.setChecked(True)
                self.score_input.setText(backtest['score'])
            if 'max_hold_days' in backtest:
                self.max_hold_days_check.setChecked(True)
                self.max_hold_days_input.setText(backtest['max_hold_days'])
            if 'take_profit' in backtest:
                self.take_profit_check.setChecked(True)
                self.take_profit_input.setText(backtest['take_profit'])
            if 'stop_loss' in backtest:
                self.stop_loss_check.setChecked(True)
                self.stop_loss_input.setText(backtest['stop_loss'])
            if 'max_drawdown' in backtest:
                self.max_drawdown_check.setChecked(True)
                self.max_drawdown_input.setText(backtest['max_drawdown'])
            if 'limit_up_no_sell' in backtest:
                if backtest['limit_up_no_sell']:
                    self.limit_up_no_sell_check.setChecked(True)
                else:
                    self.limit_up_no_sell_check.setChecked(False)
            if 'min_hold_days' in backtest:
                self.min_hold_days_check.setChecked(True)
                self.min_hold_days_check.setText(backtest['min_hold_days'])

    def on_strategy_row_changed(self):
        row = self.strategy_table.currentRow()
        if row == -1:
            return
        strategy_name = self.strategy_table.item(row, 0).text()
        file = Path(factor_strategies_config_path).joinpath(
            strategy_name).with_suffix('.json')
        self.fill_conditions(file)

    def on_remove_pool(self):
        if not factor_pool_config_path.exists():
            self.factor_pool = []
        else:
            with open(factor_pool_config_path, 'r', encoding='utf-8') as f:
                self.factor_pool = json.load(f)

        rows = self.table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                code = self.table.item(row.row(), 0).text()
                for stock in self.factor_pool:
                    if stock['code'] == code:
                        self.factor_pool.remove(stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.table.removeRow(row_idx)

    def open_ops_menu(self, position):
        pop_menu = QMenu()
        remove_action = QAction('删除', self)
        pop_menu.addAction(remove_action)

        remove_action.triggered.connect(self.on_remove_pool)
        pop_menu.exec_(self.table.mapToGlobal(position))

    def on_remove_strategy(self):
        row = self.strategy_table.currentRow()
        if row == -1:
            return
        strategy_name = self.strategy_table.item(row, 0).text()
        file = Path(factor_strategies_config_path).joinpath(
            strategy_name).with_suffix('.json')
        file.unlink()
        self.strategy_table.removeRow(row)

    def open_strategy_ops_menu(self, position):
        pop_menu = QMenu()
        remove_action = QAction('删除', self)
        pop_menu.addAction(remove_action)

        remove_action.triggered.connect(self.on_remove_strategy)
        pop_menu.exec_(self.strategy_table.mapToGlobal(position))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Factor()
    main.show()
    sys.exit(app.exec_())
