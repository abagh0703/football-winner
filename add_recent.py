#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 22:21:47 2018

@author: victorodouard
"""

def find_form(team, start_index, length):
    # print("__________", start_index, "______________")
    team_name = table.loc[start_index, team + "_team"]
    # print(team_name)
    index = start_index
    last_index = start_index
    counter = 0
    team_prev = team
    season = table.loc[index, "season"]
    
    while counter < length and index > 0 and season == table.loc[index - 1, "season"]:
        index = index - 1
        if team_name == table.loc[index, "home_team"]:
            counter += 1
            team_prev = "home"
            last_index = index
        if team_name == table.loc[index, "away_team"]:
            counter += 1
            team_prev = "away"
            last_index = index
        #print(index, counter)
            
            
    wins_col = team + "_wins"
    ties_col = team + "_ties"
    loss_col = team + "_loss"
    
    old_wins_col = team_prev + "_wins"
    old_ties_col = team_prev + "_ties"
    old_loss_col = team_prev + "_loss"
    
    """
    print(wins_col)
    print(old_wins_col)
    print(start_index)
    print(last_index)
    """
   
    wins = table.loc[start_index, wins_col] - table.loc[last_index, old_wins_col]
    ties = table.loc[start_index, ties_col] - table.loc[last_index, old_ties_col]
    loss = table.loc[start_index, loss_col] - table.loc[last_index, old_loss_col]
    
    total = wins + ties + loss
    
    if total > 0:
        wins_pct = wins / total
        ties_pct = ties / total
        loss_pct = loss / total
        
        return wins_pct, ties_pct, loss_pct
    else:
        return wins, ties, loss
    
    
            
    
import pandas as pd 
import numpy as np

table = pd.read_csv("data/cum_rec_pct_multiclass.csv")
# table = table.loc[:400,:]

for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20]:
    print(i)
    h_w = "home_l" + str(i) + "_wins"
    h_t = "home_l" + str(i) + "_ties"
    h_l = "home_l" + str(i) + "_loss"
    
    table[h_w] = 0
    table[h_t] = 0
    table[h_l] = 0
    
    a_w = "away_l" + str(i) + "_wins"
    a_t = "away_l" + str(i) + "_ties"
    a_l = "away_l" + str(i) + "_loss"
    
    table[a_w] = 0
    table[a_t] = 0
    table[a_l] = 0
    
    for j, row in enumerate(table.iterrows()):
        
        table.loc[j, h_w], table.loc[j, h_t], table.loc[j, h_l] = find_form("home", j, i)
        table.loc[j, a_w], table.loc[j, a_t], table.loc[j, a_l] = find_form("away", j, i)


    
