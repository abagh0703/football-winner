#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 20:30:53 2018

Gradient boosted tree classifier for match outcome. 

@author: victorodouard
"""
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

feature_cols = [26, 28, 30, 71, 72, 73, 78, 79, 80, 105, 106, 107, 108, 109, 110, 83, 84, 87, 88, 113, 114, 117, 118]
label_col = 7

file = "../data/base_data.xlsx"

data = pd.read_excel(file)

features = data.iloc[:,feature_cols]
labels = data.iloc[:,label_col]


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



