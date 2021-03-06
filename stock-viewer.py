#!/usr/bin/python3
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import pandas as pd
import sys, os, argparse
import datetime
import numpy
import copy
from filelock import Timeout, FileLock
from pandas_datareader import data
from numpy import NaN
from matplotlib import gridspec
from lib.CountryInfo import CountryInfo
from lib.DataOperations import *
from lib.Stock import *
from lib.StockData import *
from lib.ReportSignals import *
from lib.TimeInterval import *
from lib.assets import *

# Create plot figures file
def PlotSave(fig):
    global graphsCreated
    filePath=outputFilepath+str(fig.number)+outputExtension
    plt.figure(fig.number)
    plt.savefig(filePath)
    graphsCreated.append(filePath)
    print(filePath) 

# remove all created plots
def PlotsRemove():
    global graphsCreated
    for filepath in graphsCreated:
        os.system("rm -rf %s" % (filepath))

# Save reports to file. Append text.
def ReportBaseSave(filepath):
    global outputFilename
    global args
    global closePrice
    global closePriceTotal
    global volume
    global volumeTotal
    
    lastPrice      = closePriceTotal.values[0]
    maxPrice       = closePriceTotal.values.max()
    minPrice       = closePriceTotal.values.min()
    maxWindowPrice = closePrice.values.max()
    minWindowPrice = closePrice.values.min()
    lastPriceAsPercentOfMaxPrice = (lastPrice*100)/maxPrice
    growthChance    = (maxPrice*100)/lastPrice - 100
    lostChance      = 100-(minPrice*100)/lastPrice
    # Volume statistics
    volumeSubset    = GetSubsetByDates(volume, last2Weeks, today)
    volumeAvgChange = volumeSubset.median()

    lock             = FileLock(filepath+".lock", timeout=lockTimeout)
    lock.acquire()
    with open(filepath, 'a+') as f:
        # Write statistics
        f.write("# Report for %s.\n" % (args.stockCode))
        f.write("1. Price **%2.2f%s** - (**%u%%** of history, \
                 growth chance <span style='color:green'>+%u%%</span>, \
                 lost chance <span style='color:red'>-%u%%</span>)\n" % 
                (lastPrice,info.GetCurrency(),lastPriceAsPercentOfMaxPrice,growthChance,lostChance))
        f.write("    * Current - **%2.2f%s - %2.2f%s**\n" % (minWindowPrice,info.GetCurrency(),maxWindowPrice,info.GetCurrency()))
        f.write("    * History - **%2.2f%s - %2.2f%s**\n" % (minPrice,info.GetCurrency(),maxPrice,info.GetCurrency()))
        f.write("    * Volume chng. (2 weeks) - med. **%2.2f**, max **+%2.2f**, min **%2.2f**\n" % 
                (volumeSubset.median(), volumeSubset.max(),volumeSubset.min()))
        f.write("    * **%2.2f**%% return rate for last 7 days.\n" % (GetReturnRates(closePrice, 7)))
        f.write("\n")
        
        # Assets
        stockData.ReportAssets(f)
        f.write("\n")
        
        # Insert all created graphs
        f.write("## Graphs\n\n")
        for path in graphsCreated:
            f.write("![Graph](%s)\n\n" % (os.path.basename(path)))
        f.write("\n")

    lock.release()

# Const objects
# #####################################################
lockTimeout = 5*60
executionIntervals = [ "monthly", "weekly", "daily"]
reportFile="plots/report.md"
plotsPath="plots/"
outputExtension=".png"

# Varaables
# #####################################################

# Arguments and config
# #####################################################
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--stockCode", type=str, required=True, help="Stock name code")
parser.add_argument("-d", "--beginDate", type=str, required=False, help="Begin date")
parser.add_argument("-Y", "--lastYear", action='store_true', required=False, help="Last Year")
parser.add_argument("-6M", "--last6Months", action='store_true', required=False, help="Last 6 Months")
parser.add_argument("-3M", "--last3Months", action='store_true', required=False, help="Last 3 Months")
parser.add_argument("-M", "--lastMonth", action='store_true', required=False, help="Last Month")
parser.add_argument("-W", "--lastWeek", action='store_true', required=False, help="Last Week")
parser.add_argument("-g", "--plotToFile", action='store_true', required=False, help="Plot to file")
parser.add_argument("-r", "--reports", action='store_true', required=False, help="Generate extra reports")
parser.add_argument("-ri", "--reportsInterval", type=str, required=False, help="Interval of extra reports")
args = parser.parse_args()

#Assert
if (not args.stockCode):
    print("No stockCode!")
    sys.exit(1)

# Assert
if (args.reportsInterval is not None):
    if (args.reportsInterval not in executionIntervals):
        print("Wrong execution interval!")
        sys.exit(1)

# Create Country Info
info = CountryInfo(args.stockCode)
        
# Use non-interactive backend when plot to file used
if (args.plotToFile):
    import matplotlib
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Dates
today       = datetime.datetime.now()
lastYear    = datetime.datetime.now() - datetime.timedelta(days=365)
last6Months = datetime.datetime.now() - datetime.timedelta(days=30*6)
lastMonth   = datetime.datetime.now() - datetime.timedelta(days=30)
last2Weeks  = datetime.datetime.now() - datetime.timedelta(days=14)
lastWeek    = datetime.datetime.now() - datetime.timedelta(days=7)
## End date
end_date    = today.strftime("%Y-%m-%d")
## Start date
if (args.beginDate):
    start_date  = args.beginDate
else:
    start_date  = '2010-01-01'
# Check last year
if (args.lastYear):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=365)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last 6 month
if (args.last6Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30*6)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last 3 month
if (args.last3Months):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30*3)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last month
if (args.lastMonth):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=30)
    start_date  =  tmpDate.strftime("%Y-%m-%d")
# Check last Week
if (args.lastWeek):
    tmpDate = datetime.datetime.now() - datetime.timedelta(days=7)
    start_date  =  tmpDate.strftime("%Y-%m-%d")


# Dynamic variables
# #####################################################
outputFilename=args.stockCode+"_"+end_date+"_"
outputFilepath=plotsPath+outputFilename
graphsCreated=[]
reportSignals = CreateReportSignals()
executionInterval="weekly"

# Update - execution Interval
if (args.reportsInterval is not None):
    executionInterval = args.reportsInterval
    
reportSignals.SetBeginTimestamp(GetIntervalBegin(executionInterval))
reportSignals.SetStockCode(args.stockCode)


# 1. Get DATA from URL
# #####################################################
stockAssets = StockAssets()
stockData   = StockData(args.stockCode, start_date, end_date)
stockData.SetAssets(stockAssets)
stockData.SetCurrencySymbol(info.GetCurrency())

# Get Close price and average
closePriceTotal  = stockData.GetAllData('Close')
closePrice       = stockData.GetData('Close')
alligator        = CreateWilliamsAlligator(closePrice)
macd             = CreateMACD(closePrice)
rsi              = CreateRSI(closePrice)
cci              = CreateCCI(stockData.GetData('High'),stockData.GetData('Low'),stockData.GetData('Close'))
bollinger        = CreateBollinger(closePrice)
atr              = CreateATR(stockData.GetData('High'),stockData.GetData('Low'),stockData.GetData('Close'))
dmi              = CreateDMI(stockData.GetData('High'),stockData.GetData('Low'),atr.GetAtr())
if (stockData.hasVolume()):
    mfi        = CreateMoneyFlowIndex(stockData.GetData('High'),stockData.GetData('Low'),stockData.GetData('Close'),stockData.GetData('Volume'),info)
    cmf        = CreateChaikinMoneyFlow(stockData.GetData('High'),stockData.GetData('Low'),stockData.GetData('Close'),stockData.GetData('Volume'),info)

# Export all signals to report
alligator.ExportSignals(reportSignals)
macd.ExportSignals(reportSignals)
rsi.ExportSignals(reportSignals)
bollinger.ExportSignals(reportSignals)

# Find max and mins
PriceRange=closePrice.max()-closePrice.min()
print("ClosePrice Pk-Pk change %2.2f.\n" % (PriceRange))
mins, maxs       = FindPeaks(closePrice, PriceRange/10)

# Volume
obvTotal    = stockData.GetAllData('OBV')
volumeTotal = stockData.GetAllData('Volume')
volume      = stockData.GetData('Volume')
obv         = stockData.GetData('OBV')


# PLOTS
# #####################################################
fig = plt.figure(figsize=(16.0, 9.0))


# Price
# #####################################################
plot1=plt.subplot(221)
alligator.Plot()
stockData.Plot()
stockData.PlotAssets()
# plt.plot(maxs.index,maxs,'go', label="Maxs")
# plt.plot(mins.index,mins,'ro', label="Mins")
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.grid()
plt.title("Price, OBV, MoneyOnMarket")
plt.legend(loc='upper left')

# OBV
# #####################################################
if (stockData.hasVolume()):
    plot1A = plot1.twinx()
    plot1A.plot(obv.index, obv, "-.", linewidth=1.2, label="OBV", color="blue")
    plot1A.legend(loc='upper left')
    plot1A.tick_params(axis='y', labelcolor='tab:blue')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))

# Money on market
# #####################################################
if (stockData.hasVolume()):
    plot1B = plot1.twinx()
    stockData.PlotMoneyOnMarket(plot1B)
    plot1B.tick_params(axis='y', labelcolor='tab:red')
    plt.legend(loc='upper left')


# Price - ALL
# #####################################################
plot2=plt.subplot(222)
stockData.PlotAll()
stockData.PlotAllAssets()
rect = CreateRect(datetime.datetime.strptime(start_date, "%Y-%m-%d"), 
                          stockData.GetAllData('Close').max(), 
                          datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                          stockData.GetAllData('Close').min())
plt.plot(rect.index, rect, "--", linewidth=1.2, color="#FF0000")
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.grid()
plt.title("Price, OBV, MoneyOnMarket - alltime")
plt.legend(loc='upper left')

# OBV - ALL
# #####################################################
if (stockData.hasVolume()):
    plot2A = plot2.twinx()
    plot2A.plot(obvTotal.index, obvTotal, label="OBV total")
    plot2A.legend(loc='upper left')
    plot2A.tick_params(axis='y', labelcolor='tab:blue')

# Money on market - ALL
# #####################################################
if (stockData.hasVolume()):
    plot2B = plot2.twinx()
    stockData.PlotMoneyOnMarketAll(plot2B)
    plot2B.tick_params(axis='y', labelcolor='tab:red')
    plt.legend(loc='upper left')

# Plot to file
if (args.plotToFile):
    PlotSave(fig)

### 
fig = plt.figure(figsize=(16.0, 9.0))

# Total close price
Rows=6
gs = gridspec.GridSpec(Rows, 1)
plot5=plt.subplot(gs[0:4])
stockData.PlotCandle(plot5)
stockData.PlotAssets()
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.title("Price and oscillators - period")
plt.legend(loc='upper left')
plt.minorticks_on()
plt.grid(b=True, which='major', axis='both',color='k')
plt.grid(b=True, which='minor', axis='both')
plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

# MACD
plot6=plt.subplot(gs[Rows-2], sharex=plot5)
macd.Plot()
macd.Histogram()
plt.ylabel('Value')
plt.grid()
plt.legend(loc='upper left')
plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

# RSI
plot8=plt.subplot(gs[Rows-1], sharex=plot5)
PlotRSI(rsi)
plt.ylabel('RSI')
plt.grid()
plt.legend(loc='upper left')
plt.xticks(rotation=90)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

### FIG 3
fig = plt.figure(figsize=(16.0, 9.0))

# Bollinger with candleplot
Rows=6
gs = gridspec.GridSpec(Rows, 1)
plot9=plt.subplot(gs[0:4])
stockData.PlotCandle(plot9)
stockData.PlotAssets()
bollinger.Plot()
plt.ylabel('Price (%s)' % (info.GetCurrency()))
plt.title("Price candlestick")
plt.legend(loc='upper left')
plt.minorticks_on()
plt.grid(b=True, which='major', axis='both',color='k')
plt.grid(b=True, which='minor', axis='both')
plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

# ATR
plot10=plt.subplot(gs[Rows-2],sharex=plot9)
# atr.Plot()
dmi.Plot()
plt.legend(loc='upper left')
plt.grid()
plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

# CCI
plot11=plt.subplot(gs[Rows-1],sharex=plot9)
cci.Plot()
plt.legend(loc='upper left')
plt.grid()
plt.xticks(rotation=90)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
#bollinger.PlotAbsDeviation()
# plt.minorticks_on()
# plt.grid(b=True, which='major', axis='both',color='k')
# plt.grid(b=True, which='minor', axis='both')

# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

if (stockData.hasVolume()):
    ### FIG 4
    fig = plt.figure(figsize=(16.0, 9.0))

    # Create rows
    Rows=6
    gs = gridspec.GridSpec(Rows, 1)
    plot9=plt.subplot(gs[0:4])
    # Bollinger with candleplot
    stockData.PlotCandle(plot9)
    stockData.PlotAssets()
    bollinger.Plot()
    plt.ylabel('Price (%s)' % (info.GetCurrency()))
    plt.title("Price candlestick")
    plt.legend(loc='upper left')
    plt.minorticks_on()
    plt.grid(b=True, which='major', axis='both',color='k')
    plt.grid(b=True, which='minor', axis='both')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
    plot9A = plot9.twinx()
    stockData.PlotMoneyOnMarket(plot9A)
    plot9.tick_params(axis='y', labelcolor='tab:red')
    plt.ylabel('Money on the market (%s)' % (info.GetCurrency()))
    plt.legend(loc='upper left')

    # CMF
    plot10=plt.subplot(gs[Rows-2],sharex=plot9)
#     cmf.PlotChaikinMoneyFlow()
    cmf.PlotChaikinOscillator()    
    plt.legend(loc='upper left')
    plt.grid()
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

    # MFI
    plot11=plt.subplot(gs[Rows-1],sharex=plot9)
    mfi.Plot()
    plt.legend(loc='upper left')
    plt.grid()

# Plot to file or show
if (args.plotToFile):
    PlotSave(fig)

# Create reports
if (args.reports):
    reportAllSignalTypes=False

    # If there are opened assets then report all signals
    if (len(stockAssets.GetAssetsForStockCode(args.stockCode,onlyOpened=True)) != 0):
        reportAllSignalTypes=True

    # Daily report
    if (executionInterval=="daily"):
        reportSignals.Report(reportFile,reportAllSignalTypes)
        
        # If signals reported
        if (reportSignals.reportedAnything == True):
            with open(reportFile, 'a+') as f:
                stockData.Report(f,executionInterval)
        # remove plots if nothing reported
        else:
            PlotsRemove()
    # Weekly report
    else:
        ReportBaseSave(reportFile)
        reportSignals.Report(reportFile,reportAllSignalTypes)

# Show all plots
if (not args.plotToFile):
    plt.show()

