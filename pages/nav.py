from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from conf.conf import bundle_dir, logo_svg_path
from conf.version import RELEASE, name, channel, major, minor, fix
from pages.config import Config
from pages.factor import Factor
from pages.shape import Shape


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
        if channel == RELEASE:
            ver_info = 'v' + str(major) + '.' + str(minor) + '.' + str(
                fix)
        else:
            ver_info = 'v' + str(major) + '.' + str(minor) + '.' + str(
                fix) + '(' + channel + ')'
        self.setWindowTitle(name + ' --- ' + ver_info)
        icon = QIcon()
        self.setWindowIcon(QIcon(logo_svg_path.as_posix()))
        self.resize(1280, 768)

        self.factor = None
        self.shape = None
        self.config = None

        main_h_box = QHBoxLayout()
        main_h_box.setContentsMargins(0, 0, 0, 0)

        op_v_box = QVBoxLayout()
        op_v_box.setContentsMargins(0, 0, 0, 0)
        pe = QPalette()
        self.logo = QLabel()
        # self.logo.setScaledContents(True)
        self.logo.setAutoFillBackground(True)
        # pe.setColo(QPalette.Window, Qt.red)
        self.logo.setPalette(pe)
        self.logo.setFixedSize(50, 50)
        pic = QPixmap(logo_svg_path.as_posix()).scaled(50, 50)
        self.logo.setPixmap(pic)

        self.list = QListWidget()
        self.list.setFixedWidth(50)
        self.list.setFrameShape(QListWidget.NoFrame)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        op_v_box.addWidget(self.logo)
        op_v_box.addSpacing(7)
        op_v_box.addWidget(self.list)

        main_h_box.addLayout(op_v_box)

        self.stacked_window = QStackedWidget()
        main_h_box.addWidget(self.stacked_window)

        self.setLayout(main_h_box)

        self.init_nav_list()
        self.init_stacked_window()

        self.list.currentRowChanged.connect(self.stacked_window.setCurrentIndex)

    def init_nav_list(self):
        factor_widget = get_item_widget('因子', bundle_dir / 'media/factor.svg')
        factor_item = QListWidgetItem()
        factor_item.setSizeHint(QSize(150, 70))
        self.list.addItem(factor_item)
        self.list.setItemWidget(factor_item, factor_widget)

        shape_widget = get_item_widget('形态', bundle_dir / 'media/shape.svg')
        shape_item = QListWidgetItem()
        shape_item.setSizeHint(QSize(150, 70))
        self.list.addItem(shape_item)
        self.list.setItemWidget(shape_item, shape_widget)

        config_widget = get_item_widget('设置', bundle_dir / 'media/config.svg')
        config_item = QListWidgetItem()
        config_item.setSizeHint(QSize(150, 70))
        self.list.addItem(config_item)
        self.list.setItemWidget(config_item, config_widget)

        self.list.setCurrentItem(factor_item)

    def init_stacked_window(self):
        self.factor = Factor()
        self.stacked_window.addWidget(self.factor)

        self.shape = Shape()
        self.stacked_window.addWidget(self.shape)

        self.config = Config()
        self.stacked_window.addWidget(self.config)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = Nav()
    w.show()
    sys.exit(app.exec_())
