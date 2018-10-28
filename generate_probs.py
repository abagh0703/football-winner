#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 00:09:38 2018

@author: victorodouard
"""
import numpy as np 
import pandas as pd
import math




data_df = pd.read_csv("data/2008-2018.csv", delimiter=",")
data_df = data_df.drop(["Unnamed: 74", "Unnamed: 75", "Unnamed: 76"], axis=1)

odds_df = data_df.loc[:,"B365H":"BSA"]
odds_df = odds_df.fillna(0)

pct_df = odds_df.apply(lambda s : 1/s, axis=1)

pct_df = pct_df.replace([np.inf, -np.inf], np.nan)
pct_df = pct_df.fillna(0)
namemap = {n: n + "_P" for n in pct_df.columns.values}
pct_df = pct_df.rename(namemap, axis=1)
pct_df = pct_df.set_index(data_df.index)


new_df = pd.concat([data_df, pct_df], axis=1)

important= ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "H", "D", "A", "FTR", "HTHG", "HTAG", "HTR", "Referee", "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"]
order = important + [c for c in new_df.columns if c not in important]
new_df = new_df[order]


new_df.to_csv("data/2008-2018-pct.csv")





