# football-winner

# quick_and_dirty.py
This is our first pass at a VERY basic model, just to get our feet wet.

* Library: `sklearn`
* Algorithm: Logistic Regression
* Output: `1` for home team win (away team loss), `0` for home team loss or draw (away team win or draw)
* Features: Cumulative win/tie/loss percentages for both teams, `6` total
* Training set: Randomly chosen `70%` split of all games between 2006-2017 and 2017-2018 seasons
* Test set: Randomly chosen `30%` split games between 2006-2017 and 2017-2018 seasons
* Accuracy: `65%`


# multiclass.py

* Library: `sklearn`
* Algorithm: Logistic Regression, Multiclass
* Output: `2` for home team win (away team loss), `1` for home team draw (away team draw), `0` for home team loss (away team win)
* Features: Cumulative win/tie/loss percentages for both teams, `6` total
* Training set: Randomly chosen `70%` split of all games between 2006-2017 and 2017-2018 seasons
* Test set: Randomly chosen `30%` split games between 2006-2017 and 2017-2018 seasons
* Accuracy: `50%` (since it must choose between three outcomes and no longer just two)

# Datasets

* 



