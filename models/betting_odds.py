#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 01:33:36 2018

@author: victorodouard
"""

7#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:51:03 2018

@author: Victor Odouard and Ankita Pannu 
"""
import numpy as np

data_arr = data_df = np.genfromtxt("data/2008-2018-pct.csv", delimiter=",")
data_arr = np.delete(data_arr, [0], axis=0)

X = data_arr[:,76:106]
y = data_arr[:, 7]
# y = data_arr[:, 6] # Column vector

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

logreg = LogisticRegression()
logreg.fit(X_train, y_train)

predictions = logreg.predict(X_test)
score = logreg.score(X_test, y_test)
