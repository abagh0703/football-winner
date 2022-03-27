# football-winner
A website to show predictions for upcoming Football (called Soccer in America) games. This is no longer maintained.

# quick_and_dirty.py
This is our first pass at a VERY basic model, just to get our feet wet.

* Library: `sklearn`
* Algorithm: Logistic Regression
* Output: `1` for home team win (away team loss), `0` for home team loss or draw (away team win or draw)
* Features: Cumulative win/tie/loss percentages for both teams, `6` total
* Training set: Randomly chosen `70%` split of all games between 2006-2017 and 2017-2018 seasons
* Test set: Randomly chosen `30%` split games between 2006-2017 and 2017-2018 seasons
* Accuracy: `65%`


# multi-class.py

* Library: `sklearn`
* Algorithm: Logistic Regression, Multiclass
* Output: `2` for home team win (away team loss), `1` for home team draw (away team draw), `0` for home team loss (away team win)
* Features: Cumulative win/tie/loss percentages for both teams, `6` total
* Training set: Randomly chosen `70%` split of all games between 2006-2017 and 2017-2018 seasons
* Test set: Randomly chosen `30%` split games between 2006-2017 and 2017-2018 seasons
* Accuracy: `50%` (since it must choose between three outcomes and no longer just two)

# Datasets

* cum_recs_pct.csv: Contains all games from 06-07 season to 17-18 season and their results, along with each teams cumulative record up to that point. Outcome is labeled as 1 for home win and 0 for home tie or loss.
* cum_recs_pct_multiclass.csv: Same dataset except it is labeled with 2 for home win, 1 for home tie, 0 for home loss



