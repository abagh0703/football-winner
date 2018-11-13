#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 12:54:52 2018

Calculates the difference between the last value for a "col_to_differentiate" and the value n 
rows prior.

For instance, if col_to_differentiate is accumulated goals, this script will calculate the goals
scored by that particular team in the last n games.


@author: victorodouard
"""

import pandas as pd
import time

    
new_col_name = "_l20_cum_gls"
col_to_differentiate = "_cum_gls"
n = 20


def differentiate():
    
    start_index = 0
    counter = 0
    for i, end_row in team_df.iterrows():
        start_row = team_df.iloc[start_index,:]
    
        start_where = ""
        end_where = ""
    
        if team == start_row.home:
            start_where = "home"
        elif team == start_row.away:
                start_where = "away"
        
        if team == end_row.home:
            end_where = "home"
        elif team == end_row.away:
            end_where = "away"
        
        difference = end_row[end_where + col_to_differentiate] - start_row[start_where + col_to_differentiate]
        data.at[i, end_where + new_col_name] = difference
        
        data.at[i, end_where + "_difference"] = counter - start_index
        
        print(difference)
        print(counter, start_index)
        
        if counter - start_index == n:
            start_index += 1
            
        counter += 1
        
            #print(i, start_index)
        
        
data = pd.read_excel("base_data.xlsx")

teams = data.home.unique()

data["home" + new_col_name] = 0
data["away" + new_col_name] = 0
data["away_difference"] = 0
data["home_difference"] = 0

for team in teams:
    team_df = data[((data.home == team) | (data.away == team))]
    differentiate()
    
    
    
    