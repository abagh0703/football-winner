#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:51:03 2018

@author: victorodouard
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix

table = np.genfromtxt("data/cum_rec_pct.csv", delimiter=",")
X = table[1:,-6:]
y = table[1:, 6:7]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

logreg = LogisticRegression()
logreg.fit(X_train, y_train)

predictions = logreg.predict(X_test)

predictions = predictions.reshape((-1, 1))

comp = np.concatenate((predictions, y_test), axis=1)

score = logreg.score(X_test, y_test)

confusion_matrix = confusion_matrix(y_test, predictions)

print(confusion_matrix)


coeffs = logreg.coef_[0]

print(table)

