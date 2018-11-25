#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 23:41:17 2018

This script is used to concatenate the various csv files from the different premier league seasons
@author: victorodouard
"""
import pandas as pd 

years = [format(i, "02") for i in range(0,20)]

dfs = []

column_headers = []
for i, y in enumerate(years):
    
    if i == len(years) - 1:
        break
    
    new_df = pd.read_csv("../data/20{0}-20{1}.csv".format(years[i], years[i + 1]))
    
    new_column_headers = new_df.columns.values
    print(column_headers == new_column_headers)
    column_headers = new_column_headers
    
    dfs.append(new_df)
    

combined = pd.concat(dfs, axis=0, ignore_index=True)
combined = combined.reindex(new_df.columns, axis=1)

combined.to_csv("full_data.csv")
    



