pyStock - repository of stock analyze, alarm and follow tools.
-------------
pyStock is a bunch of tools used for stock market analyze, follow, and alarms.
* stock-alarms - tool for setting stock alarms and notifiyng user about alarms.
* stock-viewer - tool for generating stock plots and text reports for given stock code. Diffrent plot options, volume, MACD, Williams indicator or RSI.
* stock-viewer-manager - tool manager which can send emails with stock reports, generates reports and plots using stock-viewer. Configurable via json settings files.

!! **Please fork and contribute! Contributors needed to develop project!** Merge requests with yout features welcomed !!

# Installation 
(Linux) To install all commands and systemd timers and services run script.
```
./install.sh
```

(Other OS) No installation tool provided.

## Emails sending

Emails from stock-manager are send through linux command `mutt`. Please install this command and configure it with your local 
email server or with your email mailbox. You can use install & configuration script from here 
[Link to .sh script from github](https://github.com/folkien/scripts/blob/master/packages/ubuntu-packages/ssmtp-gmail.sh)

# Usage

## Stock viewer.

Features :
* Generates plots,
    * Close price
    * Volume
* Oscillators
    * MACD & MACD Histogram
    * RSI
    * CCI
    * Williams alligator
    * Bollinger
* Save plots to files \*.png
* Generates/Appends report.md with some usefull informations,


```bash
usage: stock-viewer.py [-h] -n STOCKCODE [-d BEGINDATE] [-a AVERAGEDAYS] [-Y]
                       [-6M] [-M] [-W] [-g] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -n STOCKCODE, --stockCode STOCKCODE
                        Stock name code
  -d BEGINDATE, --beginDate BEGINDATE
                        Begin date
  -a AVERAGEDAYS, --averageDays AVERAGEDAYS
                        Day to calc mean
  -Y, --lastYear        Last Year
  -6M, --last6Months    Last 6 Months
  -M, --lastMonth       Last Month
  -W, --lastWeek        Last Week
  -g, --plotToFile      Plot to file
  -r, --reports         Generate extra reports
```

Plot Apple last 6M to file
```bash
./stock-viewer.py -n AAPL.US -6M -g
```

![image](doc/AAPL.US_1.png)
![image](doc/AAPL.US_2.png)
![image](doc/AAPL.US_3.png)

Last year of google with markdown reports into report.md
```bash
./stock-viewer.py -n GOOG.US -Y -r
```
![image](doc/GOOG.US_1.png)
![image](doc/GOOG.US_2.png)
![image](doc/GOOG.US_3.png)

Markdown report
```markdown
# Report for GOOG.us.
1. Price **1455.84zl** - (**97%** of history,                  growth chance <span style='color:green'>+2%</span>,                  lost chance <span style='color:red'>-66%</span>)
    * Current - **1036.23zl - 1486.65zl**
    * History - **492.55zl - 1486.65zl**
    * Volume chng. (2 weeks) - med. **1345387.50**, max **+2396215.00**, min **-1784644.00**


# Report for GOOG.us.
1. Price **1455.84zl** - (**97%** of history,                  growth chance <span style='color:green'>+2%</span>,                  lost chance <span style='color:red'>-66%</span>)
    * Current - **1036.23zl - 1486.65zl**
    * History - **492.55zl - 1486.65zl**
    * Volume chng. (2 weeks) - med. **1345387.50**, max **+2396215.00**, min **-1784644.00**

![Graph](GOOG.us_2020-02-01_1.png)
![Graph](GOOG.us_2020-02-01_2.png)
```

Example CD Projekt Red plot
```bash
 ./stock-viewer.py -n CDR.pl -6M -g
```

![CDPR image](doc/CDR.pl_1.png)
![CDPR image](doc/CDR.pl_2.png)
![CDPR image](doc/CDR.pl_3.png)


## Stock manager

Features :
* Generates plots(via stoc-viewer) for all configured stock codes
* Generates report for all configured stock codes with extra HTML informations about news,
* Sends emails to cofnigured recipents

```bash
usage: stock-viewer-manager.py [-h] [-a] [-d] [-e] [-s] [-ar ADDRECIPIENT]
                               [-an ARGUMENTS] [-au URL]

optional arguments:
  -h, --help            show this help message and exit
  -a, --add             Adds given
  -d, --delete          Remove
  -e, --execute         Execute
  -s, --show            Print
  -ar ADDRECIPIENT, --addRecipient ADDRECIPIENT
                        Add email recipient
  -an ARGUMENTS, --arguments ARGUMENTS
                        Arguments
  -au URL, --url URL    Bankier URL
```

## Stock alarms

```bash
usage: stock-alarms.py [-h] [-a] [-d] [-c] [-p] [-n STOCKCODE]
                       [-r REFERENCEPRICE] [-t TYPE] [-v VALUE] [-W]

optional arguments:
  -h, --help            show this help message and exit
  -a, --addAlarm        Adds given alarm
  -d, --deleteAlarm     Removes alarm
  -c, --checkAlarms     Check all alarms
  -p, --printAlarms     Print all alarms
  -n STOCKCODE, --stockCode STOCKCODE
  -r REFERENCEPRICE, --referencePrice REFERENCEPRICE
  -t TYPE, --type TYPE
  -v VALUE, --value VALUE
  -W, --lastWeek        Last Week
```


# Known Issues

# Problem with pandas_datareader
There was a problem with pandas_datareader
https://stackoverflow.com/questions/53097523/importing-data-from-stooq-with-pandas-datareader-returns-empty-dataframe-in-pyth

Problem was solved in new pandas version. Recommeneded to use newest version. With newest version `country codes` after stock code works. 
Example of polish CDPR
```bash
./stock-viewer.py -n CDR.pl -Y
```
or USA google alphabet
```bash
./stock-viewer.py -n GOOG.us -Y
```

# TODO - for developers

## TODO Viewer
- MoneyFlow as separated plot with MF index and TRIX,
- Add colors background bollinger,
- Add levels of wsparcia based on STD consolidations,
- Add MACD Convergence-Divergence add,
- Add RSI Convergence-Divergence
- Add trend lines for max/mins peaks,
* Algorytm wyszukiwania maximów oraz minimów
* Wykrycie ogólnych trendów na bazie maximów oraz minmów, kolorowanie tła pod wykresem.
    https://openwritings.net/pg/python/python-find-peaks-and-valleys-chart-using-scipysignalargrelextrema
* Rysowani lini trendu w zakresach trendu z poprzedniego punktu za pomocą algorytmu z 
    https://stackoverflow.com/questions/43769906/how-to-calculate-the-trendline-for-stock-price
- ADD trend power factor,
- Read assets and show on plot,
TESTS :
- test and extend MACD + report info,
- test and extend RSI + report info,

## TODO Simulator
- Create simulator,
- Add strategy 10%,

## TODO Manager
- config .json z aktywami,

## TODO Alarmy : 
- aktywny i nieaktywne alarmy,
- pokazywanie alarmów,
- Wysyłanie emaili,
- Sprawdzanie najnowszych raportów dla inwestorów,
- Monitorowanie trendów oraz alarmy z trendów,

# Bibliography
* https://www.edukacjagieldowa.pl/gieldowe-abc/analiza-techniczna/
* https://money.stackexchange.com/questions/tagged/stocks
* https://www.investopedia.com/terms/m/macd.asp
* https://en.wikipedia.org/wiki/MACD
* https://en.wikipedia.org/wiki/Relative_strength_index
* https://www.investopedia.com/terms/r/rsi.asp
