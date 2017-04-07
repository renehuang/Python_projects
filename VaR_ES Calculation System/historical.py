import pandas as pd
import numpy as np
import heapq

# Calculate Historical VaR / ES
    
def historical_VaR_ES_Calculation(df,window_years,output_years,var_per,es_per,day_num):
    outputdf = pd.DataFrame()  
    outputdf['DATE'] = df['DATE'][:252*output_years]
    npts=252*window_years
    npaths = npts- day_num
    ntrails=252*output_years
    port_n_rtn=np.log(df['port_cur_value']/(df['port_cur_value'].shift(-5)))
    port_value = 10000 * np.exp(port_n_rtn)
    
    scenario=[]
    for i in range(ntrails):
        scenario.append(port_value[i:i+npaths-1])
    
    # sort the matrix by column
    scenario = np.msort(scenario)
    
    for i in range(252*output_years):
        # VaR
        outputdf.ix[i,'Historical_VaR_'] = df.ix[i,'port_cur_value']-scenario[np.ceil((1-var_per)*npaths),:]
        # ES
        outputdf.ix[i,'Historical_ES_'] = df.ix[i,'PORT_CurrentValue']-mean(scenario[1:np.ceil((1-es_per)*npaths),:])
