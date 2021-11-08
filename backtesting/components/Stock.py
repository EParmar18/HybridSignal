import yfinance as yf
from datetime import datetime
from datetime import date
import mibian
import statistics
import pandas as pd

class Stock:
	def __init__(self, ticker, investment_period='1y', interval='1d'):
		self.ticker = ticker
		self.yfObject = yf.Ticker(ticker)
		self.history = self.yfObject.history(period=investment_period, interval=interval)
		self.investment_period = investment_period
		self.interval = interval
		self.openprices = self.history['Open']
		self.closeprices = self.history['Close']
		self.change_nominal = self.closeprices - self.openprices
		self.change_percent = round((self.change_nominal / self.openprices) * 100, 2)
		self.period_return_nominal = round(self.closeprices[-1] - self.openprices[0], 2)
		self.period_return_percent = round((self.period_return_nominal / self.openprices[0]) * 100, 2)
		self.avg_nominal_change = round(self.change_nominal.mean(), 2)
		self.avg_percent_change = round(self.change_percent.mean(), 2)
		self.stdev_changes = statistics.stdev(self.change_nominal)
	
		try:
			# CALCULATING 30 DAY ATM CALL IV 
			self.options_expirations = self.yfObject.options

			# finds the contract with at least 30d to expiration
			lowest = 0
			today = date.today()
			todaydatetime = datetime(year = today.year, month = today.month, day = today.day)	
			dte = 0
			for i in range(len(self.options_expirations)):
				converted_time = datetime.strptime(self.options_expirations[i], '%Y-%m-%d')
				if (converted_time - todaydatetime).days >= 30:
					dte = (converted_time - todaydatetime).days
					lowest = i
					break

			# prepares the calls chain to find the ATM option
			self.option_chain_calls = self.yfObject.option_chain(self.options_expirations[lowest]).calls

			atm = 0
			for i in range(len(self.option_chain_calls['impliedVolatility'])):
				if self.option_chain_calls['inTheMoney'][i] != self.option_chain_calls['inTheMoney'][i+1]:
					atm = i
					break

			# calculates the IV of the ATM call option
			# mibian.BS([Underlying Price, Call / Price Strike Price, Interest Rate, Days To Expiration], Call / Put Price)
			self.impvolcall = mibian.BS([self.closeprices[-1], self.option_chain_calls['strike'][atm], 0, dte], callPrice = self.option_chain_calls['lastPrice'][atm]).impliedVolatility / 100

			# prepares the puts chain to find the ATM option
			self.option_chain_puts = self.yfObject.option_chain(self.options_expirations[lowest]).puts
		
			atm = 0
			for i in range(len(self.option_chain_puts['impliedVolatility'])):
				if self.option_chain_puts['inTheMoney'][i] != self.option_chain_puts['inTheMoney'][i+1]:
					atm = i + 1
					break
			
			# calculates the IV of the ATM put option
			self.impvolput = mibian.BS([self.closeprices[-1], self.option_chain_puts['strike'][atm], 0, dte], callPrice = self.option_chain_puts['lastPrice'][atm]).impliedVolatility / 100

		except:
			pass
	
	def setData(self, data):
		self.closeprices = pd.DataFrame(index=self.closeprices.index, data=data)

	def __str__(self):
		return "{}".format(self.ticker.upper())
		
	def corr(self, target):
		return round(self.change_percent.corr(target.change_percent),3)
		
	
if __name__ == "__main__":
	stock = Stock('TSLA', '1y', '1d')
	print(stock)
	print("Period return (nominal $): {}".format(stock.period_return_nominal))
	print("Period return (%): {}".format(stock.period_return_percent))
	print("Avg nominal ($) change: {}".format(stock.avg_nominal_change))
	print("Avg percent (%) change: {}".format(stock.avg_percent_change))
	qqq = Stock('qqq', '1y', '1d')
	print("Correlation with QQQ: {}".format(stock.corr(qqq)))
	print("30 dte call impvol: {}".format(stock.impvolcall))
	print("30 dte put impvol: {}".format(stock.impvolput))
