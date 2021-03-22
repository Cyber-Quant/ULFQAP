import pyqtgraph as pg

from pyqtgraph.dockarea import *
from qtpy.QtWidgets import *

from strategies.common import get_latest_batch_data
from strategies.alligator import Alligator
from strategies.boll import BOLL
from strategies.bottom_break_up import BottomBreakUp
from strategies.kdj import KDJ
from strategies.lucky_duck_head import LuckyDuckHead
from strategies.macd import MACD
from strategies.mcst import MCST
from strategies.rsi import RSI
from strategies.triple_golden_cross import TripleGoldenCross
from strategies.wr import WR
from utils.candlestick import CandlestickItem


class Plots(QWidget):
    def __init__(self, parent=None):
        super(Plots, self).__init__(parent)
        self.setWindowTitle('Plots')

        self.current_kline_code = None
        self.current_indicator_name = None

        self.kline_data = []
        self.k_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.k_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.vol_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.vol_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.macd_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.macd_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.kdj_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.kdj_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.rsi_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.rsi_h_line = pg.InfiniteLine(angle=0, movable=False)
        self.wr_v_line = pg.InfiniteLine(angle=90, movable=False)
        self.wr_h_line = pg.InfiniteLine(angle=0, movable=False)

        self.plt_area = DockArea()

        self.dock_k = Dock('K')
        self.k_plt = pg.PlotWidget(enableMenu=False)
        self.k_plt.plotItem.setMouseEnabled(y=False)
        self.k_plt.hideAxis('bottom')
        self.info_label = pg.TextItem()
        self.plt_area.addDock(self.dock_k, 'bottom')
        self.dock_k.addWidget(self.k_plt)

        index_height = 70

        self.dock_vol = Dock('Volume')
        self.vol_plt = pg.PlotWidget(enableMenu=False)
        self.vol_plt.plotItem.setMouseEnabled(y=False)
        self.vol_plt.hideAxis('bottom')
        self.vol_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_vol, 'bottom', self.dock_k)
        self.dock_vol.addWidget(self.vol_plt)
        self.dock_vol.setFixedHeight(index_height)

        self.dock_macd = Dock('MACD')
        self.macd_plt = pg.PlotWidget(enableMenu=False)
        self.macd_plt.plotItem.setMouseEnabled(y=False)
        self.macd_plt.hideAxis('bottom')
        self.macd_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_macd, 'bottom', self.dock_vol)
        self.dock_macd.addWidget(self.macd_plt)
        self.dock_macd.setFixedHeight(index_height)

        self.dock_kdj = Dock('KDJ')
        self.kdj_plt = pg.PlotWidget(enableMenu=False)
        self.kdj_plt.plotItem.setMouseEnabled(y=False)
        self.kdj_plt.hideAxis('bottom')
        self.kdj_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_kdj, 'bottom', self.dock_macd)
        self.dock_kdj.addWidget(self.kdj_plt)
        self.dock_kdj.setFixedHeight(index_height)

        self.dock_rsi = Dock('RSI')
        self.rsi_plt = pg.PlotWidget(enableMenu=False)
        self.rsi_plt.plotItem.setMouseEnabled(y=False)
        self.rsi_plt.hideAxis('bottom')
        self.rsi_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_rsi, 'bottom', self.dock_kdj)
        self.dock_rsi.addWidget(self.rsi_plt)
        self.dock_rsi.setFixedHeight(index_height)

        self.dock_wr = Dock('WR')
        self.wr_plt = pg.PlotWidget(enableMenu=False)
        self.wr_plt.plotItem.setMouseEnabled(y=False)
        self.wr_plt.hideAxis('bottom')
        self.wr_plt.setXLink(self.k_plt)
        self.plt_area.addDock(self.dock_wr, 'bottom', self.dock_rsi)
        self.dock_wr.addWidget(self.wr_plt)
        self.dock_wr.setFixedHeight(index_height)

        self.k_move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved,
                                          rateLimit=60,
                                          slot=self.kline_emit_info)
        self.vol_move_slot = pg.SignalProxy(self.vol_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.vol_emit_info)
        self.macd_move_slot = pg.SignalProxy(
            self.macd_plt.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.macd_emit_info)
        self.kdj_move_slot = pg.SignalProxy(self.kdj_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.kdj_emit_info)
        self.rsi_move_slot = pg.SignalProxy(self.rsi_plt.scene().sigMouseMoved,
                                            rateLimit=60,
                                            slot=self.rsi_emit_info)
        self.wr_move_slot = pg.SignalProxy(self.wr_plt.scene().sigMouseMoved,
                                           rateLimit=60,
                                           slot=self.wr_emit_info)

    def re_render_all_plots(self, code):
        if code is None:
            return
        else:
            self.current_kline_code = code
            self.render_all_plots(code)

    def render_all_plots(self, code):
        self.current_kline_code = code
        if self.current_kline_code is None:
            return

        self.kline_data = []
        date, _open, close, high, low, volume, amount, turn, pct_chg, \
        ma_price, ma_volume = \
            get_latest_batch_data(code, period=self.current_kline_period)

        _macd = MACD()
        macd, dif, dea = _macd.calc_macd(close)

        _kdj = KDJ()
        k, d, j = _kdj.calc_kdj(close, high, low)

        _rsi = RSI()
        fast_rsi, slow_rsi = _rsi.calc_rsi(close)

        _wr = WR()
        wr = _wr.calc_williams(close, high, low)

        for i in range(len(close)):
            obj = {
                'id': i,
                'date': date[i],
                'code': code,
                'open': _open[i],
                'close': close[i],
                'high': high[i],
                'low': low[i],
                'volume': volume[i],
                'amount': amount[i],
                'ma_price': ma_price[i],
                'ma_volume': ma_volume[i],
                'dif': dif[i],
                'dea': dea[i],
                'macd': macd[i],
                'k': k[i],
                'd': d[i],
                'j': j[i],
                'slow_rsi': slow_rsi[i],
                'fast_rsi': fast_rsi[i],
                'wr': wr[i]
            }
            self.kline_data.append(obj)
        self._render_all_plots()

    def _render_all_plots(self):
        self.k_plt.plotItem.clear()

        if self.current_kline_period == '1':
            self.vol_plt.plotItem.clear()
            self.kdj_plt.plotItem.clear()
            self.macd_plt.plotItem.clear()
            self.rsi_plt.plotItem.clear()
            self.wr_plt.plotItem.clear()

            prices = []
            volumes = []
            for item in self.kline_data:
                prices.append(item['close'])
                volumes.append(item['volume'])
            y_min = min(prices)
            y_max = max(prices)
            axis = zip(range(len(self.times)), self.times)
            self.k_plt.getAxis('bottom').setTicks([axis])
            self.k_plt.plot(prices, pen='y')
            self.k_plt.showGrid(True, True)
            self.k_plt.setYRange(y_min, y_max)
            self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
            self.k_plt.addItem(self.k_h_line, ignoreBounds=True)
            self.k_plt.addItem(self.info_label)
        else:
            uni_index = []

            k_data = []
            lows = []
            highs = []
            k_axis = []

            volumes = []

            difs = []
            deas = []
            red_macds = []
            green_macds = []
            red_macds_index = []
            green_macds_index = []

            k = []
            d = []
            j = []

            slow_rsis = []
            fast_rsis = []

            wrs = []

            for item in self.kline_data:
                uni_index.append(item['id'])

                (i, _open, close, high, low) = (
                    item['id'], item['open'], item['close'], item['high'],
                    item['low'])
                k_data.append((i, _open, close, high, low))
                lows.append(item['low'])
                highs.append(item['high'])
                k_axis.append(item['date'])

                volumes.append(item['volume'])

                difs.append(item['dif'])
                deas.append(item['dea'])
                if item['macd'] >= 0:
                    red_macds.append(item['macd'])
                    red_macds_index.append(item['id'])
                else:
                    green_macds.append(item['macd'])
                    green_macds_index.append(item['id'])

                k.append(item['k'])
                d.append(item['d'])
                j.append(item['j'])

                slow_rsis.append(item['slow_rsi'])
                fast_rsis.append(item['fast_rsi'])

                wrs.append(item['wr'])

            if self.current_kline_period != '60':
                ma_prices = []
                ma_volumes = []
                for item in self.kline_data:
                    ma_prices.append(item['ma_price'])
                    ma_volumes.append(item['ma_volume'])
                self.k_plt.plot(ma_prices, pen='y')

            axis = zip(range(len(k_axis)), k_axis)
            item = CandlestickItem(k_data)
            y_min = min(lows)
            # y_min = 0
            y_max = max(highs)
            self.k_plt.getAxis('bottom').setTicks([axis])
            self.k_plt.addItem(item)
            self.k_plt.showGrid(True, True)
            self.k_plt.setYRange(y_min, y_max)
            self.k_plt.addItem(self.k_v_line, ignoreBounds=True)
            self.k_plt.addItem(self.k_h_line, ignoreBounds=True)
            self.k_plt.addItem(self.info_label)

            uni_width = (k_data[1][0] - k_data[0][0]) / 3.0

            self.vol_plt.plotItem.clear()
            volume_bar = pg.BarGraphItem(x=uni_index, height=volumes,
                                         width=uni_width,
                                         pen='b')
            self.vol_plt.addItem(volume_bar)
            self.vol_plt.addItem(self.vol_v_line, ignoreBounds=True)
            self.vol_plt.addItem(self.vol_h_line, ignoreBounds=True)

            self.macd_plt.plotItem.clear()
            red_macd_bar = pg.BarGraphItem(x=red_macds_index, height=red_macds,
                                           width=uni_width,
                                           pen='r')
            green_macd_bar = pg.BarGraphItem(x=green_macds_index,
                                             height=green_macds,
                                             width=uni_width,
                                             pen='g')
            self.macd_plt.addItem(red_macd_bar)
            self.macd_plt.addItem(green_macd_bar)
            self.macd_plt.plot(difs, pen='w')
            self.macd_plt.plot(deas, pen='y')
            self.macd_plt.addItem(self.macd_v_line, ignoreBounds=True)
            self.macd_plt.addItem(self.macd_h_line, ignoreBounds=True)

            self.kdj_plt.plotItem.clear()
            self.kdj_plt.plot(k, pen='r')
            self.kdj_plt.plot(d, pen='b')
            self.kdj_plt.plot(j, pen='y')
            self.kdj_plt.addItem(self.kdj_v_line, ignoreBounds=True)
            self.kdj_plt.addItem(self.kdj_h_line, ignoreBounds=True)

            self.rsi_plt.plotItem.clear()
            self.rsi_plt.plot(slow_rsis, pen='b')
            self.rsi_plt.plot(fast_rsis, pen='y')
            self.rsi_plt.addItem(self.rsi_v_line, ignoreBounds=True)
            self.rsi_plt.addItem(self.rsi_h_line, ignoreBounds=True)

            self.wr_plt.plotItem.clear()
            self.wr_plt.plot(wrs, pen='w')
            self.wr_plt.addItem(self.wr_v_line, ignoreBounds=True)
            self.wr_plt.addItem(self.wr_h_line, ignoreBounds=True)

    def _emit_info(self, mouse_point):
        index = int(mouse_point.x())
        if -1 < index < len(self.kline_data):
            if self.current_kline_period == 'd':
                volume = int(self.kline_data[index]['volume'] / 100)
            else:
                volume = self.kline_data[index]['volume']
            self.info_label.setHtml(
                "<p style='color:white'><strong>日期：{0}</strong></p>"
                "<p style='color:white'>开：{1}</p>"
                "<p style='color:white'>高：{2}</p>"
                "<p style='color:white'>低：{3}</p>"
                "<p style='color:white'>收：{4}</p>"
                "<p style='color:white'>量：{5}</p>".format(
                    self.kline_data[index]['date'],
                    self.kline_data[index]['open'],
                    self.kline_data[index]['high'],
                    self.kline_data[index]['low'],
                    self.kline_data[index]['close'],
                    volume))
            self.info_label.setPos(mouse_point.x(), mouse_point.y())
            self.kline_info_signal.emit(self.kline_data[index]['date'],
                                        self.kline_data[index]['open'],
                                        self.kline_data[index]['close'],
                                        self.kline_data[index]['high'],
                                        self.kline_data[index]['low'],
                                        volume)

    def kline_emit_info(self, event):
        pos = event[0]
        if self.k_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.k_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.k_v_line.setPos(mouse_point.x())
            self.k_h_line.setPos(mouse_point.y())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def vol_emit_info(self, event):
        pos = event[0]
        if self.vol_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.vol_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.vol_v_line.setPos(mouse_point.x())
            self.vol_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def macd_emit_info(self, event):
        pos = event[0]
        if self.macd_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.macd_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.macd_v_line.setPos(mouse_point.x())
            self.macd_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def kdj_emit_info(self, event):
        pos = event[0]
        if self.kdj_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.kdj_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.kdj_v_line.setPos(mouse_point.x())
            self.kdj_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def rsi_emit_info(self, event):
        pos = event[0]
        if self.rsi_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.rsi_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.rsi_v_line.setPos(mouse_point.x())
            self.rsi_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.wr_v_line.setPos(mouse_point.x())

    def wr_emit_info(self, event):
        pos = event[0]
        if self.wr_plt.sceneBoundingRect().contains(pos):
            mouse_point = self.wr_plt.plotItem.vb.mapSceneToView(pos)
            self._emit_info(mouse_point)

            self.wr_v_line.setPos(mouse_point.x())
            self.wr_h_line.setPos(mouse_point.y())
            self.k_v_line.setPos(mouse_point.x())
            self.vol_v_line.setPos(mouse_point.x())
            self.macd_v_line.setPos(mouse_point.x())
            self.kdj_v_line.setPos(mouse_point.x())
            self.rsi_v_line.setPos(mouse_point.x())

    def re_draw_indicators(self, name):
        self.current_indicator_name = name
        if self.current_kline_code is None:
            return
        self.draw_indicators(name)

    def draw_indicators(self, strategy_name):
        self.current_indicator_name = strategy_name
        if self.current_kline_code is None or \
                self.current_indicator_name is None:
            return

        closes = []
        highs = []
        lows = []
        volumes = []
        amount = []
        for item in self.kline_data:
            closes.append(item['close'])
            highs.append(item['high'])
            lows.append(item['low'])
            volumes.append(item['volume'])
            amount.append(item['amount'])

        # NEW STRATEGIES #
        if self.current_indicator_name == self.alligator_info.name:
            alligator = Alligator()
            ups = alligator.calc_batch_ups(closes)
            middles = alligator.calc_batch_middles(closes)
            downs = alligator.calc_batch_downs(closes)
            k_data = [ups, middles, downs]
            k_pen_colors = ['g', 'r', 'b']
            vol_data = []
            vol_pen_colors = []
        elif self.current_indicator_name == self.boll_info.name:
            boll = BOLL()
            ups = boll.calc_batch_up(closes)
            middles = boll.calc_batch_middle(closes)
            downs = boll.calc_batch_down(closes)
            k_data = [ups, middles, downs]
            k_pen_colors = ['r', 'w', 'y']
            vol_data = []
            vol_pen_colors = []
        elif self.current_indicator_name == self.bottom_break_up_info.name:
            bottom_break_up = BottomBreakUp()
            ma_5 = bottom_break_up.calc_5_ma(closes)
            ma_10 = bottom_break_up.calc_10_ma(closes)
            ma_20 = bottom_break_up.calc_20_ma(closes)
            ma_30 = bottom_break_up.calc_30_ma(closes)
            ma_60 = bottom_break_up.calc_60_ma(closes)
            k_data = [ma_5, ma_10, ma_20, ma_30, ma_60]
            k_pen_colors = ['r', 'y', 'w', 'b', 'g']
            mav_5 = bottom_break_up.calc_mav(volumes, 5)
            mav_10 = bottom_break_up.calc_mav(volumes, 10)
            vol_data = [mav_5, mav_10]
            vol_pen_colors = ['r', 'y']
        elif self.current_indicator_name == self.lucky_duck_head_info.name:
            lucky_duck_head = LuckyDuckHead()
            fast_ma = lucky_duck_head.calc_fast_ma(closes)
            slow_ma = lucky_duck_head.calc_slow_ma(closes)
            base_ma = lucky_duck_head.calc_base_ma(closes)
            k_data = [fast_ma, slow_ma, base_ma]
            k_pen_colors = ['r', 'y', 'w']
            fast_mav = lucky_duck_head.calc_fast_mav(volumes)
            slow_mav = lucky_duck_head.calc_slow_mav(volumes)
            vol_data = [fast_mav, slow_mav]
            vol_pen_colors = ['r', 'y']
        elif self.current_indicator_name == self.mcst_info.name:
            mcst = MCST()
            _mcst = mcst.calc_batch_mcst(volumes, amount,
                                         self.current_kline_code)
            k_data = [_mcst]
            k_pen_colors = ['y']
            vol_data = []
            vol_pen_colors = []
        elif self.current_indicator_name == self.triple_golden_cross_info.name:
            triple_golden_cross = TripleGoldenCross()
            fast_ma = triple_golden_cross.calc_fast_ma(closes)
            slow_ma = triple_golden_cross.calc_slow_ma(closes)
            season_ma = triple_golden_cross.calc_season_ma_indicator(
                closes)
            k_data = [fast_ma, slow_ma, season_ma]
            k_pen_colors = ['r', 'y', 'w']
            fast_mav = triple_golden_cross.calc_fast_mav(volumes)
            slow_mav = triple_golden_cross.calc_slow_mav(volumes)
            vol_data = [fast_mav, slow_mav]
            vol_pen_colors = ['r', 'y']
        else:
            k_data = []
            k_pen_colors = []
            vol_data = []
            vol_pen_colors = []
        self.draw_k_indicators(k_data, k_pen_colors)
        self.draw_vol_indicators(vol_data, vol_pen_colors)

    def draw_k_indicators(self, data, pen_colors):
        for i, _data in enumerate(data):
            self.draw_k_indicator(_data, pen_colors[i])

    def draw_k_indicator(self, data, pen_color):
        self.k_plt.plot(data, pen=pen_color)

    def draw_vol_indicators(self, data, pen_colors):
        for i, _data in enumerate(data):
            self.draw_vol_indicator(_data, pen_colors[i])

    def draw_vol_indicator(self, data, pen_color):
        self.vol_plt.plot(data, pen=pen_color)
