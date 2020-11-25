import json

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from conf.conf import apply_rules_config_path, fav_stocks_config_path, \
    custom_watch_config_path, bundle_dir
from pages.choose import Choose
from pages.config import Config
from pages.watch import Watch
from pages.backtrack import Backtrack
from rules.boll import BOLLConfig, BOLLInfo
from rules.dual_ma import DualMAConfig, DualMAInfo
from rules.kdj import KDJConfig, KDJInfo
from rules.macd import MACDConfig, MACDInfo
from rules.rsi import RSIConfig, RSIInfo
from rules.turtle import TurtleConfig, TurtleInfo
from rules.wr import WRConfig, WRInfo
from rules.volume_increase import VolumeIncreaseConfig, VolumeIncreaseInfo
from utils.custom_add_dialog import CustomAddDialog


def get_item_widget(name, pic_path):
    widget = QWidget()
    v_box = QVBoxLayout()
    pic_label = QLabel()
    pic_label.setFixedSize(30, 30)
    pic = QPixmap(pic_path.as_posix()).scaled(30, 30)
    pic_label.setPixmap(pic)
    pic_label.setAlignment(Qt.AlignTop)
    label = QLabel(name)
    label.setFixedWidth(30)
    label.setAlignment(Qt.AlignBottom)
    v_box.addWidget(pic_label)
    v_box.addWidget(label)
    widget.setLayout(v_box)

    return widget


class Nav(QWidget):
    def __init__(self, parent=None):
        super(Nav, self).__init__(parent)
        self.setWindowTitle('量化分析平台')
        icon = QIcon()
        self.setWindowIcon(QIcon((bundle_dir / 'media/logo.svg').as_posix()))
        self.resize(1280, 768)

        if not fav_stocks_config_path.exists():
            self.fav_stocks = []
        else:
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                self.fav_stocks = json.load(f)

        if not apply_rules_config_path.exists():
            self.apply_rules = []
        else:
            with open(apply_rules_config_path, 'r', encoding='utf-8') as f:
                self.apply_rules = json.load(f)

        if not custom_watch_config_path.exists():
            self.custom_watch = []
        else:
            with open(custom_watch_config_path, 'r', encoding='utf-8') as f:
                self.custom_watch = json.load(f)

        # NEW RULES #
        self.dual_ma_info = DualMAInfo()
        self.volume_increase_info = VolumeIncreaseInfo()
        self.wr_info = WRInfo()
        self.turtle_info = TurtleInfo()
        self.boll_info = BOLLInfo()
        self.macd_info = MACDInfo()
        self.kdj_info = KDJInfo()
        self.rsi_info = RSIInfo()

        self.watch = None
        self.choose = None
        self.back_track = None
        self.config = None

        main_h_box = QHBoxLayout()
        main_h_box.setContentsMargins(0, 0, 0, 0)

        op_v_box = QVBoxLayout()
        op_v_box.setContentsMargins(0, 0, 0, 0)
        pe = QPalette()
        self.logo = QLabel()
        # self.logo.setScaledContents(True)
        self.logo.setAutoFillBackground(True)
        pe.setColor(QPalette.Window, Qt.red)
        self.logo.setPalette(pe)
        self.logo.setFixedSize(50, 50)
        pic = QPixmap((bundle_dir / 'media/logo.svg').as_posix()).scaled(50, 50)
        self.logo.setPixmap(pic)

        self.list = QListWidget()
        self.list.setFixedWidth(50)
        self.list.setFrameShape(QListWidget.NoFrame)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        op_v_box.addWidget(self.logo)
        op_v_box.addWidget(self.list)

        main_h_box.addLayout(op_v_box)

        self.rule_fav_widget = QWidget()
        rule_fav_v_box = QVBoxLayout()
        rule_fav_v_box.setContentsMargins(0, 10, 0, 10)
        self.rule_table = QTableWidget()
        headers = ['应用', '策略', '选股', '盯盘']
        self.rule_table.setColumnCount(len(headers))
        self.rule_table.setHorizontalHeaderLabels(headers)
        self.rule_table.setColumnWidth(0, 37)
        self.rule_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self.rule_table.setColumnWidth(2, 30)
        self.rule_table.setColumnWidth(3, 30)
        self.rule_table.verticalHeader().setVisible(False)
        self.rule_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rule_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rule_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rule_table.setSortingEnabled(True)
        self.rule_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rule_table.customContextMenuRequested.connect(
            self.open_rule_table_menu)
        self.rule_table.itemSelectionChanged.connect(
            self.on_rule_table_row_changed)

        # NEW RULES #
        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.dual_ma_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.dual_ma_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.dual_ma_info.name in self.apply_rules:
            self.dual_ma_apply_check.setChecked(True)
        else:
            self.dual_ma_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(self.dual_ma_info.name))
        self.dual_ma_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.dual_ma_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.dual_ma_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.volume_increase_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.volume_increase_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.volume_increase_info.name in self.apply_rules:
            self.volume_increase_apply_check.setChecked(True)
        else:
            self.volume_increase_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(
                                    self.volume_increase_info.name))
        self.volume_increase_apply_check.stateChanged.connect(
            self.update_watch_rules)
        if self.volume_increase_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.volume_increase_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.wr_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.wr_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.wr_info.name in self.apply_rules:
            self.wr_apply_check.setChecked(True)
        else:
            self.wr_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(self.wr_info.name))
        self.wr_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.wr_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.wr_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.turtle_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.turtle_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.turtle_info.name in self.apply_rules:
            self.turtle_apply_check.setChecked(True)
        else:
            self.turtle_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1, QTableWidgetItem(self.turtle_info.name))
        self.turtle_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.turtle_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.turtle_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.boll_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.boll_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.boll_info.name in self.apply_rules:
            self.boll_apply_check.setChecked(True)
        else:
            self.boll_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1, QTableWidgetItem(self.boll_info.name))
        self.boll_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.boll_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.boll_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.macd_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.macd_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.macd_info.name in self.apply_rules:
            self.macd_apply_check.setChecked(True)
        else:
            self.macd_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(self.macd_info.name))
        self.macd_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.macd_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.macd_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.kdj_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.kdj_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.kdj_info.name in self.apply_rules:
            self.kdj_apply_check.setChecked(True)
        else:
            self.kdj_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(self.kdj_info.name))
        self.kdj_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.kdj_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.kdj_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        row = self.rule_table.rowCount()
        self.rule_table.insertRow(row)
        self.rsi_apply_check = QCheckBox()
        h_box = QHBoxLayout()
        # h_box.setAlignment(Qt.AlignCenter)
        h_box.addWidget(self.rsi_apply_check)
        widget = QWidget()
        widget.setLayout(h_box)
        if self.rsi_info.name in self.apply_rules:
            self.rsi_apply_check.setChecked(True)
        else:
            self.rsi_apply_check.setChecked(False)
        self.rule_table.setCellWidget(row, 0, widget)
        self.rule_table.setItem(row, 1,
                                QTableWidgetItem(self.rsi_info.name))
        self.rsi_apply_check.stateChanged.connect(self.update_watch_rules)
        if self.rsi_info.choose_flag:
            choose_flag = 'Y'
        else:
            choose_flag = 'N'
        item = QTableWidgetItem(choose_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 2, item)
        if self.rsi_info.watch_flag:
            watch_flag = 'Y'
        else:
            watch_flag = 'N'
        item = QTableWidgetItem(watch_flag)
        item.setTextAlignment(Qt.AlignCenter)
        self.rule_table.setItem(row, 3, item)

        self.fav_table = QTableWidget()
        headers = ['代码', '名称']
        self.fav_table.setColumnCount(len(headers))
        self.fav_table.setHorizontalHeaderLabels(headers)
        self.fav_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.fav_table.horizontalHeader().setVisible(False)
        self.fav_table.verticalHeader().setVisible(False)
        self.fav_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fav_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.fav_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.fav_table.setSortingEnabled(True)
        self.fav_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fav_table.customContextMenuRequested.connect(
            self.open_fav_table_menu)
        self.fav_table.itemSelectionChanged.connect(
            self.on_fav_table_row_changed)

        for stock in self.fav_stocks:
            row = self.fav_table.rowCount()
            self.fav_table.insertRow(row)
            self.fav_table.setItem(row, 0, QTableWidgetItem(stock['code']))
            self.fav_table.setItem(row, 1, QTableWidgetItem(stock['name']))

        rule_fav_v_box.addWidget(self.rule_table)
        rule_fav_v_box.addWidget(self.fav_table)
        self.rule_fav_widget.setLayout(rule_fav_v_box)
        self.rule_fav_widget.setMinimumWidth(220)
        self.rule_fav_widget.setMaximumWidth(250)
        main_h_box.addWidget(self.rule_fav_widget)

        self.stacked_window = QStackedWidget()
        main_h_box.addWidget(self.stacked_window)

        self.setLayout(main_h_box)

        self.init_nav_list()
        self.init_stacked_window()

        self.list.currentRowChanged.connect(self.stacked_window.setCurrentIndex)

    def init_nav_list(self):
        watch_widget = get_item_widget('盯盘', bundle_dir / 'media/watch.svg')
        watch_item = QListWidgetItem()
        watch_item.setSizeHint(QSize(150, 70))
        self.list.addItem(watch_item)
        self.list.setItemWidget(watch_item, watch_widget)
        self.list.setCurrentItem(watch_item)

        choose_widget = get_item_widget('选股', bundle_dir / 'media/choose.svg')
        choose_item = QListWidgetItem()
        choose_item.setSizeHint(QSize(150, 70))
        self.list.addItem(choose_item)
        self.list.setItemWidget(choose_item, choose_widget)

        test_widget = get_item_widget('回测', bundle_dir / 'media/backtrack.svg')
        test_item = QListWidgetItem()
        test_item.setSizeHint(QSize(150, 70))
        self.list.addItem(test_item)
        self.list.setItemWidget(test_item, test_widget)

        config_widget = get_item_widget('设置', bundle_dir / 'media/setting.svg')
        config_item = QListWidgetItem()
        config_item.setSizeHint(QSize(150, 70))
        self.list.addItem(config_item)
        self.list.setItemWidget(config_item, config_widget)

    def init_stacked_window(self):
        self.watch = Watch()
        self.stacked_window.addWidget(self.watch)

        self.choose = Choose()
        self.choose.fav_stock_changed_signal.connect(self.on_refresh_fav_table)
        self.stacked_window.addWidget(self.choose)

        self.back_track = Backtrack()
        self.stacked_window.addWidget(self.back_track)

        self.config = Config()
        self.stacked_window.addWidget(self.config)

    def update_watch_rules(self):
        # NEW RULES #
        if self.dual_ma_apply_check.isChecked() and \
                self.dual_ma_info.name not in self.apply_rules:
            self.apply_rules.append(self.dual_ma_info.name)
        if self.volume_increase_apply_check.isChecked() and \
                self.volume_increase_info.name not in self.apply_rules:
            self.apply_rules.append(self.volume_increase_info.name)
        if self.wr_apply_check.isChecked() and \
                self.wr_info.name not in self.apply_rules:
            self.apply_rules.append(self.wr_info.name)
        if self.turtle_apply_check.isChecked() and \
                self.turtle_info.name not in self.apply_rules:
            self.apply_rules.append(self.turtle_info.name)
        if self.boll_apply_check.isChecked() and \
                self.boll_info.name not in self.apply_rules:
            self.apply_rules.append(self.boll_info.name)
        if self.macd_apply_check.isChecked() and \
                self.macd_info.name not in self.apply_rules:
            self.apply_rules.append(self.macd_info.name)
        if self.kdj_apply_check.isChecked() and \
                self.kdj_info.name not in self.apply_rules:
            self.apply_rules.append(self.kdj_info.name)
        if self.rsi_apply_check.isChecked() and \
                self.rsi_info.name not in self.apply_rules:
            self.apply_rules.append(self.rsi_info.name)

        if not self.dual_ma_apply_check.isChecked() and \
                self.dual_ma_info.name in self.apply_rules:
            self.apply_rules.remove(self.dual_ma_info.name)
        if not self.volume_increase_apply_check.isChecked() and \
                self.volume_increase_info.name in self.apply_rules:
            self.apply_rules.remove(self.volume_increase_info.name)
        if not self.wr_apply_check.isChecked() and \
                self.wr_info.name in self.apply_rules:
            self.apply_rules.remove(self.wr_info.name)
        if not self.turtle_apply_check.isChecked() and \
                self.turtle_info.name in self.apply_rules:
            self.apply_rules.remove(self.turtle_info.name)
        if not self.boll_apply_check.isChecked() and \
                self.boll_info.name in self.apply_rules:
            self.apply_rules.remove(self.boll_info.name)
        if not self.macd_apply_check.isChecked() and \
                self.macd_info.name in self.apply_rules:
            self.apply_rules.remove(self.macd_info.name)
        if not self.kdj_apply_check.isChecked() and \
                self.kdj_info.name in self.apply_rules:
            self.apply_rules.remove(self.kdj_info.name)
        if not self.rsi_apply_check.isChecked() and \
                self.rsi_info.name in self.apply_rules:
            self.apply_rules.remove(self.rsi_info.name)

        with open(apply_rules_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.apply_rules, f, indent=4, ensure_ascii=False)

    def open_rule_table_menu(self, pos):
        pop_menu = QMenu()
        setting_action = QAction('详情/设置', self)
        pop_menu.addAction(setting_action)

        setting_action.triggered.connect(self.on_rule_setting)
        pop_menu.exec_(self.rule_table.mapToGlobal(pos))

    def on_rule_setting(self):
        row = self.rule_table.currentIndex().row()
        name = self.rule_table.item(row, 1).text()
        # NEW RULES #
        if name == self.dual_ma_info.name:
            cfg_dlg = DualMAConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.volume_increase_info.name:
            cfg_dlg = VolumeIncreaseConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.wr_info.name:
            cfg_dlg = WRConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.turtle_info.name:
            cfg_dlg = TurtleConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.boll_info.name:
            cfg_dlg = BOLLConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.macd_info.name:
            cfg_dlg = MACDConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.kdj_info.name:
            cfg_dlg = KDJConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.rsi_info.name:
            cfg_dlg = RSIConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()

    def open_fav_table_menu(self, pos):
        pop_menu = QMenu()
        refresh_action = QAction('刷新', self)
        custom_add_action = QAction('添加', self)
        un_fav_action = QAction('删除', self)
        set_custom_watch_action = QAction('设置价格提醒', self)
        pop_menu.addAction(refresh_action)
        pop_menu.addSeparator()
        pop_menu.addAction(custom_add_action)
        pop_menu.addAction(un_fav_action)
        pop_menu.addSeparator()
        pop_menu.addAction(set_custom_watch_action)

        refresh_action.triggered.connect(self.on_refresh_fav_table)
        custom_add_action.triggered.connect(self.on_custom_add)
        un_fav_action.triggered.connect(self.on_un_fav)
        set_custom_watch_action.triggered.connect(self.on_set_custom_watch)
        pop_menu.exec_(self.fav_table.mapToGlobal(pos))

    def on_refresh_fav_table(self):
        if not fav_stocks_config_path.exists():
            self.fav_stocks = []
        else:
            with open(fav_stocks_config_path, 'r', encoding='utf-8') as f:
                self.fav_stocks = json.load(f)

        self.fav_table.setRowCount(0)
        for stock in self.fav_stocks:
            row = self.fav_table.rowCount()
            self.fav_table.insertRow(row)
            self.fav_table.setItem(row, 0, QTableWidgetItem(stock['code']))
            self.fav_table.setItem(row, 1, QTableWidgetItem(stock['name']))

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
        if stock not in self.fav_stocks:
            self.fav_stocks.append(stock)

        row_idx = self.fav_table.rowCount()
        self.fav_table.insertRow(row_idx)
        self.fav_table.setItem(row_idx, 0, QTableWidgetItem(code))
        self.fav_table.setItem(row_idx, 1, QTableWidgetItem(name))

        with open(fav_stocks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.fav_stocks, f, indent=4, ensure_ascii=False)

    def on_un_fav(self):
        rows = self.fav_table.selectedIndexes()
        rows_to_remove = []
        for row in rows:
            if row.row() not in rows_to_remove:
                rows_to_remove.append(row.row())
                code = self.fav_table.item(row.row(), 0).text()
                stock = {
                    'code': code,
                    'name': self.fav_table.item(row.row(), 1).text()
                }
                if stock in self.fav_stocks:
                    self.fav_stocks.remove(stock)
                for custom_watch_stock in self.custom_watch:
                    if code == custom_watch_stock['code']:
                        self.custom_watch.remove(custom_watch_stock)

        rows_to_remove.sort(reverse=True)
        for row_idx in rows_to_remove:
            self.fav_table.removeRow(row_idx)

        with open(fav_stocks_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.fav_stocks, f, indent=4, ensure_ascii=False)
        with open(custom_watch_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.custom_watch, f, indent=4, ensure_ascii=False)

    def on_set_custom_watch(self):
        custom_watch_set_dlg = CustomWatchDialog(self)
        custom_watch_set_dlg.show()
        custom_watch_set_dlg.set_custom_watch_signal.connect(
            self.set_custom_watch)
        custom_watch_set_dlg.exec_()

    def set_custom_watch(self, up, down):
        row = self.fav_table.currentIndex().row()
        if row == -1:
            return
        code = self.fav_table.item(row, 0).text()
        name = self.fav_table.item(row, 1).text()
        obj = {
            'code': code,
            'name': name,
            'up': up,
            'down': down
        }
        if not custom_watch_config_path.exists():
            self.custom_watch = []
        else:
            with open(custom_watch_config_path, 'r', encoding='utf-8') as f:
                self.custom_watch = json.load(f)
        for item in self.custom_watch:
            if item['code'] == code:
                self.custom_watch.remove(item)
        self.custom_watch.append(obj)
        with open(custom_watch_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.custom_watch, f, indent=4, ensure_ascii=False)

    def on_fav_table_row_changed(self):
        row = self.fav_table.currentRow()
        code = self.fav_table.item(row, 0).text()
        name = self.fav_table.item(row, 1).text()
        row = self.rule_table.currentRow()
        if row != -1:
            rule = self.rule_table.item(row, 1).text()
        else:
            rule = None
        if self.list.currentRow() == 0:
            self.watch.draw_kline(code)
            self.watch.draw_indicatrix(rule)
        elif self.list.currentRow() == 1:
            self.choose.re_render_all_plots(code)
            self.choose.draw_indicatrix(rule)
        elif self.list.currentRow() == 2:
            self.back_track.set_code(code, name)

    def on_rule_table_row_changed(self):
        row = self.rule_table.currentRow()
        rule = self.rule_table.item(row, 1).text()
        row = self.fav_table.currentRow()
        if row != -1:
            code = self.fav_table.item(row, 0).text()
        else:
            code = None
        if self.list.currentRow() == 0:
            self.watch.draw_kline(code)
            self.watch.draw_indicatrix(rule)
        elif self.list.currentRow() == 1:
            self.choose.re_render_all_plots(code)
            self.choose.re_draw_indicatrix(rule)
        elif self.list.currentRow() == 2:
            self.back_track.set_rule(rule)


class CustomWatchDialog(QDialog):
    set_custom_watch_signal = Signal(float, float)

    def __init__(self, parent=None):
        super(CustomWatchDialog, self).__init__(parent)
        self.setWindowModality(Qt.WindowModal)

        double_validator = QDoubleValidator()
        self.up_label = QLabel('上位价')
        self.up_input = QLineEdit()
        self.up_input.setValidator(double_validator)
        self.down_label = QLabel('下位价')
        self.down_input = QLineEdit()
        self.down_input.setValidator(double_validator)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_form_box = QFormLayout()
        main_form_box.addRow(self.up_label, self.up_input)
        main_form_box.addRow(self.down_label, self.down_input)
        main_form_box.addRow(self.btn_cancel, self.btn_ok)
        self.setLayout(main_form_box)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.on_ok)

    def on_ok(self):
        up = float(self.up_input.text())
        down = float(self.down_input.text())
        self.set_custom_watch_signal.emit(up, down)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = Nav()
    w.show()
    sys.exit(app.exec_())
