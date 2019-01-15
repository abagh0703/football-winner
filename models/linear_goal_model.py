#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:41:03 2018

@author: victorodouard
"""

import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

"""
1. HAvP - Home average percentage chance (betting odds)
2. DAvP - Draw average percentage chance (betting odds)
3. AAvP - Away average percentage chance (betting odds)
4. home_gls_game - home avg goals per game (season)
5. away_gls_game - away avg goals per game (season)
6. home_conceded_game - home abg goals conceded per game (season)
7. away_conceded_game - away avg goals conceded per game (season)
8. home_gls_game - home avg goals per game (last 20)
9. away_gls_game - away avg goals per game (last 20)
10. home_conceded_game - home abg goals conceded per game (last 20)
11. away_conceded_game - away avg goals conceded per game (last 20)

"""

feature_cols = [26, 28, 30, 83, 84, 87, 88, 113, 114, 117, 118]
# home win prob, draw prob, away prob,
label_col = 5

file = "../data/base_data.xlsx"

data = pd.read_excel(file)

features = data.iloc[:,feature_cols]
labels = data.iloc[:,label_col]

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)

reg = LinearRegression().fit(X_train, y_train)

score = reg.score(X_test, y_test)

preds = reg.predict(X_test)
preds = preds.round()

difference = preds - y_test

with open("home_goals.pkl", "wb") as f:
    pickle.dump(reg, f) 