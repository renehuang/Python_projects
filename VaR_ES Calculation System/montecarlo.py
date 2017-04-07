import numpy as np
import pandas as pd
from scipy.stats import norm
from heapq import nlargest



# Basic BSM Functions
# BSM_c is the price of c option given parameters, the same as BSM_p
def BSM_c(spot,strike,mu,vol,maturity):
    return spot*norm.cdf(np.log(spot/strike)+(mu+0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))-strike*np.exp(-mu*maturity)*norm.cdf(np.log(spot/strike)+(mu-0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))

def BSM_p(spot,strike,mu,vol,maturity):
    return -spot*norm.cdf(-(np.log(spot/strike)+(mu+0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity)))+strike*np.exp(-mu*maturity)*norm.cdf(-(np.log(spot/strike)+(mu-0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity)))



def stock_px_generator(stock_px_s,ticker,mus,sigmas,day_num,path_num):
    
    rows = len(stock_px_s)
    cols = len(stock_px_s.columns)
    t = day_num/252.0
    W = np.random.randn(rows,cols,path_num)    
    
    simulation_stock_px_s = pd.Panel(major_axis=ticker,minor_axis=range(path_num))
    for i in range(len(W)):
        stock_px = np.array(stock_px_s)[[i]].T
        mu = np.array(mus)[[i]].T
        sigma = np.array(sigmas)[[i]].T
        simulation_stock_px = pd.DataFrame(data=stock_px*np.exp((mu-0.5*sigma*sigma)*t+sigma*np.sqrt(t)*W[i]),index=ticker)
        simulation_stock_px_s[i]=simulation_stock_px
        
    # returned result is a pandas panel
    # observationDays * stockNumber * path_num   
    return simulation_stock_px_s

def simulation_loss_calculator(original_value,original_stock_px_s,simulated_stock_px_s,stock_shares,c_name,c_shares,p_name,p_shares,rr,c_imp_vols,p_imp_vols,c_maturity,p_maturity,day_num):

    # Only pick stocks with c/p in portfolio for BS pricing, and numpy array-ize inp    
    c_spot = np.array(simulated_stock_px_s.ix[:,c_name,:])
    c_strike = np.array(original_stock_px_s.ix[:,[c+'_close' for c in c_name]])
    c_imp_vols = np.array(c_imp_vols)
    c_maturity = np.array(c_maturity).reshape(1,len(c_name))
    c_shares = np.array(c_shares)
    p_spot = np.array(simulated_stock_px_s.ix[:,p_name,:])
    p_strike = np.array(original_stock_px_s.ix[:,[p+'_close' for p in p_name]])
    p_imp_vols = np.array(p_imp_vols)
    p_maturity = np.array(p_maturity).reshape(1,len(p_name))
    p_shares = np.array(p_shares)
    stock_shares = np.array(stock_shares)
    
    simulated_stock_px_s = np.array(simulated_stock_px_s).swapaxes(0,1).swapaxes(0,2)
    c_spot = c_spot.swapaxes(0,1).swapaxes(0,2)
    p_spot = p_spot.swapaxes(0,1).swapaxes(0,2)
    simulated_c_px = BSM_c(c_spot,c_strike,rr,c_imp_vols/100,c_maturity/12.0-day_num/252.0)
    simulated_p_px = BSM_p(p_spot,p_strike,rr,p_imp_vols/100,p_maturity/12.0-day_num/252.0)
    
    c_value = (c_shares * simulated_c_px).sum(axis=2)
    p_value = (p_shares * simulated_p_px).sum(axis=2)
    stock_value = (stock_shares * simulated_stock_px_s).sum(axis=2)

    return original_value - (c_value + p_value + stock_value)


def monteCarlo_VaR_ES_Calculation(df,rr,day_num,var_per,es_per,path_num,ticker,c_name,p_name,c_maturity,p_maturity, output_years):

    obs_days = 252*output_years
    outputdf = pd.DataFrame()
    outputdf['DATE']=df['DATE'][:obs_days]

    stock_px_cols =[]
    stock_share_cols =[]
    c_share_cols =[]
    c_imp_vol_cols =[]
    p_share_cols =[]
    p_imp_vol_cols = []    
    
    for stock in ticker:
        stock_px_cols.append(df[stock+'_close'])
    for stock in ticker:
        stock_share_cols.append(df[stock+'_share'])
    for c in c_name:
        c_share_cols.append(df[c+'_c_share'])
    for c in c_name:
        for maturity in c_maturity:
            c_imp_vol_cols.append(df[c+'_c_imp_vol_'+str(maturity)])       
    for p in p_name:
        p_share_cols.append(df[p+'_p_share'])
    for p in p_name:
        for maturity in p_maturity:
            p_imp_vol_cols.append(df[p+'_p_imp_vol_'+str(maturity)])
    original_value = df.ix[0,'port_cur_value']
    
    
    # for year in [2, 5]
    year=[2]                 
    nth_var = int(252*year*(1-var_per))
    nth_var = max([1,nth_var])
    nth_es = int(252*year*(1-es_per))
    nth_es = max([1,nth_es])
     
    for stock in ticker:
        stock_mu_cols = df[[stock+'_mu_'+str(year) for stock in ticker]]
        stockSigmaCols = df[[stock+'_sigma_'+str(year) for stock in ticker]]
        
        # Gather all parameters

        stock_px_s = stock_px_cols[:obs_days]
        stock_shares = stock_share_cols[:obs_days]
        c_shares  = c_share_cols[:obs_days]
        p_shares = p_share_cols[:obs_days]
        c_imp_vols = c_imp_vol_cols[:obs_days]
        p_imp_vols = p_imp_vol_cols[:obs_days]
        mus = stock_mu_cols[:obs_days]
        sigmas = stockSigmaCols[:obs_days]
        
        # Generate simulated_ day_num later stock price
        simulated_stock_px_s = stock_px_generator(stock_px_s,ticker,mus,sigmas,day_num,path_num)
        
        # Given stock price, calculate option price and portfolio loss in the future
        simulated_loss = simulation_loss_calculator(original_value,stock_px_s,simulated_stock_px_s,stock_shares,c_name,c_shares,p_name,p_shares,rr,c_imp_vols,p_imp_vols,c_maturity,p_maturity,day_num)
        
        # Calculate VaR and ES using heap sort????????
        nth_var_largest = lambda array: nlargest(nth_var,array)[-1]
        nth_es_mean = lambda array: np.array((nlargest(nth_es,array))).mean()
        value_at_risk = np.apply_along_axis(nth_var_largest,axis=0,arr=simulated_loss)
        expected_shortfall = np.apply_along_axis(nth_es_mean,axis=0,arr=simulated_loss)
                    
        outputdf['MonteCarlo_VaR_'+str(year)] = pd.Series(value_at_risk)
        outputdf['MonteCarlo_ES_'+str(year)] = pd.Series(expected_shortfall)
    
    return outputdf