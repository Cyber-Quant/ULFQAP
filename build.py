from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='cyber',
    ext_modules=cythonize(
        ['./apis/code_index.py', './apis/finance.py',
         './apis/k_charts.py', './apis/realtime_price.py',
         './apis/statements.py',
         './conf/conf.py', './conf/version.py',
         './db/db.py', './db/models.py', './db/ops.py',
         './pages/about.py', './pages/backtest.py', './pages/choose.py',
         './pages/config.py', './pages/license.py', './pages/main_win.py',
         './pages/nav.py', './pages/pool.py', './pages/watch.py',
         './strategies/boll.py', './strategies/bottom_break_up.py',
         './strategies/common.py', './strategies/custom_watch.py',
         './strategies/kdj.py', './strategies/lucky_duck_head.py',
         './strategies/macd.py', './strategies/mcst.py',
         './strategies/percent_change.py', './strategies/rsi.py',
         './strategies/triple_golden_cross.py', './strategies/turn_over.py',
         './strategies/value.py', './strategies/volume_increase.py',
         './strategies/wr.py',
         './utils/candlestick.py', './utils/custom_add_dialog.py',
         './widgets/plots.py'
         ])
)
