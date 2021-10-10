import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from termcolor import colored
from components.Stock import Stock
from stockmontecarlo import Montecarlo

class Backtest():
	def __init__(self, startcash, strategy, pos_size, stoploss, stoploss_percent, takeprofit, takeprofit_percent, commissions, commission_amount, ticker, index_ticker, investment_period, interval):
		self.startcash = startcash
		self.strategy = strategy
		self.pos_size = pos_size
		self.stoploss = stoploss
		self.stoploss_percent = stoploss_percent
		self.takeprofit = takeprofit
		self.takeprofit_percent = takeprofit_percent
		self.commissions = commissions
		self.commission_amount = commission_amount
		self.ticker = ticker
		self.index_ticker = index_ticker
		self.investment_period = investment_period
		self.interval = interval

		self.stock = Stock(ticker, investment_period, interval)

	def setData(self, data):
		self.stock.closeprices = pd.DataFrame(index=self.stock.closeprices.index, data=data)

	def run(self, display_trades = False):
		pos_size = self.pos_size
		commission_amount = self.commission_amount
		commissions = self.commissions
		stoploss = self.stoploss
		stoploss_percent = self.stoploss_percent
		takeprofit = self.takeprofit
		takeprofit_amount = self.takeprofit_percent
		cash = self.startcash
		stock = self.stock

		# Moving average configuration
		short_rolling = stock.closeprices.ewm(span=12, adjust=False).mean()
		long_rolling = stock.closeprices.ewm(span=26, adjust=False).mean()
		ema_indicator = short_rolling - long_rolling

		# MACD configuation
		macd_line = short_rolling - long_rolling
		signal = macd_line.ewm(9, adjust=False).mean()
		macd_indicator = macd_line - signal

		#day to day percent configuration
		d2d_indicator = [0]
		for i in range(1, len(stock.closeprices)):
			if stock.closeprices[i] <= .97*stock.closeprices[i-1]:
				d2d_indicator.append(1)
			elif stock.closeprices[i] >= 1.04*stock.closeprices[i-1]:
				d2d_indicator.append(-1)
			else:
				d2d_indicator.append(0)
		
		baseprice_indicator = []

		profit_record = pd.DataFrame(index=stock.closeprices.index)

		profit = 0
		entryprice = 0
		entered = False
		profit_record_temp = []
		tradecount = 0 
		if self.strategy == 'macd':
			indicator = macd_indicator
		elif self.strategy == 'ema':
			indicator = ema_indicator
		elif self.strategy == 'd2d':
			indicator = d2d_indicator
		else:
			raise NameError('STRATEGY NOT FOUND')
		for closeprice, indicate, date in zip(stock.closeprices, indicator, stock.history.index):
			# opening trade
			if indicate > 0 and entered == False:
				entered = True
				entryprice = closeprice
				if entryprice * pos_size <= cash:
					cash -= entryprice * pos_size
					if commissions:
						cash -= commission_amount
				else:
					raise NameError('NOT ENOUGH CASH TO OPEN POSITION')
				tradecount += 1
				if display_trades:
					print('[{}] entered at {}'.format(date, entryprice))

			# closing trade
			elif indicate < 0 and entered == True:
				entered = False
				profit += closeprice - entryprice
				cash += closeprice * pos_size
				if commissions:
					cash -= commission_amount
				tradecount += 1
				if display_trades:
					print('[{}] closed at {}'.format(date, closeprice))

			# stop loss check
			elif stoploss == True and entered == True and closeprice < (entryprice * (1 - stoploss_percent)):
				entered = False
				profit += closeprice - entryprice
				cash += closeprice * pos_size
				if commissions:
					cash -= commission_amount
				tradecount += 1
				if display_trades:
					print('[{}] STOPLOSS closed at {}'.format(date, closeprice))

			# take profits check
			elif takeprofit == True and entered == True and closeprice > entryprice * (1 + takeprofit_percent):
				entered = False
				profit += closeprice - entryprice
				cash += closeprice * pos_size
				if commissions:
					cash -= commission_amount
				tradecount += 1
				if display_trades:
					print('[{}] TAKE PROFITS closed at {}'.format(date, closeprice))
			profit_record_temp.append(profit * pos_size)
		if entered == True:
			profit += stock.closeprices[-1] - entryprice
			profit_record_temp[-1] = profit * pos_size
			cash += stock.closeprices[-1] * pos_size
			if commissions:
				cash -= commission_amount
			tradecount += 1
			if display_trades:
				print('[{}] closed at {}'.format(stock.history.index[-1], stock.closeprices[-1]))

		profit_record['Profit'] = np.array(profit_record_temp)

		# CALCULATING ALL RETURNS
		# strat: percent return is adjusted so that cash in account does not skew returns
		self.strat_return_percent = round(float(100 * ((cash - startcash) / (pos_size * stock.closeprices[0]))), 2)
		self.strat_return_amount = round(float(cash - startcash), 2)
		# hold
		self.hold_return_percent = round(float(100 * ((stock.closeprices[-1] - stock.closeprices[0]) / stock.closeprices[0])), 2)
		self.hold_return_amount = round(float(pos_size * (stock.closeprices[-1] - stock.closeprices[0])), 2)
		# index
		index = Stock(index_ticker, investment_period, interval) 
		self.index_return_percent = round(float(100 * ((index.closeprices[-1] - index.closeprices[0]) / index.closeprices[0])),2)
		self.index_return_amount = round(float(index.closeprices[-1] - index.closeprices[0]),2)
		# commissions calculation
		self.commissions_cost = commission_amount * tradecount

		self.endcash = cash
		self.tradecount = tradecount
		self.profit_record = profit_record
		self.macd_line = macd_line
		self.signal = signal

	def display_results(self):
		# RESULTS DISPLAY	
		print('TICKER: {}'.format(self.ticker))
		print('STARTING CASH: {}'.format(self.startcash))
		print('ENDING CASH: {}'.format(round(self.endcash, 2)))
		print('STRATEGY: {}'.format(self.strategy))
		print('INVESTMENT PERIOD: {}'.format(self.investment_period))
		print('INTERVAL: {}'.format(self.interval))
		print('POSITION SIZE: {}'.format(self.pos_size))
		print('NUMBER OF TRADES: {}'.format(self.tradecount))
		print('COMMISSIONS: {} {}'.format(self.commissions, self.commission_amount))
		print('COMMISSIONS COST: {}'.format(self.commissions_cost))
		print('STOP LOSS: {} {}'.format(self.stoploss, self.stoploss_percent))
		print('TAKE PROFIT: {} {}'.format(self.takeprofit, self.takeprofit_percent))
		print(colored('STRAT P/L (%): {}'.format(self.strat_return_percent), 'red', attrs=['underline']))
		print('STRAT P/L ($): {}'.format(self.strat_return_amount))
		print(colored('HOLD P/L (%): {}'.format(self.hold_return_percent), 'yellow', attrs=['underline']))
		print('HOLD P/L ($): {}'.format(self.hold_return_amount))
		print(colored('INDEX P/L (%) {}: {}'.format(self.index_ticker, self.index_return_percent), 'cyan', attrs=['underline']))
		print('INDEX P/L ($): {}'.format(self.index_return_amount))
	
	def graph_results(self):
		# GRAPH DISPLAY
		fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10,7))
		fig.tight_layout(pad=5)
		self.stock.closeprices.plot(title="Closing price", label='Price', legend=True, ax = axes[0]) #ax = axes[0] etc

		xline = self.profit_record.copy(deep=True)
		del xline['Profit']
		xline['Line'] = 0 
		xline.plot(ax=axes[1], linewidth=0.5, color='black')
		self.macd_line.plot(title="SIGNAL", label='macd', color='red', ax = axes[1])
		self.signal.plot(label='signal', color='blue', ax = axes[1])

		self.profit_record.plot(title='profit',label='profit', ax = axes[2])

		plt.show()
		
if __name__ == "__main__":
	startcash = 5000
	strategy = 'ema' # choose one: macd, ema
	pos_size = 10
	stoploss = False 
	stoploss_percent = 0.02
	takeprofit = False 
	takeprofit_percent = 0.06
	commissions = False 
	commission_amount = .65
	ticker = 'AAPL'
	index_ticker = '^GSPC'
	investment_period = '1y'
	interval = '1d'

	x = Backtest(startcash, strategy, pos_size, stoploss, stoploss_percent, takeprofit, takeprofit_percent, commissions, commission_amount, ticker, index_ticker, investment_period, interval)

	x.run()
	x.display_results()
	x.graph_results()

	steps = len(x.stock.closeprices)
	runs = 10000
	bias = 0

	# monte = Montecarlo(x.stock, steps, runs, bias)
	# monte.display()
