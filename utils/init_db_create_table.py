from db.models import AStockInfo, AStockDayLine, AStockProfitData, \
    AStockOperationData, AStockGrowthData, AStockBalanceData, \
    AStockCashFlowData, AStockDupontData
from db.ops import create_table

# TODO: Due to the '_MEIPASS' attr, I don't know how to make it runnable
#  under its current directory.  I have to put this script into the ROOT
#  directory to run it.

create_table(AStockInfo)
create_table(AStockDayLine)
create_table(AStockProfitData)
create_table(AStockOperationData)
create_table(AStockGrowthData)
create_table(AStockBalanceData)
create_table(AStockCashFlowData)
create_table(AStockDupontData)
