from db.models import AStockInfo, AStockDayLine
from db.ops import create_table

create_table(AStockInfo)
create_table(AStockDayLine)
