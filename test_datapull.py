import requests
import config
import pandas as pd
#import talib as ta
import matplotlib.pyplot as plt
import pandas_ta as pta
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots

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

# Price and volume data
z = pd.DataFrame(data.get('candles'))
z['Volume'] = z.get('volume')
z['Price'] = z.get('close')

times = []
for epoch in z.get('datetime'):
	times.append(datetime.fromtimestamp(epoch/1000))

# INDICATORS
# for the EMA, we can use .ewm from the dataframe object
# this line makes an 18 day moving average1
z['8EMA'] = z['close'].ewm(span=8, adjust=False).mean()
z['21EMA'] = z['close'].ewm(span=21, adjust=False).mean()
z['MACD'] = z['21EMA'] - z['8EMA']
z['MACDsignal'] = z['MACD'].ewm(span=9, adjust=False).mean()
z['RSI'] = pta.rsi(z['close'], length = 14)

z['zeroindex'] = 0
z['30rsi'] = 30
z['70rsi'] = 70

#  - - - - - PLOTTING - - - - -

# setting up subplots

fig = make_subplots(rows=4, cols=1)

# plotting the candlesticks
candlesticks = go.Figure(data=go.Candlestick(x=times,
                open=z.get('open'),
                high=z.get('high'),
                low=z.get('low'),
                close=z.get('close'),
				increasing_line_color= 'green', decreasing_line_color= 'red'))
fig.append_trace(candlesticks, row=1, col=1)

# plotting the macd
macd = go.Figure(px.line(z, x=times, y=['MACD', 'MACDsignal', 'zeroindex'], color_discrete_map={'MACD':'blue','MACDsignal':'gold'}))
fig.append_trace(macd, row=2, col=1)

# plotting 8 step and 21 step ema
ema = go.Figure(px.line(z, x=times, y=['8EMA', '21EMA'], color_discrete_map={'8EMA':'blue','21EMA':'gold'}))
fig.append_trace(ema, row=3, col=1)

# plotting RSI
rsi = go.Figure(px.line(z, x=times, y=['RSI', '30rsi', '70rsi']))
fig.append_trace(rsi, row=4, col=1)

fig.update_layout(height=600, width=600)
fig.show()

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