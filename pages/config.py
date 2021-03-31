import baostock as bs
import json

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from apis.code_index import need_update, reset_last_updated_date, \
    fetch_last_trading_day, reset_stock_index, save_last_updated_date, \
    fetch_all_code, store_all_code
from apis.finance import FetchFinancialData, reset_finance_data
from apis.k_charts import FetchDayK, get_code_list, reset_k_line_data
from apis.statements import reset_statements_data
from conf.conf import FIRST_DAY_YEAR, FIRST_DAY_MONTH, FIRST_DAY_DAY, \
    backtest_config_path
from pages.about import About


class Config(QWidget):
    def __init__(self, parent=None):
        super(Config, self).__init__(parent)
        self.setWindowTitle('设置')

        self.fdk = None
        self.ffd = None
        self.index_date = None
        self.day_e_date = None
        self.financial_date = None
        self.code_list = None

        self.progress_bar = QProgressBar()

        self.up_group_box = QGroupBox('数据更新')
        up_h_box = QHBoxLayout()
        self.btn_up_stock_index = QPushButton('更新股票索引')
        self.btn_up_day_k = QPushButton('更新K线数据')
        self.btn_up_financial_data = QPushButton('更新财务数据')
        self.btn_reset = QPushButton('删除所有数据')
        up_h_box.addWidget(self.btn_up_stock_index)
        up_h_box.addWidget(self.btn_up_day_k)
        up_h_box.addWidget(self.btn_up_financial_data)
        up_h_box.addStretch()
        up_h_box.addWidget(self.btn_reset)
        self.up_group_box.setLayout(up_h_box)

        if not backtest_config_path.exists():
            backtest_config = {
                'start_date': '2006-01-01',
                'init_money': '10',
                'fee': '2.5',
                'pass_fee': '0.2',
                'tax': '1'
            }
        else:
            with open(backtest_config_path, 'r', encoding='utf-8') as f:
                backtest_config = json.load(f)

        self.op_group_box = QGroupBox('回测设置')
        cond_h_box = QHBoxLayout()
        self.start_date_label = QLabel('起始日期')
        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setMinimumDate(QDate(FIRST_DAY_YEAR, FIRST_DAY_MONTH,
                                             FIRST_DAY_DAY))
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-365))
        self.start_date.setDate(QDate.fromString(
            backtest_config['start_date'], 'yyyy-MM-dd'))

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
        self.init_money_input.setText(backtest_config['init_money'])

        self.fee_label = QLabel('手续费(万分)')
        self.fee_input = QLineEdit()
        self.fee_input.setValidator(double_validator)
        self.fee_input.setText(backtest_config['fee'])

        self.pass_fee_label = QLabel('过户费(万分)')
        self.pass_fee_input = QLineEdit()
        self.pass_fee_input.setValidator(double_validator)
        self.pass_fee_input.setText(backtest_config['pass_fee'])

        self.tax_label = QLabel('印花税(千分)')
        self.tax_input = QLineEdit()
        self.tax_input.setValidator(double_validator)
        self.tax_input.setText(backtest_config['tax'])

        self.btn_save_backtest = QPushButton('保存')

        cond_h_box.addWidget(self.start_date_label)
        cond_h_box.addWidget(self.start_date)
        cond_h_box.addStretch()
        cond_h_box.addWidget(self.end_date_label)
        cond_h_box.addWidget(self.end_date)
        cond_h_box.addStretch()
        cond_h_box.addWidget(self.init_money_label)
        cond_h_box.addWidget(self.init_money_input)
        cond_h_box.addStretch()
        cond_h_box.addWidget(self.fee_label)
        cond_h_box.addWidget(self.fee_input)
        cond_h_box.addStretch()
        cond_h_box.addWidget(self.pass_fee_label)
        cond_h_box.addWidget(self.pass_fee_input)
        cond_h_box.addStretch()
        cond_h_box.addWidget(self.tax_label)
        cond_h_box.addWidget(self.tax_input)
        cond_h_box.addStretch()

        op_h_box = QHBoxLayout()
        op_h_box.addStretch()
        op_h_box.addWidget(self.btn_save_backtest)

        op_v_box = QVBoxLayout()
        op_v_box.addLayout(cond_h_box)
        op_v_box.addLayout(op_h_box)
        self.op_group_box.setLayout(op_v_box)

        about_h_box = QHBoxLayout()
        self.btn_about = QPushButton('关于')
        about_h_box.addStretch()
        about_h_box.addWidget(self.btn_about)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addWidget(self.up_group_box)
        main_v_box.addWidget(self.op_group_box)
        main_v_box.addStretch()
        main_v_box.addLayout(about_h_box)

        self.setLayout(main_v_box)

        self.btn_up_stock_index.clicked.connect(self.on_up_stock_index)
        self.btn_up_day_k.clicked.connect(self.on_up_day_k)
        self.btn_up_financial_data.clicked.connect(self.on_up_financial_data)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_about.clicked.connect(self.on_about)
        self.btn_save_backtest.clicked.connect(self.on_save_backtest)

    def on_save_backtest(self):
        backtest_config = {
            'start_date': self.start_date.date().toString('yyyy-MM-dd'),
            'init_money': self.init_money_input.text(),
            'fee': self.fee_input.text(),
            'pass_fee': self.pass_fee_input.text(),
            'tax': self.tax_input.text()
        }
        with open(backtest_config_path, 'w', encoding='utf-8') as f:
            json.dump(backtest_config, f, indent=4, ensure_ascii=False)

    def enable_all(self):
        self.btn_up_stock_index.setEnabled(True)
        self.btn_up_day_k.setEnabled(True)
        self.btn_up_financial_data.setEnabled(True)
        self.btn_reset.setEnabled(True)

    def disable_all(self):
        self.btn_up_stock_index.setDisabled(True)
        self.btn_up_day_k.setDisabled(True)
        self.btn_up_financial_data.setDisabled(True)
        self.btn_reset.setDisabled(True)

    def set_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def show_warning(self, msg):
        QMessageBox.warning(self, '警告', msg,
                            QMessageBox.Ok, QMessageBox.Ok)
        self.enable_all()

    def on_reset(self):
        self.progress_bar.reset()
        reset_stock_index()
        reset_k_line_data()
        reset_finance_data()
        reset_statements_data()
        reset_last_updated_date()

    def complete_financial_progress(self):
        self.set_progress_bar(100)
        self.enable_all()
        save_last_updated_date(self.financial_date, 'f')
        self.code_list = []
        self.progress_bar.reset()

    def _up_financial_data(self):
        self.code_list = get_code_list()
        self.ffd = FetchFinancialData(self.financial_date, self.code_list)
        self.ffd.sig_fetch_financial.connect(self.set_progress_bar)
        self.ffd.sig_fetch_financial_done.connect(
            self.complete_financial_progress)
        self.ffd.err_signal.connect(self.show_warning)
        self.ffd.start()

    def on_up_financial_data(self):
        self.progress_bar.reset()
        self.disable_all()

        if self.financial_date is None:
            self.prepare_financial_date()

        if self.financial_date is not None:
            self._up_financial_data()
        else:
            QMessageBox.warning(self, '警告', '日K更新失败，请重试',
                                QMessageBox.Ok, QMessageBox.Ok)

    def complete_day_k_progress(self):
        self.set_progress_bar(100)
        self.enable_all()
        save_last_updated_date(self.day_e_date, 'd')
        self.code_list = []
        self.progress_bar.reset()

    def _up_day_k(self):
        self.code_list = get_code_list()
        self.fdk = FetchDayK(self.day_e_date, self.code_list)
        self.fdk.sig_fetch_day_k.connect(self.set_progress_bar)
        self.fdk.sig_fetch_day_k_done.connect(self.complete_day_k_progress)
        self.fdk.err_signal.connect(self.show_warning)
        self.fdk.start()

    def on_up_day_k(self):
        self.progress_bar.reset()
        self.disable_all()

        if self.day_e_date is None:
            self.prepare_date_range('d')

        if self.day_e_date is not None:
            self._up_day_k()
        else:
            QMessageBox.warning(self, '警告', '日K更新失败，请重试',
                                QMessageBox.Ok, QMessageBox.Ok)

    def complete_stock_info_progress(self):
        self.set_progress_bar(100)
        self.enable_all()
        save_last_updated_date(self.index_date, 'i')
        self.progress_bar.reset()

    def on_up_stock_index(self):
        self.progress_bar.reset()
        self.disable_all()

        if self.index_date is None:
            self.prepare_index_update()

        if self.index_date is not None:
            lg = bs.login()
            ret, data = fetch_all_code(self.index_date)
            if ret != 0:
                msg = '获取index失败'
                self.show_warning(msg)
            bs.logout()
            reset_stock_index()
            store_all_code(data)
            self.complete_stock_info_progress()

    def prepare_index_update(self):
        ret = need_update('i')
        if ret == 0:
            lg = bs.login()
            if lg.error_code != '0' or lg.error_msg != 'success':
                QMessageBox.warning(self, '警告', lg.error_msg,
                                    QMessageBox.Ok, QMessageBox.Ok)
            ret, date_str = fetch_last_trading_day()
            bs.logout()
            if ret != 0:
                QMessageBox.warning(self, '警告', date_str,
                                    QMessageBox.Ok, QMessageBox.Ok)
            else:
                self.index_date = date_str

    def prepare_date_range(self, flag):
        ret = need_update(flag)
        if ret == 0:
            lg = bs.login()
            if lg.error_code != '0' or lg.error_msg != 'success':
                QMessageBox.warning(self, '警告', lg.error_msg,
                                    QMessageBox.Ok, QMessageBox.Ok)
            ret, day_e_date_str = fetch_last_trading_day()
            bs.logout()
            if ret != 0:
                QMessageBox.warning(self, '警告', day_e_date_str,
                                    QMessageBox.Ok, QMessageBox.Ok)

            self.day_e_date = day_e_date_str
        elif ret == -1:
            QMessageBox.information(self, '提示', '目前还没有更新的数据',
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.progress_bar.reset()
            self.enable_all()
            return False
        else:
            QMessageBox.warning(self, '警告', ret,
                                QMessageBox.Ok, QMessageBox.Ok)
            return False

    def prepare_financial_date(self):
        ret = need_update('f')
        if ret == 0:
            lg = bs.login()
            if lg.error_code != '0' or lg.error_msg != 'success':
                QMessageBox.warning(self, '警告', lg.error_msg,
                                    QMessageBox.Ok, QMessageBox.Ok)
            ret, financial_date_str = fetch_last_trading_day()
            bs.logout()
            if ret != 0:
                QMessageBox.warning(self, '警告', financial_date_str,
                                    QMessageBox.Ok, QMessageBox.Ok)

            self.financial_date = financial_date_str
        elif ret == -1:
            QMessageBox.information(self, '提示', '目前还没有更新的数据',
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.progress_bar.reset()
            self.enable_all()
            return False
        else:
            QMessageBox.warning(self, '警告', ret,
                                QMessageBox.Ok, QMessageBox.Ok)
            return False

    def on_about(self):
        about = About(self)
        about.show()
        about.exec_()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Config()
    main.show()
    sys.exit(app.exec_())
