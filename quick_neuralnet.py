#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:51:03 2018

@author: victorodouard
"""

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix

table = np.genfromtxt("data/cum_rec.csv", delimiter=",")
table = np.delete(table, (0, 1), axis=0)
idx = np.r_[18:24,48:54]
X = table[1:,idx]
y = table[1:, 5:6]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

clf = MLPClassifier(solver="lbfgs", alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1)
clf.fit(X_train, y_train)


predictions = clf.predict(X_test)

predictions = predictions.reshape((-1, 1))

comp = np.concatenate((predictions, y_test), axis=1)

score = clf.score(X_test, y_test)

confusion_matrix = confusion_matrix(y_test, predictions)

print(confusion_matrix)



print(table)

