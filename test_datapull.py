import requests
import config
import pandas as pd
#import talib as ta
import matplotlib.pyplot as plt
import pandas_ta as pta
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

#daily prices endpoint

#define endpoint
ticker = 'AAPL'
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(ticker);

#define payload
payload = {'apikey':config.client_id,
	   'periodType':'day',
	   'frequencyType':'minute',
	   'frequency':'1',
	   'period':'1',
#	   'endDate':'1633721305000',
#	   'startDate':'1554535854123',
	   'needExtendedHours':'true'}


#send the request
content = requests.get(url = endpoint, params = payload)

# convert the json string to a dictionary
data = content.json()

# print(data.get('candles'))


# Price and volume data
z = pd.DataFrame(data.get('candles'))
z['Volume'] = z.get('volume')
z['Price'] = z.get('close')

times = []
for epoch in z.get('datetime'):
	times.append(datetime.fromtimestamp(epoch/1000))

fig = go.Figure(data=[go.Candlestick(x=times,
                open=z.get('open'),
                high=z.get('high'),
                low=z.get('low'),
                close=z.get('close'),
				increasing_line_color= 'cyan', decreasing_line_color= 'gray'))])

fig.show()

# INDICATORS
# for the EMA, we can use .ewm from the dataframe object
# this line makes an 18 day moving average1
z['8EMA'] = z['close'].ewm(span=8, adjust=False).mean()
z['21EMA'] = z['close'].ewm(span=21, adjust=False).mean()
z['MACD'] = z['21EMA'] - z['8EMA']
z['MACDsignal'] = z['MACD'].ewm(span=9, adjust=False).mean()
z['RSI'] = pta.rsi(z['close'], length = 14)

print(z)



z['zeroindex'] = 0
z['30rsi'] = 30
z['70rsi'] = 70


z['RSIsignal'] = 0
z['MACDcross'] = 0

def macd_range( m,upper, lower):
	if m < upper and m > lower:
		return True

# In the future keep track of whether there is a position open
# cant sell if you have nothing

for pos,i in enumerate(z['RSI']):
	if i < 30:
		z['RSIsignal'][pos] = 1
	elif i > 70:
		z['RSIsignal'][pos] = -1
	else:
		z['RSIsignal'][pos] = 0

# Clean this up later
#Find where MACD is between -.5 and .5 AND RSI is > 70 || < 30
# Get the slope of MACD to determine whether to buy or sell
for pos,m in enumerate(z['MACD']):
	#in_range = macd_range(m, .1,-.1)
	#compare the lines between days, and determine when they would cross
	if m > -.1 and m < .1:
		z['MACDcross'][pos] = 1
	else:
		z['MACDcross'][pos] = 0

# Printing out Plots

fig, axes = plt.subplots(nrows=7, ncols=1, figsize=(20,15))

z['MACD'].plot(title='MACD', label='macd', color='red', ax = axes[0])
z['MACDsignal'].plot(label='macdsignal', color='green',ax = axes[0])
z['zeroindex'].plot(color='black', ax = axes[0])

z['8EMA'].plot(title='EMA', label='8ema', color='blue', ax = axes[1])
z['21EMA'].plot(title='EMA', label='21ema', color='orange', ax = axes[1])

#z['close'].plot(title='RSIsignal', label='price', color='purple', ax = axes[1,2])

z['RSI'].plot(title='RSI', label='RSI', color='purple', ax = axes[2])
z['30rsi'].plot(label='30', color='black', linestyle='dashed', ax = axes[2])
z['70rsi'].plot(label='70', color='black', linestyle='dashed', ax=axes[2])

z['RSIsignal'].plot(title='RSIsignal', label = 'RSIsignal', color='green', ax = axes[3])
z['MACDcross'].plot(title='MACDcross', label = 'MACDcross', color='green', ax = axes[4])

z['Price'].plot(title='Price', label = 'Price', color = 'blue', ax = axes[5])

rsiSet = z['RSIsignal'].copy(deep = True)

num = range(len(z['Price']))
for index ,i in enumerate(z['RSIsignal']):
	if i  == -1:
		# Plot a sell dot	
		rsiSet[index] = z['Price'][index]
		#plt.scatter(z = num[index], y = rsiSet[index], color = 'red',marker = 'o')
		
	elif i == 1:
		# Plot a buy dot
		rsiSet[index] = z['Price'][index]
		#plt.scatter(z = num[index], y = rsiSet[index], color = 'green',marker = 'o',)
		
		# 0 0 0 0 0 0 144 0 0 0 0 0 0 

# Working on displaying Volume
#z['Volume'].plot.bar(width = .2, color = 'green', ax = axes[5])

plt.show()