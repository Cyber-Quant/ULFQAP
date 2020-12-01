from db.models import AStockInfo, AStockDayLine
from db.ops import create_table

# TODO: Due to the '_MEIPASS' attr, I don't know how to make it runnable
#  under its current directory.  I have to put this script into the ROOT
#  directory to run it.

create_table(AStockInfo)
create_table(AStockDayLine)
