# nightTrader
Get email notifications with candlestick charts about the volatility of your stocks

## What is nightTrader?
**nightTrader** is an email alert system that notifies users when the prices of their stocks increase or decrease by a certian amount

## How to use nightTrader
To use **nightTrader**, email night.trader.system@gmail.com

The email should have the stock ticker in the subject box

**nightTrader** will email you the percentage that your stock changed by alongside a candlestick chart of your stock in the past 10 minutes whenever your stock makes a significant enough change
## Example
### Email to nightTrader: 

**Subject:** GCT

### nightTrader reply:

![stockemail](https://github.com/jamesmcaleer/nightTrader/assets/77809943/c635daa5-2c30-49ed-9d4f-a6d010a637ae)

## How it works
The _get_stock_data_ function is ran for every stock every 60 seconds

The percent change from the last 5 minutes is found

If this percent is greater than a given value, a candlestick chart of the stock from the past 10 minutes is sent to every user who is tracking that stock:

```python
def get_stock_data(stock):
   # get from 10 min ago to now
   end = dt.datetime.now()
   start = end - dt.timedelta(minutes=11)

   # get the data from yahoo over the time period in intervals of 1 minute
   yf.pdr_override()
   df = pdr.get_data_yahoo(stock.ticker, start=start, end=end, interval="1m")

   # get only the last 5 minutes of the stock, this will be used for finding the percent change
   info = df["Close"][5:10]
   min = info.min()
   max = info.max()
   # find the percent change in the last 5 minutes
   change = ((max - min) / min) * 100
   change = round(float(change), 2)

   # create the candlestick chart
   if change > 2: # 2 is the percent but this can change
       prefix = stock.ticker
       mpf.plot(df, type='candle', style='yahoo', savefig=prefix + ".png")
       image = prefix + ".png"
       send(stock, change, image, stock.emails.split())
```


