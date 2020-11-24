from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='cyber',
    ext_modules=cythonize(
        ['./apis/k_charts.py', './apis/realtime_price.py',
         './apis/stock_info.py',
         './conf/conf.py', './conf/version.py',
         './db/db.py', './db/models.py', './db/ops.py',
         './pages/about.py', './pages/backtrack.py', './pages/choose.py',
         './pages/config.py', './pages/license.py', './pages/main_win.py',
         './pages/nav.py', './pages/watch.py',
         './rules/base.py', './rules/boll.py', './rules/custom_watch.py',
         './rules/dual_ma.py', './rules/kdj.py', './rules/macd.py',
         './rules/rsi.py', './rules/turtle.py', './rules/volume_increase.py',
         './rules/wr.py',
         './utils/candlestick.py', './utils/custom_add_dialog.py'
         ])
)
