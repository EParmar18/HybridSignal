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

The main file to run is **test_datapull.py** which will produce a series of graphs

Graph 1 is the candle graph for a specified stock
Graph 2 is the MACD of that specific stock
Graph 3 is the 8EMA and the 21EMA over that time period
Graph 4 is the RSI index over that time period
