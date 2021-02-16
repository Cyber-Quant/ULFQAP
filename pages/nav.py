import json

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from conf.conf import apply_strategies_config_path, fav_stocks_config_path, \
    custom_watch_config_path, bundle_dir
from pages.backtest import Backtest
from pages.choose import Choose
from pages.config import Config
from pages.pool import Pool
from pages.watch import Watch
from strategies.boll import BOLLConfig, BOLLInfo
from strategies.dual_line import DualLineConfig, DualLineInfo
from strategies.kdj import KDJConfig, KDJInfo
from strategies.macd import MACDConfig, MACDInfo
from strategies.rsi import RSIConfig, RSIInfo
from strategies.stairs import StairsConfig, StairsInfo
from strategies.triple_golden_cross import TripleGoldenCrossConfig, \
    TripleGoldenCrossInfo
from strategies.turtle import TurtleConfig, TurtleInfo
from strategies.wr import WRConfig, WRInfo
from strategies.volume_increase import VolumeIncreaseConfig, VolumeIncreaseInfo
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

        if not apply_strategies_config_path.exists():
            self.apply_strategies = []
        else:
            with open(apply_strategies_config_path, 'r', encoding='utf-8') as f:
                self.apply_strategies = json.load(f)

        if not custom_watch_config_path.exists():
            self.custom_watch = []
        else:
            with open(custom_watch_config_path, 'r', encoding='utf-8') as f:
                self.custom_watch = json.load(f)

        # NEW STRATEGIES #
        self.dual_line_info = DualLineInfo()
        self.stairs_info = StairsInfo()
        self.triple_golden_cross_info = TripleGoldenCrossInfo()
        self.turtle_info = TurtleInfo()
        self.volume_increase_info = VolumeIncreaseInfo()
        self.wr_info = WRInfo()
        self.boll_info = BOLLInfo()
        self.macd_info = MACDInfo()
        self.kdj_info = KDJInfo()
        self.rsi_info = RSIInfo()
        self.strategies = [
            {
                'name': self.dual_line_info.name,
                'choose': 'Y' if self.dual_line_info.choose_flag else 'N',
                'watch': 'Y' if self.dual_line_info.watch_flag else 'N'
            },
            {
                'name': self.stairs_info.name,
                'choose': 'Y' if self.stairs_info.choose_flag else 'N',
                'watch': 'Y' if self.stairs_info.watch_flag else 'N'
            },
            {
                'name': self.triple_golden_cross_info.name,
                'choose': 'Y' if self.triple_golden_cross_info.choose_flag else 'N',
                'watch': 'Y' if self.triple_golden_cross_info.watch_flag else 'N'
            },
            {
                'name': self.turtle_info.name,
                'choose': 'Y' if self.turtle_info.choose_flag else 'N',
                'watch': 'Y' if self.turtle_info.watch_flag else 'N'
            },
            {
                'name': self.volume_increase_info.name,
                'choose': 'Y' if self.volume_increase_info.choose_flag else 'N',
                'watch': 'Y' if self.volume_increase_info.watch_flag else 'N'
            },
            {
                'name': self.wr_info.name,
                'choose': 'Y' if self.wr_info.choose_flag else 'N',
                'watch': 'Y' if self.wr_info.watch_flag else 'N'
            },
            {
                'name': self.boll_info.name,
                'choose': 'Y' if self.boll_info.choose_flag else 'N',
                'watch': 'Y' if self.boll_info.watch_flag else 'N'
            },
            {
                'name': self.macd_info.name,
                'choose': 'Y' if self.macd_info.choose_flag else 'N',
                'watch': 'Y' if self.macd_info.watch_flag else 'N'
            },
            {
                'name': self.kdj_info.name,
                'choose': 'Y' if self.kdj_info.choose_flag else 'N',
                'watch': 'Y' if self.kdj_info.watch_flag else 'N'
            },
            {
                'name': self.rsi_info.name,
                'choose': 'Y' if self.rsi_info.choose_flag else 'N',
                'watch': 'Y' if self.rsi_info.watch_flag else 'N'
            }
        ]

        self.watch = None
        self.choose = None
        self.pool = None
        self.backtest = None
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

        self.strategy_fav_widget = QWidget()
        strategy_fav_v_box = QVBoxLayout()
        strategy_fav_v_box.setContentsMargins(0, 10, 0, 10)
        self.strategy_table = QTableWidget()
        headers = ['应用', '策略', '选股', '盯盘']
        self.strategy_table.setColumnCount(len(headers))
        self.strategy_table.setHorizontalHeaderLabels(headers)
        self.strategy_table.setColumnWidth(0, 37)
        self.strategy_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self.strategy_table.setColumnWidth(2, 30)
        self.strategy_table.setColumnWidth(3, 30)
        self.strategy_table.verticalHeader().setVisible(False)
        self.strategy_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.strategy_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.strategy_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.strategy_table.setSortingEnabled(True)
        self.strategy_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.strategy_table.customContextMenuRequested.connect(
            self.open_strategy_table_menu)
        self.strategy_table.itemSelectionChanged.connect(
            self.on_strategy_table_row_changed)
        self.strategy_table.setRowCount(len(self.strategies))

        for i, strategy in enumerate(self.strategies):
            check = QCheckBox(parent=self.strategy_table)
            if self.strategies[i]['name'] in self.apply_strategies:
                check.setChecked(True)
            check.clicked.connect(self.update_watch_strategies)
            self.strategy_table.setCellWidget(i, 0, check)
            item_name = QTableWidgetItem(self.strategies[i]['name'])
            item_name.setTextAlignment(Qt.AlignCenter)
            self.strategy_table.setItem(i, 1, item_name)
            item_choose = QTableWidgetItem(self.strategies[i]['choose'])
            item_choose.setTextAlignment(Qt.AlignCenter)
            self.strategy_table.setItem(i, 2, item_choose)
            item_watch = QTableWidgetItem(self.strategies[i]['watch'])
            item_watch.setTextAlignment(Qt.AlignCenter)
            self.strategy_table.setItem(i, 3, item_watch)

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

        strategy_fav_v_box.addWidget(self.strategy_table)
        strategy_fav_v_box.addWidget(self.fav_table)
        self.strategy_fav_widget.setLayout(strategy_fav_v_box)
        self.strategy_fav_widget.setMinimumWidth(220)
        self.strategy_fav_widget.setMaximumWidth(250)
        main_h_box.addWidget(self.strategy_fav_widget)

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

        pool_widget = get_item_widget('股池', bundle_dir / 'media/pool.svg')
        pool_item = QListWidgetItem()
        pool_item.setSizeHint(QSize(150, 70))
        self.list.addItem(pool_item)
        self.list.setItemWidget(pool_item, pool_widget)

        test_widget = get_item_widget('回测', bundle_dir / 'media/backtest.svg')
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

        self.pool = Pool()
        self.stacked_window.addWidget(self.pool)

        self.backtest = Backtest()
        self.backtest.fav_stock_changed_signal.connect(
            self.on_refresh_fav_table)
        self.stacked_window.addWidget(self.backtest)

        self.config = Config()
        self.stacked_window.addWidget(self.config)

    def update_watch_strategies(self):
        check = self.sender()
        i = self.strategy_table.indexAt(check.pos()).row()
        if check.isChecked():
            self.apply_strategies.append(self.strategies[i]['name'])
        elif self.strategies[i]['name'] in self.apply_strategies:
            self.apply_strategies.remove(self.strategies[i]['name'])

        with open(apply_strategies_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.apply_strategies, f, indent=4, ensure_ascii=False)

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
        if name == self.dual_line_info.name:
            cfg_dlg = DualLineConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.stairs_info.name:
            cfg_dlg = StairsConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.triple_golden_cross_info.name:
            cfg_dlg = TripleGoldenCrossConfig(self)
            cfg_dlg.show()
            cfg_dlg.exec_()
        if name == self.turtle_info.name:
            cfg_dlg = TurtleConfig(self)
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
        if row == -1:
            return
        code = self.fav_table.item(row, 0).text()
        name = self.fav_table.item(row, 1).text()
        row = self.strategy_table.currentRow()
        if row != -1:
            strategy = self.strategy_table.item(row, 1).text()
        else:
            strategy = None
        if self.list.currentRow() == 0:
            self.watch.render_all_plots(code)
            self.watch.draw_indicators(strategy)
        elif self.list.currentRow() == 1:
            self.choose.re_render_all_plots(code)
            self.choose.draw_indicators(strategy)
        elif self.list.currentRow() == 2:
            self.pool.set_code(code, name)
        elif self.list.currentRow() == 3:
            self.backtest.set_code(code, name)

    def on_strategy_table_row_changed(self):
        row = self.strategy_table.currentRow()
        strategy = self.strategy_table.item(row, 1).text()
        row = self.fav_table.currentRow()
        if row == -1:
            return
        code = self.fav_table.item(row, 0).text()
        if self.list.currentRow() == 0:
            self.watch.render_all_plots(code)
            self.watch.draw_indicators(strategy)
        elif self.list.currentRow() == 1:
            self.choose.re_render_all_plots(code)
            self.choose.re_draw_indicators(strategy)
        elif self.list.currentRow() == 3:
            self.backtest.set_strategy(strategy)


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
