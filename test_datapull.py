import requests
import config
import pandas as pd
#import talib as ta
import matplotlib.pyplot as plt
import pandas_ta as pta
import numpy as np

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

# Price and volume data
x = pd.DataFrame(data.get('candles'))
x['Volume'] = x.get('volume')

# INDICATORS
# for the EMA, we can use .ewm from the dataframe object
# this line makes an 18 day moving average1
x['8EMA'] = x['close'].ewm(span=8, adjust=False).mean()
x['21EMA'] = x['close'].ewm(span=21, adjust=False).mean()
x['MACD'] = x['21EMA'] - x['8EMA']
x['MACDsignal'] = x['MACD'].ewm(span=9, adjust=False).mean()
x['RSI'] = pta.rsi(x['close'], length = 14)

print(x)



x['zeroindex'] = 0
x['30rsi'] = 30
x['70rsi'] = 70


x['RSIsignal'] = 0
x['MACDcross'] = 0

def macd_range( m,upper, lower):
	if m < upper and m > lower:
		return True

# In the future keep track of whether there is a position open
# cant sell if you have nothing

for pos,i in enumerate(x['RSI']):
	if i < 30:
		x['RSIsignal'][pos] = 1
	elif i > 70:
		x['RSIsignal'][pos] = -1
	else:
		x['RSIsignal'][pos] = 0

# Clean this up later
#Find where MACD is between -.5 and .5 AND RSI is > 70 || < 30
# Get the slope of MACD to determine whether to buy or sell
for pos,m in enumerate(x['MACD']):
	#in_range = macd_range(m, .1,-.1)
	#compare the lines between days, and determine when they would cross
	if m > -.1 and m < .1:
		x['MACDcross'][pos] = 1
	else:
		x['MACDcross'][pos] = 0

# Printing out Plots

fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(10,7))

x['MACD'].plot(title='MACD', label='macd', color='red', ax = axes[0])
x['MACDsignal'].plot(label='macdsignal', color='green',ax = axes[0])
x['zeroindex'].plot(color='black', ax = axes[0])

x['8EMA'].plot(title='EMA', label='8ema', color='blue', ax = axes[1])
x['21EMA'].plot(title='EMA', label='21ema', color='orange', ax = axes[1])

#x['close'].plot(title='RSIsignal', label='price', color='purple', ax = axes[1,2])

x['RSI'].plot(title='RSI', label='RSI', color='purple', ax = axes[2])
x['30rsi'].plot(label='30', color='black', linestyle='dashed', ax = axes[2])
x['70rsi'].plot(label='70', color='black', linestyle='dashed', ax=axes[2])

x['RSIsignal'].plot(title='RSIsignal', label = 'RSIsignal', color='green', ax = axes[3])
x['MACDcross'].plot(title='MACDcross', label = 'MACDcross', color='green', ax = axes[4])

# Working on displaying Volume
#x['Volume'].plot.bar(width = .2, color = 'green', ax = axes[5])
plt.show()
