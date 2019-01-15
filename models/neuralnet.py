#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 15:19:54 2018

Neural net that fits data based on accumulated and differentiated features in base_data.
Maximum training accuracy : 62.6% for (45, 49) neural net
Maximum test accuracy: 54.6% for (1, 25) neural net

@author: victorodouard
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


feature_cols = [26, 28, 30, 71, 72, 73, 78, 79, 80, 105, 106, 107, 108, 109, 110, 83, 84, 87, 88, 113, 114, 117, 118]
#               0   1   2   3   4    5   6  7    8   9    10   11   12   13   14  15  16  17  18  19    20   21   22
label_col = 7

file = "../data/base_data.xlsx"

data = pd.read_excel(file)

features = data.iloc[:,feature_cols]
labels = data.iloc[:,label_col]


max_score = 0
max_score_train = 0
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)

clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(1,50), random_state=1)
          
        
clf.fit(X_train, y_train)
        
score_train = clf.score(X_train, y_train)
score_test = clf.score(X_test, y_test)

with open("model.pkl", "wb") as f:
    pickle.dump(clf, f) 
 
with open("model.pkl", "rb") as f:
    clf2 = pickle.load(f)

print(np.array([X_test.loc[1,:]]).shape)
pred = clf2.predict(np.array([X_test.loc[1,:]]))
"""
pred = pred.reshape(-1, 1)
print(pred.shape)
y_test = y_test.reshape(-1, 1)
print(y_test.shape)
new_array = np.concatenate((pred, y_test), axis=1)
"""

            
"""
for i in range(1, 50):
    for jsonData in range(1, 50):
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(i,jsonData), random_state=1)
          
        
        clf.fit(X_train, y_train)
        
        score_train = clf.score(X_train, y_train)
        score_test = clf.score(X_test, y_test)
        
        if score_test > max_score:
            max_score = score_test
            max_i = i
            max_j = jsonData
        if score_train > max_score_train:
            max_score_train = score_train
            max_i_train = i
            max_j_train = jsonData
            
        print("max train: ", max_score_train, max_i_train, max_j_train)
        print("max: ", max_score, max_i, max_j)
"""