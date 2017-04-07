'''
 *******************************************************
 * Copyright (C) 2017 MENGYU HUANG, CHENG GUO <renehuang0917@gmail.com>
 * 
 * This file is part of {NBA Simulatior}.
 * 
 * {NBA Simulator} can not be copied and/or distributed without the express
 * permission of MENGYU HUANG and CHENG GUO
 *******************************************************/
'''

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 13:53:37 2017

@author: reneh
"""
import math

#test the model
def test(games, game_data):
    temp1=0
    temp2=0
    for index, row in game_data.iterrows():
        real_mar=float(row['away_score'])-float(row['home_score'])
        sim_mar=games['sim_ascore'].loc[row['away_tm']+' vs '+row['home_tm']]-games['sim_hscore'].loc[row['away_tm']+' vs '+row['home_tm']]
        temp1=temp1+int(real_mar*sim_mar>0)
        temp2=temp2+int(math.fabs(real_mar-sim_mar)<=5)
    pick=temp1/len(game_data)*100
    mar=temp2/len(game_data)*100
    return pick,mar
