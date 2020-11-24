from db.models import AStockInfo, AStockDayLine, AStockWeekLine, AStockMonthLine
from db.ops import create_table

create_table(AStockInfo)
create_table(AStockDayLine)
create_table(AStockWeekLine)
create_table(AStockMonthLine)
