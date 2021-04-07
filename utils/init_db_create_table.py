from db.models import AStockIndex, AStockDayLine, AStockYJBB, AStockZCFZB, \
    AStockLRB, AStockXJLLB
from db.ops import create_table

# TODO: Due to the '_MEIPASS' attr, I don't know how to make it runnable
#  under its current directory.  I have to put this script into the ROOT
#  directory to run it.

create_table(AStockIndex)
create_table(AStockDayLine)
create_table(AStockYJBB)
create_table(AStockZCFZB)
create_table(AStockLRB)
create_table(AStockXJLLB)
