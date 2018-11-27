# API key: ca42e9efce635c0d2922b584c8fcdd2e121258dfb8752e00875018bda96521df

import requests
import json
import pickle
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize

"""
r = requests.get("https://apifootball.com/api/?action=get_events&from=2015-08-01&to=2018-11-25&league_id=62&APIkey=ca42e9efce635c0d2922b584c8fcdd2e121258dfb8752e00875018bda96521df")

parsed = json.loads(r.text)

with open('data.json', 'w') as outfile:
    json.dump(parsed, outfile)

"""
with open('data.json') as f:
    data = json.load(f)

    
df = json_normalize(data)
df = df[df.match_status == "FT"]


df_trimmed = df[df.match_id == "10008"]
print(json.dumps(parsed, indent=4))


overall = np.zeros((0, 7))

for i, row in df.iterrows():
    mbym = np.zeros((91, 7))
    
    mbym[:, 0] = int(row["match_id"])
    home_final = int(row["match_hometeam_score"])
    away_final = int(row["match_awayteam_score"])
    mbym[:, 4] = home_final
    mbym[:, 5] = away_final
    
    if home_final > away_final:
        mbym[:, 6] = 2
    elif home_final < away_final:
        mbym[:, 6] = 0
    else:
        mbym[:, 6] = 1
    
    goals = row["goalscorer"]
    
    for m in range(0, 91):
        mbym[m, 3] = m/90
        
        away_goals = 0
        home_goals = 0
        last_score = '0 - 0'
        
        for goal in goals:
            minute = int(goal['time'].strip('\''))
            
            if minute < m and goal['score'] != last_score:
                if goal['home_scorer'] == '':
                    away_goals += 1
                if goal['away_scorer'] == '':
                    home_goals += 1
            
        
        mbym[m, 1] = home_goals
        mbym[m, 2] = away_goals
        
    overall = np.concatenate((overall, mbym), axis=0)

saved = np.save("data", overall)
