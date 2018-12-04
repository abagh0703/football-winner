#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:41:03 2018

@author: victorodouard
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


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
