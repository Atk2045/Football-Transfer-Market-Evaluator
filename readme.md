# FIFA_Transfer_Market_Evaluator


## Football Team Expenditure and Performance Analysis
This project analyzes the expenditure and performance of top football teams over two seasons (2022 and 2023) for selected European football leagues. It scrapes transfer expenditure data from the Transfermarkt website and fetches team performance data (such as goals, points, wins, losses, etc.) from the Football-Data.org API. The project then visualizes the relationship between team expenditure and performance using a scatter plot.


### Features
Scrapes football team expenditure data from Transfermarkt.
Fetches team performance data (e.g., goals, points, wins, draws) using the Football-Data.org API.
Calculates performance metrics, including the number of goals scored, points earned, and the cost per point.
Supports multiple leagues:
Premier League
La Liga
Bundesliga
Generates a scatter plot of expenditure versus points, labeling each team.
Exports the processed data to a CSV file.


### Requirements

Python 3.x
requests
BeautifulSoup4
pandas
matplotlib
fuzzywuzzy

