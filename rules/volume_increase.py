import json
import numpy as np

from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from conf.conf import rules_config_path
from rules.base import get_latest_n_desc_data


class VolumeIncreaseInfo:
    def __init__(self):
        self.name = '成交量放大'
        self.desc = '''
        成交量放大
        前20(m)日的交易量平均值，最后一天成交量是平均值的2(n)倍。
        成交量放大，认为上涨/下跌是真实信号。
        '''
        self.choose_flag = True
        self.watch_flag = False


class VolumeIncreaseChoose(QThread):
    progress_signal = Signal(int, str, str)

    def __init__(self, stocks, parent=None):
        super(VolumeIncreaseChoose, self).__init__(parent)
        self.codes = []
        self.names = []
        for stock in stocks:
            self.codes.append(stock['code'])
            self.names.append(stock['name'])

        self.config_path = rules_config_path.joinpath('volume_increase.json')
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.m = data['m']
                self.n = data['n']
        else:
            self.m = 20
            self.n = 2

    def _get_volumes(self, code):
        rows = get_latest_n_desc_data(code, self.m)
        data = []
        for row in rows:
            data.append(row.volume)
        return data

    def choose(self, code):
        volumes = self._get_volumes(code)
        _volume = volumes[0]
        _volumes = volumes[1:]
        volume_avg = np.mean(_volumes)
        if _volume <= _volumes[0]:
            return False
        if float(_volume / volume_avg) >= self.n:
            return True
        else:
            return False

    def run(self):
        step = int(len(self.codes) / 100) + 1
        i = 0
        j = 0
        for code in self.codes:
            i += 1
            ret = self.choose(code)
            if not ret:
                continue
            self.progress_signal.emit(j, code, self.names[i - 1])
            if i % step == 0:
                j += 1
        self.progress_signal.emit(100, '', '')


class VolumeIncreaseConfig(QDialog):
    def __init__(self, parent=None):
        super(VolumeIncreaseConfig, self).__init__(parent)
        self.setWindowTitle('成交量放大策略配置')
        self.setWindowModality(Qt.WindowModal)

        self.config_path = rules_config_path.joinpath('volume_increase.json')
        self.info = VolumeIncreaseInfo()

        reg = QRegExp('[0-9]+$')
        validator = QRegExpValidator()
        validator.setRegExp(reg)

        reg = QRegExp('[0-9.]+$')
        float_validator = QRegExpValidator()
        float_validator.setRegExp(reg)

        main_f_box = QFormLayout()
        self.desc = QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setText(self.info.desc)
        self.m_label = QLabel('周期m')
        self.m_input = QLineEdit()
        self.m_input.setValidator(validator)
        self.n_label = QLabel('倍数n')
        self.n_input = QLineEdit()
        self.n_input.setValidator(float_validator)
        self.btn_cancel = QPushButton('取消')
        self.btn_ok = QPushButton('确定')
        main_f_box.addRow(self.desc)
        main_f_box.addRow(self.m_label, self.m_input)
        main_f_box.addRow(self.n_label, self.n_input)
        main_f_box.addRow(self.k_label, self.k_input)
        main_f_box.addRow(self.btn_cancel, self.btn_ok)
        self.setLayout(main_f_box)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.ok)

    def ok(self):
        if not self.config_path.exists():
            data = {}
        else:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        data['m'] = int(self.m_input.text())
        data['n'] = float(self.n_input.text())
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = VolumeIncreaseConfig()
    main.show()

    sys.exit(app.exec_())
