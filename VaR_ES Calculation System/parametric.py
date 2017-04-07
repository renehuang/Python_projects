import numpy as np
import pandas as pd
from scipy.stats import norm
import itertools as it

# VaR and ES given GBM parameters
def LogNormalParametric_VaR_ES(value,mu,sigma,t,var_per,es_per):
    value_at_risk = value - value * np.exp(sigma*np.sqrt(t)*norm.ppf(1-var_per)+(mu-0.5*sigma*sigma)*t)
    expected_shortfall = value - value*np.exp(mu*t)*norm.cdf(norm.ppf(1-es_per)-sigma*np.sqrt(t))/(1-es_per)
    return (value_at_risk, expected_shortfall)

def parametric_VaR_ES_Calculation(inputdf,day_num,var_per,es_per,window_years,output_years):
    
    outputdf = pd.DataFrame()
    outputdf['DATE'] = inputdf['DATE'][:252*output_years]
    dollar = inputdf['port_cur_value'][:252*output_years]   
    for (window_year) in (window_years):
        mu = inputdf['PORT_mu_'+str(window_year)][:252*output_years]
        sigma = inputdf['PORT_sigma_'+str(window_year)][:252*output_years]    
        (outputdf['Parametric_VaR_'+str(window_year)]\
        ,outputdf['Parametric_ES_'+str(window_year)])\
        = LogNormalParametric_VaR_ES(dollar,mu,sigma,day_num/252.0,var_per, es_per)
    return outputdf