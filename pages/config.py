import baostock as bs
import datetime

from qtpy.QtCore import *
from qtpy.QtWidgets import *

from apis.k_charts import FetchDayK, FetchWeekK, FetchMonthK, UpdateStockInfo, \
    get_code_list, reset_k_line_data, save_last_updated_date
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
        self.day_s_date = None
        self.day_e_date = None
        self.week_s_date = None
        self.week_e_date = None
        self.month_s_date = None
        self.month_e_date = None
        self.code_list = None

        self.progress_bar = QProgressBar()

        self.up_group_box = QGroupBox()
        up_h_box = QHBoxLayout()
        self.btn_up = QPushButton('更新到最新')
        up_h_box.addWidget(self.btn_up)
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
        self.start_date.setDate(QDate.currentDate().addDays(-30))

        self.end_date = QDateTimeEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.end_date.setMaximumDate(QDate.currentDate().addDays(0))
        self.end_date.setDate(QDate.currentDate())

        self.btn_up_range = QPushButton('按日期更新')

        range_up_h_box.addWidget(self.start_date)
        range_up_h_box.addWidget(self.end_date)
        range_up_h_box.addWidget(self.btn_up_range)
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

        self.btn_up.clicked.connect(self.on_up)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_up_range.clicked.connect(self.on_fetch_range)
        self.btn_about.clicked.connect(self.on_about)

    def enable_all_buttons(self):
        self.btn_up.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_up_range.setEnabled(True)

    def disable_all_buttons(self):
        self.btn_up.setDisabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_up_range.setDisabled(True)

    def complete_stock_info_progress(self):
        self.code_list = get_code_list()
        self.fdk = FetchDayK(self.day_s_date, self.day_e_date, self.code_list)
        self.fdk.sig_fetch_day_k.connect(self.set_progress_bar)
        self.fdk.sig_fetch_day_k_done.connect(self.complete_day_k_progress)
        self.fdk.err_signal.connect(self.show_warning)
        self.fdk.start()

    def complete_day_k_progress(self):
        self.fwk = FetchWeekK(self.week_s_date, self.week_e_date,
                              self.code_list)
        self.fwk.sig_fetch_week_k.connect(self.set_progress_bar)
        self.fwk.sig_fetch_week_k_done.connect(
            self.complete_week_k_progress)
        self.fwk.err_signal.connect(self.show_warning)
        self.fwk.start()

    def complete_week_k_progress(self):
        self.fmk = FetchMonthK(self.month_s_date, self.month_e_date,
                               self.code_list)
        self.fmk.sig_fetch_month_k.connect(self.set_progress_bar)
        self.fmk.sig_fetch_month_k_done.connect(
            self.complete_month_k_progress)
        self.fmk.err_signal.connect(self.show_warning)
        self.fmk.start()

    def complete_month_k_progress(self):
        self.set_progress_bar(100)
        self.enable_all_buttons()
        save_last_updated_date(self.day_e_date)
        self.code_list = []
        self.progress_bar.reset()

    def set_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def show_warning(self, msg):
        QMessageBox.warning(self, '警告', msg,
                            QMessageBox.Ok, QMessageBox.Ok)
        self.enable_all_buttons()

    def _up_k_line(self):
        self.usi = UpdateStockInfo(self.day_e_date)
        self.usi.sig_up_stock_info.connect(self.set_progress_bar)
        self.usi.sig_up_stock_info_done.connect(
            self.complete_stock_info_progress)
        self.usi.err_signal.connect(self.show_warning)
        self.usi.start()

    def on_reset(self):
        self.progress_bar.reset()
        reset_stock_info()
        reset_k_line_data()
        reset_last_updated_date()

    def on_up(self):
        self.progress_bar.reset()
        self.disable_all_buttons()

        ret = need_update()
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

            day_s_date_str = get_last_updated_date()
            day_e_date = datetime.datetime.strptime(day_e_date_str,
                                                    '%Y-%m-%d')
            day_s_date = datetime.datetime.strptime(day_s_date_str,
                                                    '%Y-%m-%d')
            week_s_date = day_s_date - datetime.timedelta(days=365 * 5)
            week_e_date = day_e_date
            month_s_date = day_s_date - datetime.timedelta(days=365 * 21)
            month_e_date = day_e_date
            if day_s_date_str == '1970-01-01':
                day_s_date = day_e_date - datetime.timedelta(days=365)

            day_s_date_str = day_s_date.strftime('%Y-%m-%d')
            day_e_date_str = day_e_date.strftime('%Y-%m-%d')
            week_s_date_str = week_s_date.strftime('%Y-%m-%d')
            week_e_date_str = week_e_date.strftime('%Y-%m-%d')
            month_s_date_str = month_s_date.strftime('%Y-%m-%d')
            month_e_date_str = month_e_date.strftime('%Y-%m-%d')

            self.day_s_date = day_s_date_str
            self.day_e_date = day_e_date_str
            self.week_s_date = week_s_date_str
            self.week_e_date = week_e_date_str
            self.month_s_date = month_s_date_str
            self.month_e_date = month_e_date_str

            self._up_k_line()

        elif ret == -1:
            QMessageBox.information(self, '提示', '目前还没有更新的数据',
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.progress_bar.reset()
            self.enable_all_buttons()
        else:
            QMessageBox.warning(self, '警告', ret,
                                QMessageBox.Ok, QMessageBox.Ok)
            return False

    def on_fetch_range(self):
        self.progress_bar.reset()
        self.disable_all_buttons()

        day_s_date = self.start_date.date().toPython()
        day_e_date = self.end_date.date().toPython()
        week_s_date = day_s_date - datetime.timedelta(days=365 * 5)
        week_e_date = day_e_date
        month_s_date = day_s_date - datetime.timedelta(days=365 * 21)
        month_e_date = day_e_date

        self.day_s_date = day_s_date.strftime('%Y-%m-%d')
        self.day_e_date = day_e_date.strftime('%Y-%m-%d')
        self.week_s_date = week_s_date.strftime('%Y-%m-%d')
        self.week_e_date = week_e_date.strftime('%Y-%m-%d')
        self.month_s_date = month_s_date.strftime('%Y-%m-%d')
        self.month_e_date = month_e_date.strftime('%Y-%m-%d')

        self._up_k_line()

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
