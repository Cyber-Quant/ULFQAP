import baostock as bs
import datetime

from qtpy.QtCore import *
from qtpy.QtWidgets import *

from apis.k_day import FetchDayK, reset_k_line_data
from apis.stock_info import need_update, reset_last_updated_date, \
    fetch_last_trading_day, get_last_updated_date, reset_stock_info
from pages.about import About


class Config(QWidget):
    def __init__(self, parent=None):
        super(Config, self).__init__(parent)
        self.setWindowTitle('设置')

        self.fdk = None

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
        self.btn_fetch_a_year = QPushButton('获取最近一年的数据')
        reset_up_h_box.addWidget(self.btn_reset)
        reset_up_h_box.addWidget(self.btn_fetch_a_year)
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
        self.btn_fetch_a_year.clicked.connect(self.on_fetch_a_year)
        self.btn_up_range.clicked.connect(self.on_fetch_range)
        self.btn_about.clicked.connect(self.on_about)

    def enable_all_buttons(self):
        self.btn_up.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_fetch_a_year.setEnabled(True)
        self.btn_up_range.setEnabled(True)

    def disable_all_buttons(self):
        self.btn_up.setDisabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_fetch_a_year.setDisabled(True)
        self.btn_up_range.setDisabled(True)

    def set_progress_bar(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.enable_all_buttons()

    def show_warning(self, msg):
        QMessageBox.warning(self, '警告', msg,
                            QMessageBox.Ok, QMessageBox.Ok)
        self.enable_all_buttons()

    def _up_k_line(self, s_date, e_date):
        self.fdk = FetchDayK(s_date, e_date)
        self.fdk.progress_signal.connect(self.set_progress_bar)
        self.fdk.err_signal.connect(self.show_warning)
        self.fdk.start()

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
            ret, e_date = fetch_last_trading_day()
            if ret != 0:
                QMessageBox.warning(self, '警告', e_date,
                                    QMessageBox.Ok, QMessageBox.Ok)
            bs.logout()

            s_date = get_last_updated_date()
            if s_date == '1970-01-01':
                e_date = datetime.datetime.strptime(e_date, '%Y-%m-%d')
                s_date = e_date - datetime.timedelta(days=31)
                s_date = s_date.strftime('%Y-%m-%d')
                e_date = e_date.strftime('%Y-%m-%d')

            self._up_k_line(s_date, e_date)
        elif ret == -1:
            QMessageBox.information(self, '提示', '目前还没有更新的数据',
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.progress_bar.reset()
            self.enable_all_buttons()
        else:
            QMessageBox.warning(self, '警告', ret,
                                QMessageBox.Ok, QMessageBox.Ok)
            return False

    def on_fetch_a_year(self):
        self.progress_bar.reset()
        self.disable_all_buttons()

        lg = bs.login()
        if lg.error_code != '0' or lg.error_msg != 'success':
            QMessageBox.warning(self, '警告', lg.error_msg,
                                QMessageBox.Ok, QMessageBox.Ok)
        ret, date = fetch_last_trading_day()
        if ret != 0:
            QMessageBox.warning(self, '警告', date,
                                QMessageBox.Ok, QMessageBox.Ok)
        bs.logout()

        e_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        s_date = e_date - datetime.timedelta(days=365)
        s_date = s_date.strftime('%Y-%m-%d')
        e_date = e_date.strftime('%Y-%m-%d')
        self._up_k_line(s_date, e_date)

    def on_fetch_range(self):
        self.progress_bar.reset()
        self.disable_all_buttons()

        s_date = self.start_date.date().toString('yyyy-MM-dd')
        e_date = self.end_date.date().toString('yyyy-MM-dd')
        self._up_k_line(s_date, e_date)

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
