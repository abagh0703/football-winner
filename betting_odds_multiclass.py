#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 01:51:03 2018

@author: victorodouard
"""

HEADER_ROWS = [0]
FEATURE_COLS = list(range(76, 106))
LABEL_COLS = [7, 8, 9]





def import_and_sort(heads, feats, label):
    # import dataset and delete header rows
    table = np.genfromtxt("data/2008-2018-pct.csv", delimiter=",")
    table = np.delete(table, [0], axis=0)
    
    print(table)
    # take feature columns for X and label columns for y
    X = table[:, feats]
    print(X)
    
    y_list = []
    
    for label in LABEL_COLS: 
        y_list.append(table[:, label])

    print(np.isnan(X).any())
    print(np.isnan(y_list).any())
    return X, y_list, table
    

def train(X_train, y_train):
    # Split features and labels into training and test sets
    
    # Initialize and fit logistic regression model
    logreg = LogisticRegression()
    logreg.fit(X_train, y_train)
    
    return logreg

def test(model, X_test, y_test):
    
    predictions = model.predict(X_test)
    
    # make table with actualy results and predictions side-by-side
    predictions = predictions.reshape((-1, 1))
    comp = np.concatenate((predictions, y_test), axis=1)
    
    # get accuracy
    score = model.score(X_test, y_test)
    
    # get confusion matrix (true negs, false negs, etc)
    conf_mat = confusion_matrix(y_test, predictions)
    
    
    # view coeffs
    coeffs = logreg.coef_
    print(coeffs)
    intercept = logreg.intercept_
    print(intercept)
    
    return score

def combine_classifiers(classifiers, x_test, y_test, y_multi):
    
    predictions = np.empty((x_test.shape[0], 0))
    
    for i, model in enumerate(classifiers):
        model_preds = model.predict_proba(x_test)[:, 1:]
        model_preds_2 = model.predict(x_test)
        predictions = np.concatenate((predictions, model_preds), axis=1)
    
    predictions = predictions - [[0, 0, 0]]
    pred = np.argmax(predictions, axis=1).reshape(-1,1)  
    
    comp = np.concatenate((y_multi, pred, predictions), axis=1)
    np.savetxt("terrible_model_2.csv", comp, delimiter=",")
   
    print(accuracy_score(y_multi, pred))


if __name__ == "__main__":
      
    X, y_list, table = import_and_sort(HEADER_ROWS, FEATURE_COLS, LABEL_COLS)  
    y_win, y_tie, y_loss = y_list
   
    y_multi = table[:,6:7]
    
    classifiers = [] 
    
    splits = train_test_split(X, y_win, y_tie, y_loss, y_multi, test_size=0.3, random_state=0)
    X_tr, X_te, y_win_tr, y_win_te, y_tie_tr, y_tie_te, y_loss_tr, y_loss_te, y_multi_tr, y_multi_te = splits

    classifiers.append(train(X_tr, y_loss_tr))
    classifiers.append(train(X_tr, y_tie_tr))
    classifiers.append(train(X_tr, y_win_tr))
        
    combine_classifiers(classifiers, X_te, [y_loss_te, y_tie_te, y_win_te], y_multi_te)