import baostock as bs
import datetime

from qtpy.QtCore import *
from qtpy.QtWidgets import *

from apis.k_charts import FetchDayK, UpdateStockInfo, \
    get_code_list, reset_k_line_data
from apis.stock_info import save_last_updated_date
from apis.stock_info import need_update, reset_last_updated_date, \
    fetch_last_trading_day, get_last_updated_date, reset_stock_info
from pages.about import About


class Config(QWidget):
    def __init__(self, parent=None):
        super(Config, self).__init__(parent)
        self.setWindowTitle('设置')

        self.fdk = None
        self.fwk = None
        self.fmk = None
        self.index_date = None
        self.day_s_date = None
        self.day_e_date = None
        self.code_list = None

        self.progress_bar = QProgressBar()

        self.up_group_box = QGroupBox()
        up_h_box = QHBoxLayout()
        self.btn_up_stock_info = QPushButton('更新股票信息')
        self.btn_up_day_k = QPushButton('更新日K')
        up_h_box.addWidget(self.btn_up_stock_info)
        up_h_box.addWidget(self.btn_up_day_k)
        up_h_box.addStretch()
        self.up_group_box.setLayout(up_h_box)

        self.reset_up_group_box = QGroupBox()
        reset_up_h_box = QHBoxLayout()
        self.btn_reset = QPushButton('删除所有数据')
        reset_up_h_box.addWidget(self.btn_reset)
        reset_up_h_box.addStretch()
        self.reset_up_group_box.setLayout(reset_up_h_box)

        self.range_up_group_box = QGroupBox()
        range_up_h_box = QHBoxLayout()
        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-1))
        self.start_date.setDate(QDate.currentDate().addDays(-365))

        self.end_date = QDateTimeEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.end_date.setMaximumDate(QDate.currentDate().addDays(0))
        self.end_date.setDate(QDate.currentDate())

        self.btn_up_range_stock_info = QPushButton('按日期更新股票信息')
        self.btn_up_range_day_k = QPushButton('按日期更新日K')

        range_up_h_box.addWidget(self.start_date)
        range_up_h_box.addWidget(self.end_date)
        range_up_h_box.addWidget(self.btn_up_range_stock_info)
        range_up_h_box.addWidget(self.btn_up_range_day_k)
        range_up_h_box.addStretch()
        self.range_up_group_box.setLayout(range_up_h_box)

        about_h_box = QHBoxLayout()
        self.btn_about = QPushButton('关于')
        about_h_box.addStretch()
        about_h_box.addWidget(self.btn_about)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addWidget(self.up_group_box)
        main_v_box.addWidget(self.reset_up_group_box)
        main_v_box.addWidget(self.range_up_group_box)
        main_v_box.addStretch()
        main_v_box.addLayout(about_h_box)

        self.setLayout(main_v_box)

        self.btn_up_stock_info.clicked.connect(self.on_up_stock_info)
        self.btn_up_day_k.clicked.connect(self.on_up_day_k)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_up_range_stock_info.clicked.connect(
            self.on_up_custom_stock_info)
        self.btn_up_range_day_k.clicked.connect(self.on_up_custom_day_k)
        self.btn_about.clicked.connect(self.on_about)

    def enable_all(self):
        self.btn_up_stock_info.setEnabled(True)
        self.btn_up_day_k.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_up_range_stock_info.setEnabled(True)
        self.btn_up_range_day_k.setEnabled(True)
        self.start_date.setEnabled(True)
        self.end_date.setEnabled(True)

    def disable_all(self):
        self.btn_up_stock_info.setDisabled(True)
        self.btn_up_day_k.setDisabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_up_range_stock_info.setDisabled(True)
        self.btn_up_range_day_k.setDisabled(True)
        self.start_date.setDisabled(True)
        self.end_date.setDisabled(True)

    def set_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def show_warning(self, msg):
        QMessageBox.warning(self, '警告', msg,
                            QMessageBox.Ok, QMessageBox.Ok)
        self.enable_all()

    def on_reset(self):
        self.progress_bar.reset()
        reset_stock_info()
        reset_k_line_data()
        reset_last_updated_date()

    def complete_day_k_progress(self):
        self.set_progress_bar(100)
        self.enable_all()
        save_last_updated_date(self.day_e_date, 'd')
        self.code_list = []
        self.progress_bar.reset()

    def _up_day_k(self):
        self.code_list = get_code_list()
        self.fdk = FetchDayK(self.day_s_date, self.day_e_date, self.code_list)
        self.fdk.sig_fetch_day_k.connect(self.set_progress_bar)
        self.fdk.sig_fetch_day_k_done.connect(self.complete_day_k_progress)
        self.fdk.err_signal.connect(self.show_warning)
        self.fdk.start()

    def on_up_day_k(self):
        self.progress_bar.reset()
        self.disable_all()

        if self.day_s_date is None or self.day_e_date is None:
            self.prepare_date_range('d')

        if self.day_s_date is not None and self.day_e_date is not None:
            self._up_day_k()
        else:
            QMessageBox.warning(self, '警告', '日K更新失败，请重试',
                                QMessageBox.Ok, QMessageBox.Ok)

    def complete_stock_info_progress(self):
        self.set_progress_bar(100)
        self.enable_all()
        save_last_updated_date(self.index_date, 'i')
        self.progress_bar.reset()

    def _up_stock_info(self):
        self.usi = UpdateStockInfo(self.index_date)
        self.usi.sig_up_stock_info.connect(self.set_progress_bar)
        self.usi.sig_up_stock_info_done.connect(
            self.complete_stock_info_progress)
        self.usi.err_signal.connect(self.show_warning)
        self.usi.start()

    def on_up_stock_info(self):
        self.progress_bar.reset()
        self.disable_all()

        if self.index_date is None:
            self.prepare_index_update()

        if self.index_date is not None:
            self._up_stock_info()
        else:
            QMessageBox.warning(self, '警告', '股票信息更新失败，请重试',
                                QMessageBox.Ok, QMessageBox.Ok)

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

            day_s_date_str = get_last_updated_date(flag)
            day_e_date = datetime.datetime.strptime(day_e_date_str,
                                                    '%Y-%m-%d')
            day_s_date = datetime.datetime.strptime(day_s_date_str,
                                                    '%Y-%m-%d')
            if day_s_date_str == '1970-01-01':
                day_s_date = day_e_date - datetime.timedelta(days=365)
            day_s_date_str = day_s_date.strftime('%Y-%m-%d')
            day_e_date_str = day_e_date.strftime('%Y-%m-%d')
            self.day_s_date = day_s_date_str
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

    def on_up_custom_day_k(self):
        self.custom_date_range()
        self.on_up_day_k()

    def on_up_custom_stock_info(self):
        self.on_up_stock_info()

    def custom_date_range(self):
        self.progress_bar.reset()
        self.disable_all()

        day_s_date = self.start_date.date().toPython()
        day_e_date = self.end_date.date().toPython()
        self.day_s_date = day_s_date.strftime('%Y-%m-%d')
        self.day_e_date = day_e_date.strftime('%Y-%m-%d')

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
