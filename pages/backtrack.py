import pyqtgraph as pg

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *


class Backtrack(QWidget):
    def __init__(self, parent=None):
        super(Backtrack, self).__init__(parent)
        self.setWindowTitle('回测')

        self.op_group_box = QGroupBox()
        op_h_box = QHBoxLayout()

        start_date_v_box = QVBoxLayout()
        self.start_date_label = QLabel('起始日期')
        self.start_date = QDateTimeEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('yyyy-MM-dd')
        self.start_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.start_date.setMaximumDate(QDate.currentDate().addDays(-1))
        self.start_date.setDate(QDate.currentDate().addDays(-365))
        start_date_v_box.addWidget(self.start_date_label)
        start_date_v_box.addWidget(self.start_date)

        end_date_v_box = QVBoxLayout()
        self.end_date_label = QLabel('结束日期')
        self.end_date = QDateTimeEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('yyyy-MM-dd')
        self.end_date.setMinimumDate(QDate.currentDate().addDays(-3650))
        self.end_date.setMaximumDate(QDate.currentDate().addDays(0))
        self.end_date.setDate(QDate.currentDate())
        end_date_v_box.addWidget(self.end_date_label)
        end_date_v_box.addWidget(self.end_date)

        double_validator = QDoubleValidator()
        init_money_v_box = QVBoxLayout()
        self.init_money_label = QLabel('初始资金')
        self.init_money_input = QLineEdit()
        self.init_money_input.setValidator(double_validator)
        init_money_v_box.addWidget(self.init_money_label)
        init_money_v_box.addWidget(self.init_money_input)

        offset_v_box = QVBoxLayout()
        self.offset_label = QLabel('滑点')
        self.offset_input = QLineEdit()
        self.offset_input.setValidator(double_validator)
        offset_v_box.addWidget(self.offset_label)
        offset_v_box.addWidget(self.offset_input)

        fee_v_box = QVBoxLayout()
        self.fee_label = QLabel('手续费')
        self.fee_input = QLineEdit()
        self.fee_input.setValidator(double_validator)
        fee_v_box.addWidget(self.fee_label)
        fee_v_box.addWidget(self.fee_input)

        tax_v_box = QVBoxLayout()
        self.tax_label = QLabel('印花税')
        self.tax_input = QLineEdit()
        self.tax_input.setValidator(double_validator)
        tax_v_box.addWidget(self.tax_label)
        tax_v_box.addWidget(self.tax_input)

        options_v_box = QVBoxLayout()
        self.track_fav_check = QCheckBox('只回测自选股')
        self.track_fav_check.setChecked(True)
        self.track_pool_check = QCheckBox('只回测预选池股票')
        self.track_all_check = QCheckBox('回测所有股票')
        options_v_box.addWidget(self.track_fav_check)
        options_v_box.addWidget(self.track_pool_check)
        options_v_box.addWidget(self.track_all_check)

        op_v_box = QVBoxLayout()
        self.track_fav_check.setChecked(True)
        self.btn_backtrack = QPushButton('开始回测')
        op_v_box.addWidget(self.btn_backtrack)

        op_h_box.addLayout(start_date_v_box)
        op_h_box.addLayout(end_date_v_box)
        op_h_box.addLayout(init_money_v_box)
        op_h_box.addLayout(offset_v_box)
        op_h_box.addLayout(fee_v_box)
        op_h_box.addLayout(tax_v_box)
        op_h_box.addLayout(options_v_box)
        op_h_box.addLayout(op_v_box)
        op_h_box.addStretch()
        self.op_group_box.setLayout(op_h_box)

        self.progress_bar = QProgressBar()

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
        self.k_plt = pg.PlotWidget(enableMenu=False)
        result_h_box.addWidget(self.table)
        result_h_box.addWidget(self.k_plt)
        result_h_box.addStretch()

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addWidget(self.op_group_box)
        main_v_box.addLayout(result_h_box)

        self.setLayout(main_v_box)

        self.btn_backtrack.clicked.connect(self.on_backtrack)

    def on_backtrack(self):
        msg = '''
        复权还没做，回测的结果也不会准，所以还没做。
        该功能主要用来测试新开发的策略，不影响使用。
        '''
        QMessageBox.warning(self, '警告', msg,
                            QMessageBox.Ok, QMessageBox.Ok)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Backtrack()
    main.show()
    sys.exit(app.exec_())
