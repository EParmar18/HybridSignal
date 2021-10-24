# HybridSignal

This repo is the CSC Hacks team project repository that meets all of [the repository requirements](https://www.notion.so/CSC-Hacks-901a62e005c8494fa342e0cc738101ad#da206965e3ed497f9bd6c1ceebd4fac9).

## Project Description
* We want to use market data alongside specific indicators (Ex. EMA's, MACD, RSI, VOLUME, etc) to discover buy/sell opportunites for a security using Python, Yahoo Finance API, TD Ameritrade API, NumPy, and Pandas.
* We are doing this to explore working with financial data and trying to implement optimal strategies. Also we both like finanance/stock stuff
* Doing this will require learning the TD Ameritrade API, designing algorithms to implement relevant indicators, and learning the metrics used to judge a financial strategy.
* We anticipate the following challenges: Getting a full understanding of the algorithms for indicators with require a good amount of research, the actual implementation of indicators and choosing the optimal strategy, understanding metrics.

![Indicator Data](/images/indicator_graph.png)

## Team Information
Eshan Parmar
* Pitt CS, 2022
* esp27@pitt.edu
* Eshan Parmar in the CSC Discord
* https://www.linkedin.com/in/eshan-parmar-878275172/

Nick Nazari
* Pitt CS, 2024
* nin45@pitt.edu
* nazari in the CSC Discord
* https://www.linkedin.com/in/~nick/

## Run the project
* You will need a TD Ameritrade API key in a file called config.py. Make sure the file is called config.py, because that is the only file that .gitignore will not upload.

* Store the key in a string in the variable called client_id

## MVP Milestone
In order to run the application make sure you have the following libraries installed:
*pandas*
*numpy*
*plotly*
*matlibplot*

* https://forms.gle/A5qr2dXPuURnLjww6 - Feedback Form!
* The main file to run is **test_datapull.py** which will produce a series of graphs. For the examples below the stock being used is AAPL's stock graph on Oct 22nd

![Price Candle](/images/Price.png)
* Graph 1 is the candle graph for a specified stock (AAPL in this case)

![MACD](/images/MACD.png)
* Graph 2 is the MACD of that specific stock. MACD is the Moving Average Convergence Divergence and is designed to reveal changes in the strength, direction, momentum, and duration of a trend in a stock's price. By looking at the MACD we can employ a simple trading strategy of buying when the MACD crosses above 0 and sell when it crosses below

![EMA](/images/EMA.png)
* Graph 3 is the 8EMA and the 21EMA over that time period. EMA is the exponential moving average of a stock, by looking at the 8 Day EMA and the 21 Day EMA we can see general direction of a stock since the EMA's are quick in their indication. When the 8 EMA crosses above the 21 EMA that could signal a possible buy point, and when the 21 EMA crosses below the 8 EMA that could represent a possible exit point. 

![RSI](/images/RSI.png)
* Graph 4 is the RSI index over that time period with the lines at the 30 and 70 values. When the RSI index crosses under 30 that means that the stock is currently being oversold, when the RSI goes over 70 that means the stock is being overbought.

![Peaks](/images/Peak.png)
* Graph 5 demonstrates finding peaks of a financial graph. Using certain peaks we could determine optimal selling points as well as other strategies. 
