import pandas as pd
import numpy as np
import time
from operator import add

def get_result(row, team):
    if team == row["home_team"]:
        arr = ["w", "l", "d"]
        cum = [row["home_wins"], row["home_ties"], row["home_loss"]]
    elif team == row["away_team"]:
        arr = ["l", "w", "d"]
        cum = [row["away_wins"], row["away_ties"], row["away_loss"]]
    else:
        print("there was an error")
    
        
    if row["home_goals"] > row["away_goals"]:
        return arr[0], cum
    elif row["home_goals"] < row["away_goals"]:
        return arr[1], cum
    else:
        return arr[2], cum

def increment(index, team, result, cum, team_name):
    inc_dict = {"w": [1, 0, 0], "d": [0, 1, 0], "l": [0, 0, 1]}
    wins_col = team + "_wins"
    ties_col = team + "_ties"
    loss_col = team + "_loss"
    
    vals = list( map(add, cum, inc_dict[result]))
    
    results.at[index, wins_col] = vals[0]
    results.at[index, ties_col] = vals[1]
    results.at[index, loss_col] = vals[2]
    
def accumulate(index):
    
    home_team = results["home_team"][index]
    away_team = results["away_team"][index]
    season = results["season"][index] 
    curr = index - 1
    
    home_inc = False
    away_inc = False
    
    while True:
        if curr < 0 or results["season"][curr] != season:
            break;
            
        row = results.loc[curr]
        
        if not home_inc and (row["home_team"] == home_team or row["away_team"] == home_team):
            result, cum = get_result(row, home_team)
            increment(index, "home", result, cum, home_team)
            home_inc = True 
                
        if not away_inc and (row["home_team"] == away_team or row["away_team"] == away_team):
            result, cum = get_result(row, away_team)
            increment(index, "away", result, cum, away_team)
            away_inc = True
        
        curr = curr - 1
            
prev_changed_away = []
prev_changed_home = []
results = pd.read_csv("results.csv")


results["home_wins"] = 0
results["home_ties"] = 0
results["home_loss"] = 0

results["away_wins"] = 0
results["away_ties"] = 0
results["away_loss"] = 0


for i in range(0, len(results.index)):
    accumulate(i)
    






