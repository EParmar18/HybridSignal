import requests
import config
import pandas as pd
import talib as ta

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
x['4dayEMA'] = x['close'].ewm(span=18, adjust=False).mean()

x['RSI'] = ta.RSI(x['close'], timeperiod=14)

print(x)
