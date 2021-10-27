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
from scipy.signal import find_peaks
import dash
from dash import Dash, dcc, html, Input, Output


pd.options.mode.chained_assignment = None  # default='warn'
#daily prices endpoint

#Dash app creation

app = Dash(__name__)

# DATA
#-----------------------------------------------------------------------------------------------------------------
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

# APP Layout
#-----------------------------------------------------------------------------------------------------------------

app.layout = html.Div([

	html.H1("Hybrid Signal: Finacial Indicator Project", style={'text-align': 'center'}),

	dcc.Dropdown(id="slct_stock",
				options=[
					{"label": "Apple", "value": 1},
					{"label": "Google", "value": 2},
					{"label": "Tesla", "value": 3},
					{"label": "Microsoft", "value": 4}],
				multi=False,
				value=1,
				style={'width': "40%"}
				),

	html.Div(id='output_container', children = []),
	html.Br(),

	dcc.Graph(id='stock_graph', figure={})

]) 

@app.callback(
	[Output(component_id='output_container', component_property='children'),
	Output(component_id='stock_graph', component_property='figure')],
	[Input(component_id='slct_stock', component_property='value')]
)
def update_graph(option_slctd):
	print(option_slctd)
	print(type(option_slctd))

	container = "The stock chosen by the user was: {}".format(option_slctd)

	dff = data.copy()
	fig = go.Candlestick(x=times,
                open=z.get('open'),
                high=z.get('high'),
                low=z.get('low'),
                close=z.get('close'),
				increasing_line_color= 'green', decreasing_line_color= 'red')

	fig.update_layout(
		title_text = "Dash Test",
		title_xanchor = "center",
		title_font=dict(size=24),
		title_x=0.5,
		geo=dict(scope='use'),
	)

	return container, fig

#-----------------------------------------------------------------------------------------------------------------


#  - - - - - PLOTTING - - - - -
#-----------------------------------------------------------------------------------------------------------------

#  - - - - - PLOTTING - - - - -

# setting up subplots
fig = make_subplots(rows=5, cols=1)

# plotting the candlesticks
candlesticks = go.Candlestick(x=times,
                open=z.get('open'),
                high=z.get('high'),
                low=z.get('low'),
                close=z.get('close'),
				increasing_line_color= 'green', decreasing_line_color= 'red')
fig.add_trace(candlesticks, row=1, col=1)

# plotting the macd
macd = go.Scatter(x=times, y=z['MACD'])
macdSIGNAL = go.Scatter(x=times, y=z['MACDsignal'])
zeroindex = go.Scatter(x=times, y=z['zeroindex'])
fig.add_trace(macd, row=3, col=1)
fig.add_trace(macdSIGNAL, row=3, col=1)
fig.add_trace(zeroindex, row=3, col=1)

# plotting 8 step and 21 step ema
ema8 = go.Scatter(x=times,y=z['8EMA'])
ema21 = go.Scatter(x=times,y=z['21EMA'])
fig.add_trace(ema8, row=4, col=1)
fig.add_trace(ema21, row=4, col=1)

# Example commit for new branch
#  

# plotting RSI

# above line is the other approach, but it does not work with subplots
RSI = go.Scatter(x=times, y=z['RSI'])
rsi30 = go.Scatter(x=times, y=z['30rsi'])
rsi70 = go.Scatter(x=times, y=z['70rsi'])
fig.add_trace(RSI, row=5, col=1)
fig.add_trace(rsi30, row=5, col=1)
fig.add_trace(rsi70, row=5, col=1)


fig.show()

# this line can be used to resize
# fig.update_layout(height=600, width=600)
fig = px.line(z, x=times, y=['RSI', '30rsi', '70rsi'], color_discrete_map={'30rsi':'green','21EMA':'red'} )
fig.show()

#-----------------------------------------------------------------------------------------------------------------

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

# Finding Peaks on the Graph

indices = find_peaks(z['RSI'])[0]

fig = go.Figure()
fig.add_trace(go.Scatter(
	y = z['RSI'],
	mode='lines+markers',
	name='Original Plot'
))


fig.add_trace(go.Scatter(
    x=indices,
    y=[z['RSI'][j] for j in indices],
    mode='markers',
    marker=dict(
        size=8,
        color='red',
        symbol='cross'
    ),
    name='Detected Peaks'
))

fig.show()

idx8 = np.argwhere(np.diff(np.sign(z['8EMA'] - z['21EMA']))).flatten()


# improved crossover, can be modified a bit but the general idea is below
z['emaCross'] = None
pos = 0
leading8 = True if z['8EMA'][0] > z['21EMA'][0] else False
for price in z['8EMA']: 
	if pos != 0 or pos != len(z['8EMA']):
		if leading8:
			if z['21EMA'][pos] > z['8EMA'][pos]:
				leading8 = False
				z['emaCross'][pos] = z['8EMA'][pos]
		elif not leading8:
			if z['21EMA'][pos] < z['8EMA'][pos]:
				leading8 = True
				z['emaCross'][pos] = z['21EMA'][pos]
	pos += 1

# z['8EMA'].plot()
# z['21EMA'].plot()
#z['21EMA'].plot(title='EMA', label='21ema', color='orange', ax = axes[1])
#plt.scatter(z['Price'].index[idx8], z['8EMA'][idx8], color='red')


# improved crossover, can be modified a bit but the general idea is below
z['emaCross'] = None
pos = 0
leading8 = True if z['8EMA'][0] > z['21EMA'][0] else False
for price in z['8EMA']: 
	if pos != 0 or pos != len(z['8EMA']):
		if leading8:
			if z['21EMA'][pos] > z['8EMA'][pos]:
				leading8 = False
				z['emaCross'][pos-1] = z['8EMA'][pos-1]
		elif not leading8:
			if z['21EMA'][pos] < z['8EMA'][pos]:
				leading8 = True
				z['emaCross'][pos-1] = z['21EMA'][pos-1]
	pos += 1

fig = go.Figure(data=go.Scatter(x = times, y = z['8EMA'], mode = 'lines'))
fig.add_traces(go.Scatter(x = times, y = z['21EMA'], mode = 'lines'))
fig.add_traces(go.Scatter(x = times, y= z['emaCross'], mode = 'markers'))

fig.show()

#if __name__ == '__main__':
	#app.run_server(debug=True)
