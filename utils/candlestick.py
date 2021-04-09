import pyqtgraph as pg

from PySide2.QtCore import *
from PySide2.QtGui import *


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)

        self.data = data
        self.pic = None

        self.draw_candlesticks()

    def draw_candlesticks(self):
        self.pic = QPicture()
        painter = QPainter(self.pic)
        width = (self.data[1][0] - self.data[0][0]) / 3.0
        green_pen = pg.mkPen(color=(0, 255, 255, 255), width=width * 2)
        green_brush = pg.mkBrush((0, 255, 255, 255))
        red_pen = pg.mkPen(color=(255, 0, 0, 255), width=width * 2)
        red_brush = pg.mkBrush((255, 0, 0, 255))
        red_brush.setStyle(Qt.NoBrush)

        for (time, _open, _close, _high, _low) in self.data:
            pen, brush, p_max, p_min = (green_pen, green_brush, _open, _close) \
                if _open > _close else (red_pen, red_brush, _close, _open)
            painter.setPen(pen)
            painter.setBrush(brush)
            if _open == _close:
                painter.drawLine(QPointF(time - width, _open),
                                 QPointF(time + width, _close))
            else:
                painter.drawRect(
                    QRectF(time - width, _open, width * 2, _close - _open))

            if p_min > _low:
                painter.drawLine(QPointF(time, _low), QPointF(time, p_min))
            if _high > p_max:
                painter.drawLine(QPointF(time, p_max), QPointF(time, _high))

            # painter.drawLine(QPointF(time, _high), QPointF(time, _low))
            # painter.setBrush(pg.mkBrush('g' if _open > _close else 'r'))
            # painter.drawRect(
            #     QRectF(time - width, _open, width * 2, _close - _open))
        painter.end()

    def paint(self, painter, *args):
        painter.drawPicture(0, 0, self.pic)

    def boundingRect(self):
        return QRectF(self.pic.boundingRect())
