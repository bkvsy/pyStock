#!/usr/bin/python3
# Module with dataframe operations.
# -
# append to a dataframe a.append(pd.DataFrame({'close':99.99},index=[datetime.datetime.now()])
import pandas as pd
from scipy import signal
import numpy
from numpy import NaN

# Creates empty dataframe
def CreateEmptyDataFrame():
    return pd.DataFrame()

# Creates DataFrame line
def CreateHorizontalLine(indexes,startValue,endValue,allIndexes=False):
    data=pd.DataFrame()
    # Only start and begin
    if (allIndexes == False):
        data = data.append(pd.DataFrame({'value':startValue},index=[indexes[0]]))
        data = data.append(pd.DataFrame({'value':endValue},index=[indexes[-1]]))
    # All data
    else:
        N = len(indexes)
        alpha = (endValue-startValue)/N
        for i in range(len(indexes)):
            data = data.append(pd.DataFrame(
                {'value':alpha*i+startValue},
                index=[indexes[i]]))
    return data

# Creates DataFrame line
def CreateVerticalLine(index,startValue,endValue):
    data=pd.DataFrame()
    data = data.append(pd.DataFrame({'value':startValue},index=[index]))
    data = data.append(pd.DataFrame({'value':endValue},index=[index]))
    return data

# Creates DataFrame rect
def CreateRect(index1,value1,index2,value2):
    data=pd.DataFrame()
    data = data.append(pd.DataFrame({'value':value1},index=[index1]))
    data = data.append(pd.DataFrame({'value':value2},index=[index1]))
    data = data.append(pd.DataFrame({'value':value2},index=[index2]))
    data = data.append(pd.DataFrame({'value':value1},index=[index2]))
    data = data.append(pd.DataFrame({'value':value1},index=[index1]))
    return data

# Creation of moving average with specific window and shift
def CreateMovingAverage(data, window, shiftPeriods = 0):
    average = data.rolling(window=int(window),min_periods=1).mean()
    average.shift(periods=shiftPeriods)

    return average

# Creation of moving std with specific window and shift
def CreateMovingStd(data, window, shiftPeriods = 0):
    average = data.rolling(window=int(window),min_periods=1).std()
    average.shift(periods=shiftPeriods)

    return average

# Create data subset by value
def CreateSubsetByValues(inputData,valueMin,valueMax):
    subset=pd.DataFrame()

    for i in range(len(inputData.values)):
        if ((inputData.values[i]>=valueMin) and (inputData.values[i]<=valueMax)):
            subset = subset.append(pd.DataFrame({'value':inputData.values[i]},
                                                index=[inputData.index[i]]))

    return subset

# Create data subset by date
def GetSubsetByDates(inputData,start_date,end_date,fillna=True):
    subset=pd.DataFrame()

    for i in range(len(inputData.values)):
        if ((inputData.index[i]>=start_date) and (inputData.index[i]<=end_date)):
            subset = subset.append(pd.DataFrame({'close':inputData.values[i]},
                                                index=[inputData.index[i]]))

    return subset

# Reindex weekly data
def SetReindex(data,start_date,end_date,fillna=True):
    # Getting all weekdays between 01/01/2000 and 12/31/2016
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

    # How do we align the existing prices in adj_close with our new set of dates?
    # All we need to do is reindex close using all_weekdays as the new index
    data = data.reindex(all_weekdays)

    # Reindexing will insert missing values (NaN) for the dates that were not present
    # in the original set. To cope with this, we can fill the missing by replacing them
    # with the latest available price for each instrument.
    if (fillna == True):
        data = data.fillna(method='ffill')
        data = data.dropna()

    return data

# Calculate diff
def Diffrentiate(dataset):
    diff=numpy.diff(dataset).tolist()
    diff.append(0,0)
    return diff

# Find zeroes and zero cuts
def FindZeroes(data):
    zeroes=pd.DataFrame()

    signs = numpy.sign(data.values)
    for i in range(1,len(signs)):
        if (signs[i] != signs[i-1]):
            zeroes = zeroes.append(pd.DataFrame({'close':data.values[i]},index=[data.index[i]]))

    return zeroes

# Find both signals intersections
def FindIntersections(x,y):
    # For dataframes
    if type(y) is pd.DataFrame:
        diffrence=x.subtract(y)
    # for int or float values
    else:
        diffrence=x-y

    fromBottom=pd.DataFrame()
    fromTop=pd.DataFrame()

    signs = numpy.sign(diffrence.values)
    for i in range(1,len(signs)):
        # Bottom crossing
        if (signs[i] == 1) and (signs[i-1] == -1):
            fromBottom = fromBottom.append(pd.DataFrame({'value':x.values[i]},index=[diffrence.index[i]]))
        # Top crossing
        elif (signs[i] == -1) and (signs[i-1] == 1):
            fromTop = fromTop.append(pd.DataFrame({'value':x.values[i]},index=[diffrence.index[i]]))

    return fromBottom, fromTop

def FindMaxPeaks(data, n=7):
#     maxs = data.iloc[argrelextrema(data.data.values, np.greater_equal, order=n)[0]]['data']
    maxs = data.iloc[signal.argrelextrema(data.values, numpy.greater_equal, order=n)[0]]
    return maxs

def FindMinPeaks(data,n=7):
#     mins = data.iloc[argrelextrema(data.data.values, np.less_equal, order=n)[0]]['data']
    mins = data.iloc[signal.argrelextrema(data.values, numpy.less_equal, order=n)[0]]
    return mins

def FindPeaks(data, delta):
    maxs=pd.DataFrame()
    mins=pd.DataFrame()

    # Loop max iterations
    MaxLoopIteration=10
    # Loop iteration
    loopIteration = 0

    while ((loopIteration<MaxLoopIteration) and (maxs.empty or mins.empty)):
        # Algorithm data
        last_max = data.values[0]
        last_min = data.values[0]
        last_max_pos = 0
        last_min_pos = 0
        search_max = True

        # Algorithm loop - Find max/min in loop
        for i in range(len(data.values)):
            current = data.values[i]
            # Save last max
            if (current > last_max):
                last_max = current
                last_max_pos = i
            # Save last min
            if (current < last_min):
                last_min = current
                last_min_pos = i

            if (search_max == True):
                # Save last max value
                if (current < (last_max-delta)):
                    maxs = maxs.append(pd.DataFrame({'close':last_max},index=[data.index[last_max_pos]]))
                    #maxs.values[last_max_pos] = last_max
                    last_max = current
                    last_max_pos = i
                    search_max = False
            else:
                # Save last min value
                if (current > (last_min+delta)):
                    mins = mins.append(pd.DataFrame({'close':last_min},index=[data.index[last_min_pos]]))
                    last_min = current
                    last_min_pos = i
                    search_max = True
        # Adjust delta for another loop search if min/max not found
        delta = (delta*80)/100
        loopIteration+=1

    return mins, maxs

# Uptrend calculation is based on mins
def FindUptrends(data):
    uptrends=[]
    mins = FindMinPeaks(data)

    # Find rising series. Start from end
#     for i in range(len(data.values)):
    # Calculate regression line most fitting.
    # If some point is far away from line then drop it.
    # Add to data.
    return 0

# Downtrend calculation is based on maxs
def FindDowntrends(data):
    return 0