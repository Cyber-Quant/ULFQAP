import datetime
import json

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import stock_pool_config_path
from strategies.common import get_stat_date, get_value_info
from strategies.value import ValueChoose


class Factor(QWidget):
    def __init__(self, parent=None):
        super(Factor, self).__init__(parent)
        self.setWindowTitle('股池')

        self.pool_thread = None
        self.stock_pool = []
        self.current_code = None
        self.stat_date = get_stat_date()

        self.progress_bar = QProgressBar()

        int_validator = QIntValidator()
        condition_h_box = QHBoxLayout()
        self.roe_group = QGroupBox()
        self.roe_label = QLabel('ROE大于')
        self.roe_input = QLineEdit()
        self.roe_input.setValidator(int_validator)
        self.roe_input.setText('12')
        roe_h_box = QHBoxLayout()
        roe_h_box.addWidget(self.roe_label)
        roe_h_box.addWidget(self.roe_input)
        self.roe_group.setLayout(roe_h_box)

        self.ltv_group = QGroupBox()
        self.ltv_label = QLabel('质押率小于')
        self.ltv_input = QLineEdit()
        self.ltv_input.setValidator(int_validator)
        self.ltv_input.setText('20')
        ltv_h_box = QHBoxLayout()
        ltv_h_box.addWidget(self.ltv_label)
        ltv_h_box.addWidget(self.ltv_input)
        self.ltv_group.setLayout(ltv_h_box)

        self.ito_group = QGroupBox()
        self.ito_label = QLabel('存货率小于')
        self.ito_input = QLineEdit()
        self.ito_input.setValidator(int_validator)
        self.ito_input.setText('30')
        ito_h_box = QHBoxLayout()
        ito_h_box.addWidget(self.ito_label)
        ito_h_box.addWidget(self.ito_input)
        self.ito_group.setLayout(ito_h_box)

        self.artr_group = QGroupBox()
        self.artr_label = QLabel('应收帐款率小于')
        self.artr_input = QLineEdit()
        self.artr_input.setValidator(int_validator)
        self.artr_input.setText('30')
        artr_h_box = QHBoxLayout()
        artr_h_box.addWidget(self.artr_label)
        artr_h_box.addWidget(self.artr_input)
        self.artr_group.setLayout(artr_h_box)

        self.dar_group = QGroupBox()
        self.dar_label = QLabel('资产负债率小于')
        self.dar_input = QLineEdit()
        self.dar_input.setValidator(int_validator)
        self.dar_input.setText('50')
        dar_h_box = QHBoxLayout()
        dar_h_box.addWidget(self.dar_label)
        dar_h_box.addWidget(self.dar_input)
        self.dar_group.setLayout(dar_h_box)

        condition_h_box.addWidget(self.roe_group)
        condition_h_box.addWidget(self.ltv_group)
        condition_h_box.addWidget(self.ito_group)
        condition_h_box.addWidget(self.artr_group)
        condition_h_box.addWidget(self.dar_group)

        op_h_box = QHBoxLayout()
        self.btn_search = QPushButton('筛选')
        op_h_box.addLayout(condition_h_box)
        op_h_box.addWidget(self.btn_search)

        result_h_box = QHBoxLayout()
        pool_v_box = QVBoxLayout()
        info_v_box = QVBoxLayout()
        line1_h_box = QHBoxLayout()
        self.roe_info_label = QLabel('ROE:')
        self.ltv_info_label = QLabel('质押率:')
        self.ito_info_label = QLabel('存货率:')
        line1_h_box.addWidget(self.roe_info_label)
        line1_h_box.addWidget(self.ltv_info_label)
        line1_h_box.addWidget(self.ito_info_label)
        line2_h_box = QHBoxLayout()
        self.artr_info_label = QLabel('应收账款率:')
        self.dar_info_label = QLabel('资产负债率:')
        line2_h_box.addWidget(self.artr_info_label)
        line2_h_box.addWidget(self.dar_info_label)
        info_v_box.addLayout(line1_h_box)
        info_v_box.addLayout(line2_h_box)

        self.pool_table = QTableWidget()
        headers = ['代码', '股票']
        self.pool_table.setColumnCount(len(headers))
        self.pool_table.setHorizontalHeaderLabels(headers)
        self.pool_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.pool_table.verticalHeader().setVisible(False)
        self.pool_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.pool_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pool_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pool_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.pool_table.setSortingEnabled(True)
        self.pool_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pool_table.setMinimumWidth(220)
        self.pool_table.setMaximumWidth(250)
        pool_v_box.addLayout(info_v_box)
        pool_v_box.addWidget(self.pool_table)

        self.table = QTableWidget()
        headers = ['代码', '股票', 'ROE', '质押率', '存货率', '应收帐款率', '资产负债率']
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

        result_h_box.addLayout(pool_v_box)
        result_h_box.addWidget(self.table)

        main_v_box = QVBoxLayout()
        main_v_box.addWidget(self.progress_bar)
        main_v_box.addLayout(op_h_box)
        main_v_box.addLayout(result_h_box)

        self.setLayout(main_v_box)

        self.btn_search.clicked.connect(self.on_search)
        self.table.customContextMenuRequested.connect(self.open_ops_menu)
        self.pool_table.customContextMenuRequested.connect(
            self.open_pool_ops_menu)
        self.pool_table.itemSelectionChanged.connect(self.on_pool_row_changed)

        self.on_refresh_pool_table()

    def disable_all(self):
        self.btn_search.setDisabled(True)

    def enable_all(self):
        self.btn_search.setEnabled(True)

    def set_progress_bar(self, value, code, name, roe, ltv, ito, artr, dar):
        self.progress_bar.setValue(value)
        if value == 100:
            self.enable_all()
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(roe)))
            self.table.setItem(row, 3, QTableWidgetItem(str(ltv)))
            self.table.setItem(row, 4, QTableWidgetItem(str(ito)))
            self.table.setItem(row, 5, QTableWidgetItem(str(artr)))
            self.table.setItem(row, 6, QTableWidgetItem(str(dar)))

    def on_search(self):
        roe = int(self.roe_input.text())
        ltv = int(self.ltv_input.text())
        ito = int(self.ito_input.text())
        artr = int(self.artr_input.text())
        dar = int(self.dar_input.text())

        self.disable_all()

        rows = self.table.rowCount()
        for i in reversed(range(rows)):
            self.table.removeRow(i)
        self.clear_stock_pool()

        self.pool_thread = ValueChoose(roe, ltv, ito, artr, dar)
        self.pool_thread.progress_signal.connect(
            self.set_progress_bar)
        self.pool_thread.start()

    def on_pool_row_changed(self):
        row = self.pool_table.currentRow()
        if row == -1:
            return
        code = self.pool_table.item(row, 0).text()
        for stock in self.stock_pool:
            if stock['code'] == code:
                roe = stock['roe']
                ltv = stock['ltv']
                ito = stock['ito']
                artr = stock['artr']
                dar = stock['dar']
                roe_txt = 'ROE: ' + str(roe)
                self.roe_info_label.setText(roe_txt)
                ltv_txt = '质押率: ' + str(ltv)
                self.ltv_info_label.setText(ltv_txt)
                ito_txt = '存货率: ' + str(ito)
                self.ito_info_label.setText(ito_txt)
                artr_txt = '应收账款率: ' + str(artr)
                self.artr_info_label.setText(artr_txt)
                dar_txt = '资产负债率: ' + str(dar)
                self.dar_info_label.setText(dar_txt)

    def display_basic_info(self, code):
        _, _, roe, ltv, ito, artr, dar = get_value_info(code, self.stat_date)
        self.roe_info_label.setText(str(roe))
        self.ito_info_label.setText(str(ito))
        self.artr_info_label.setText(str(artr))
        self.dar_info_label.setText(str(dar))

    def on_refresh_pool_table(self):
        if not stock_pool_config_path.exists():
            self.stock_pool = []
        else:
            with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                self.stock_pool = json.load(f)

        self.pool_table.setRowCount(0)
        for stock in self.stock_pool:
            row = self.pool_table.rowCount()
            self.pool_table.insertRow(row)
            self.pool_table.setItem(row, 0, QTableWidgetItem(stock['code']))
            self.pool_table.setItem(row, 1, QTableWidgetItem(stock['name']))

    def clear_stock_pool(self):
        self.stock_pool = []
        with open(stock_pool_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_pool, f, indent=4, ensure_ascii=False)
        self.on_refresh_pool_table()

    def on_remove(self):
        if not stock_pool_config_path.exists():
            self.stock_pool = []
        else:
            with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                self.stock_pool = json.load(f)

        rows = self.table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                code = self.table.item(row.row(), 0).text()
                for stock in self.stock_pool:
                    if stock['code'] == code:
                        self.stock_pool.remove(stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.table.removeRow(row_idx)

        with open(stock_pool_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_pool, f, indent=4, ensure_ascii=False)
        self.on_refresh_pool_table()

    def on_add_to_pool(self):
        if not stock_pool_config_path.exists():
            self.stock_pool = []
        else:
            with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                self.stock_pool = json.load(f)

        rows = self.table.selectedIndexes()
        for row in rows:
            stock = {
                'code': self.table.item(row.row(), 0).text(),
                'name': self.table.item(row.row(), 1).text(),
                'roe': float(self.table.item(row.row(), 2).text()),
                'ltv': float(self.table.item(row.row(), 3).text()),
                'ito': float(self.table.item(row.row(), 4).text()),
                'artr': float(self.table.item(row.row(), 5).text()),
                'dar': float(self.table.item(row.row(), 6).text())
            }
            if stock not in self.stock_pool:
                self.stock_pool.append(stock)

        with open(stock_pool_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_pool, f, indent=4, ensure_ascii=False)
        self.on_refresh_pool_table()

    def on_remove_from_pool(self):
        if not stock_pool_config_path.exists():
            self.stock_pool = []
        else:
            with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                self.stock_pool = json.load(f)

        rows = self.table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                code = self.table.item(row.row(), 0).text()
                for stock in self.stock_pool:
                    if stock['code'] == code:
                        self.stock_pool.remove(stock)

        with open(stock_pool_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_pool, f, indent=4, ensure_ascii=False)
        self.on_refresh_pool_table()

    def open_ops_menu(self, position):
        pop_menu = QMenu()
        add_to_pool = QAction('加入股票池', self)
        remove_from_pool = QAction('删除股票池', self)
        remove_action = QAction('删除', self)
        pop_menu.addAction(add_to_pool)
        pop_menu.addAction(remove_from_pool)
        pop_menu.addSeparator()
        pop_menu.addAction(remove_action)

        add_to_pool.triggered.connect(self.on_add_to_pool)
        remove_from_pool.triggered.connect(self.on_remove_from_pool)
        remove_action.triggered.connect(self.on_remove)
        pop_menu.exec_(self.table.mapToGlobal(position))

    def on_pool_remove(self):
        if not stock_pool_config_path.exists():
            self.stock_pool = []
        else:
            with open(stock_pool_config_path, 'r', encoding='utf-8') as f:
                self.stock_pool = json.load(f)

        rows = self.pool_table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                code = self.pool_table.item(row.row(), 0).text()
                for stock in self.stock_pool:
                    if stock['code'] == code:
                        self.stock_pool.remove(stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.pool_table.removeRow(row_idx)

        with open(stock_pool_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_pool, f, indent=4, ensure_ascii=False)
        self.on_refresh_pool_table()

    def open_pool_ops_menu(self, position):
        pop_menu = QMenu()
        remove_action = QAction('删除', self)
        pop_menu.addAction(remove_action)

        remove_action.triggered.connect(self.on_pool_remove)
        pop_menu.exec_(self.pool_table.mapToGlobal(position))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = Factor()
    main.show()
    sys.exit(app.exec_())
