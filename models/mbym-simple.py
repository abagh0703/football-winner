#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 10:15:46 2018

This model uses a gradient boosted tree to make minute by minute predictions.

@author: victorodouard
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

with open("data.npy", 'rb') as f:
    data = np.load(f)


feature_cols = [1, 2, 3]
label_col = 6


features = data[:,feature_cols]
labels = data[:,label_col]


X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)

# dtrain = xgb.DMatrix(X_train.values, label=y_train)
# dtest = xgb.DMatrix(X_test.values)

model = xgb.XGBClassifier()
model.fit(X_train, y_train)

#num_round = 45
#model = xgb.train({}, dtrain, num_round)

preds = model.predict(X_test)

predictions = [round(value) for value in preds]

accuracy = accuracy_score(y_test, predictions)