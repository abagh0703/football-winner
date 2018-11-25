#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:53:08 2018

@author: victorodouard
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor


feature_cols = [26, 28, 30, 83, 84, 87, 88, 113, 114, 117, 118]
label_col = 5

file = "../data/base_data.xlsx"

data = pd.read_excel(file)

features = data.iloc[:,feature_cols]
labels = data.iloc[:,label_col]

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)

reg = MLPRegressor().fit(X_train, y_train)

score = reg.score(X_test, y_test)