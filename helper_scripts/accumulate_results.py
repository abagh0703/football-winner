"""
Calculates cumulative record for each team up to each game
"""


import pandas as pd
import numpy as np
import time
from operator import add

by_season = True

def get_result(row, team):
    if team == row["HT"]:
        arr = ["w", "d", "l"]
        cum = [row["CUM_H_W_AT"], row["CUM_H_D_AT"], row["CUM_H_L_AT"]]
    elif team == row["AT"]:
        arr = ["l", "d", "w"]
        cum = [row["CUM_A_W_AT"], row["CUM_A_D_AT"], row["CUM_A_L_AT"]]
    else:
        print("there was an error")
    
    return arr[row["R"]], cum


def increment(index, team, result, cum, team_name):
    inc_dict = {"w": [1, 0, 0], "d": [0, 1, 0], "l": [0, 0, 1]}
    wins_col = "CUM_" + team + "_W_AT"
    ties_col = "CUM_" + team + "_D_AT"
    loss_col = "CUM_" + team + "_L_AT"
    
    vals = list( map(add, cum, inc_dict[result]))
    
    results.at[index, wins_col] = vals[0]
    results.at[index, ties_col] = vals[1]
    results.at[index, loss_col] = vals[2]
    
def accumulate(index, by_season=True):
    print(index)
    
    home_team = results["HT"][index]
    away_team = results["AT"][index]
    season = results["SZN"][index] 
    curr = index - 1
    
    home_inc = False
    away_inc = False
    
    while True:
        if curr < 0 or (results["SZN"][curr] != season and by_season):
            break;
            
        row = results.loc[curr]
        
        if not home_inc and (row["HT"] == home_team or row["AT"] == home_team):
            result, cum = get_result(row, home_team)
            increment(index, "H", result, cum, home_team)
            home_inc = True 
                
        if not away_inc and (row["HT"] == away_team or row["AT"] == away_team):
            result, cum = get_result(row, away_team)
            increment(index, "A", result, cum, away_team)
            away_inc = True
        
        curr = curr - 1

results = pd.read_excel("full_data_with_records.xlsx")

results["CUM_H_D_AT"] = 0
results["CUM_H_D_AT"] = 0
results["CUM_H_L_AT"] = 0

results["CUM_A_W_AT"] = 0
results["CUM_A_D_AT"] = 0
results["CUM_A_L_AT"] = 0


for i in range(0, len(results.index)):
    accumulate(i, by_season)

results.to_excel("full_data_with_records_at.xlsx")






