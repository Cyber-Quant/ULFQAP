from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='cyber',
    ext_modules=cythonize(
        ['./apis/k_charts.py', './apis/realtime_price.py',
         './apis/stock_info.py',
         './conf/conf.py', './conf/version.py',
         './db/db.py', './db/models.py', './db/ops.py',
         './pages/about.py', './pages/backtest.py', './pages/choose.py',
         './pages/config.py', './pages/license.py', './pages/main_win.py',
         './pages/nav.py', './pages/watch.py',
         './strategies/common.py', './strategies/boll.py',
         './strategies/custom_watch.py', './strategies/dual_ma.py',
         './strategies/kdj.py', './strategies/macd.py', './strategies/rsi.py',
         './strategies/volume_increase.py', './strategies/wr.py',
         './utils/candlestick.py', './utils/custom_add_dialog.py'
         ])
)
