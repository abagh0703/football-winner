#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 19:19:21 2018

This script creates a new column that accumulates the "accumulatee" columns up to the present game.
For example, if the "accumulatee" columns are home_goals and away_goals, each row will get a new 
column containing the number of goals each team scored up to that game.

If by_season true, the count resets every season. If not, it doesn't.

@author: victorodouard
"""

import pandas as pd
import numpy as np


home_accumulatee = "home_goals"
away_accumulatee = "away_goals"
new_col_name = "szn_gls"

by_season = True


data = pd.read_excel("accumulated_conceded_goals_szn.xlsx")



teams = data.HT.unique()

data["home_" + new_col_name] = 0
data["away_" + new_col_name] = 0


for team in teams:
    data_slice = data.loc[((data["home"] == team) | (data["away"] == team))]
    
    val = 0
    szn = ""
    for i, row in data_slice.iterrows():
        
        if(row["season"] != szn and by_season):
            val = 0
            szn = row["SZN"] 
        
        if row["home"] == team:
            data.at[i, "home_" + new_col_name] = val
            val = val + row[home_accumulatee]
         
        if row["away"] == team:
            data.at[i, "away_" + new_col_name] = val
            val = val + row[away_accumulatee]
        
            