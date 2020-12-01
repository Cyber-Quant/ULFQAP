import sys

from pathlib import Path

bundle_dir = Path(getattr(sys, '_MEIPASS', Path.cwd()))
db_path = bundle_dir / 'user_data/quant.db'

global_config_path = bundle_dir / 'user_data/conf.json'
fav_stocks_config_path = bundle_dir / 'user_data/fav_stocks.json'
apply_strategies_config_path = bundle_dir / 'user_data/apply_strategies.json'
custom_watch_config_path = bundle_dir / 'user_data/custom_watch.json'
strategies_config_path = bundle_dir / 'user_data/strategies'

licence_html_path = bundle_dir / 'media/license.html'

DEFAULT_K_LIMIT = 250

DAY_K_READY_HOUR = 17
DAY_K_READY_MINUTE = 30
MINUTE_K_READY_HOUR = 20
MINUTE_K_READY_MINUTE = 30

FIRST_DAY = '1990-12-19'
