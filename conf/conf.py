import sys

from pathlib import Path

bundle_dir = Path(getattr(sys, '_MEIPASS', Path.cwd()))
db_path = bundle_dir / 'user_data/quant.db'

logo_svg_path = bundle_dir / 'media/logo.svg'
logo_png_path = bundle_dir / 'media/logo.png'
logo_icon_path = bundle_dir / 'media/logo.ico'
logo_icns_path = bundle_dir / 'media/logo.icns'

global_config_path = bundle_dir / 'user_data/conf.json'

backtest_config_path = bundle_dir / 'user_data/backtest.json'
custom_watch_config_path = bundle_dir / 'user_data/custom_watch.json'
factor_pool_config_path = bundle_dir / 'user_data/factor_pool.json'

factor_strategies_config_path = bundle_dir / 'user_data/strategies/factor'
shape_strategies_config_path = bundle_dir / 'user_data/strategies/shape'

licence_html_path = bundle_dir / 'media/license.html'

statement_update_flag_file = bundle_dir / 'user_data/stat_up_flag.json'

DEFAULT_K_LIMIT = 250

DAY_K_READY_HOUR = 17
DAY_K_READY_MINUTE = 30
MINUTE_K_READY_HOUR = 20
MINUTE_K_READY_MINUTE = 30

FIRST_DAY_YEAR = 2007
FIRST_DAY_MONTH = 1
FIRST_DAY_DAY = 1
FIRST_DAY = str(FIRST_DAY_YEAR) + '-' + str(FIRST_DAY_MONTH) + '-' + str(
    FIRST_DAY_DAY)
