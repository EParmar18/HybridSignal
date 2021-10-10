import requests
import config
import pandas as pd
#import talib as ta
import matplotlib.pyplot as plt
import pandas_ta as pta

#daily prices endpoint

#define endpoint
ticker = 'GOOG'
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker);

#define payload
payload = {'apikey':config.client_id,
	   'periodType':'day',
	   'frequencyType':'minute',
	   'frequency':'1',
	   'period':'2',
#	   'endDate':'1633721305000',
#	   'startDate':'1554535854123',
	   'needExtendedHours':'true'}

#send the request
content = requests.get(url = endpoint, params = payload)

# convert the json string to a dictionary
data = content.json()

# print(data.get('candles'))

# put price data of payload parameters in DF
x = pd.DataFrame(data.get('candles'))

# for the EMA, we can use .ewm from the dataframe object
# this line makes an 18 day moving average1
x['8EMA'] = x['close'].ewm(span=8, adjust=False).mean()
x['21EMA'] = x['close'].ewm(span=21, adjust=False).mean()

x['MACD'] = x['21EMA'] - x['8EMA']
x['MACDsignal'] = x['MACD'].ewm(span=9, adjust=False).mean()

x['RSI'] = pta.rsi(x['close'], length = 14)

print(x)

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10,7))

x['zeroindex'] = 0
x['30rsi'] = 30
x['70rsi'] = 70

x['MACD'].plot(title='MACD', label='macd', color='red', ax = axes[0])
x['MACDsignal'].plot(label='macdsignal', color='green',ax = axes[0])
x['zeroindex'].plot(color='black', ax = axes[0])

x['8EMA'].plot(title='SIGNAL', label='8ema', color='blue', ax = axes[1])
x['21EMA'].plot(title='SIGNAL', label='21ema', color='orange', ax = axes[1])
#x['close'].plot(title='SIGNAL', label='price', color='purple', ax = axes[1])

x['RSI'].plot(title='RSI', label='RSI', color='purple', ax = axes[2])
x['30rsi'].plot(label='30', color='black', linestyle='dashed', ax = axes[2])
x['70rsi'].plot(label='70', color='black', linestyle='dashed', ax=axes[2])


plt.show()
