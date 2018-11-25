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
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


feature_cols = [26, 28, 30, 71, 72, 73, 78, 79, 80, 105, 106, 107, 108, 109, 110, 83, 84, 87, 88, 113, 114, 117, 118]
label_col = 7

file = "base_data.xlsx"

data = pd.read_excel(file)

features = data.iloc[:,feature_cols]
labels = data.iloc[:,label_col]


max_score = 0
max_score_train = 0
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=0)

for i in range(1, 50):
    for j in range(1, 50):
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(i,j), random_state=1)
          
        
        clf.fit(X_train, y_train)
        
        score_train = clf.score(X_train, y_train)
        score_test = clf.score(X_test, y_test)
        
        if score_test > max_score:
            max_score = score_test
            max_i = i
            max_j = j
        if score_train > max_score_train:
            max_score_train = score_train
            max_i_train = i
            max_j_train = j
            
        print("max train: ", max_score_train, max_i_train, max_j_train)
        print("max: ", max_score, max_i, max_j)