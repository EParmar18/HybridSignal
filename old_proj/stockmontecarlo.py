import matplotlib.pyplot as plt
import random
from components.Stock import Stock
from statistics import mean
import sys

class Montecarlo():
	def __init__(self, stock, steps, runs, bias=0, verbose=False):
		self.stock = stock
		self.steps = steps
		self.runs = runs
		self.bias = bias

		self.outputs = []
		for i in range(runs):
			if verbose:
				print('working {} run {} of {}'.format(self.stock.ticker, i + 1, self.runs))
			prices = []
			for i in range(steps):
				prices.append(0)

			prices[0] = self.stock.closeprices[-1]

			for i in range(1, steps):
				prices[i] = prices[i-1]
				modifier = random.gauss(self.stock.avg_nominal_change, self.stock.stdev_changes)
				modifier += self.bias
				if prices[i] + modifier < 0:
					modifier = 0
				prices[i] += modifier
			self.outputs.append(prices)

		# meanline calculation can be consolidated to one loop, just needs to be done
		self.meanline = []
		for i in range(self.steps):
			self.meanline.append(0)
		for out in self.outputs:
			for i in range(self.steps):
				self.meanline[i] += out[i]
		for i in range(self.steps):
			self.meanline[i] = self.meanline[i] / runs

		self.finalvalue = self.meanline[-1]

		self.title = '{} expected price: {}'.format(self.stock.ticker, round(self.finalvalue,2))
		self.subtitle = 'parameters: {} {} - {} steps - {} runs - {} bias'.format(self.stock.investment_period, self.stock.interval, self.steps, self.runs, self.bias)

	def plot(self):
		for out in self.outputs:
			plt.plot(out, linewidth=0.75)
		plt.plot(self.meanline, linewidth=2, color='red')
		plt.suptitle(self.title)
		plt.title(self.subtitle, fontsize=9)
		plt.show()
	
	def display(self):
		print(self.title)
		print(self.subtitle)

if __name__ == '__main__':
	# only use if implementing command-line arguments
	# ticker = sys.argv[1]
	period = '30d'
	interval = '1h'
	steps = 24
	# 10000000 is a good number but cannot be graphed
	runs = 10000
	bias = 0.8
	graph = False 

	basket = ['tsla']
	for ticker in basket:
		stock = Stock(ticker, period, interval)
		# if running as verbose, do not run on a basket of length greater than 1. you will not see all of the basket results
		monte = Montecarlo(stock, steps, runs, bias)
		monte.display()
		monte.plot()
