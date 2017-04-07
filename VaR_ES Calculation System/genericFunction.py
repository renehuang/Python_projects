import numpy as np
from scipy.stats import norm

# callBSM is the price of call option given parameters, the same as putBSM
def d1(spot,strike,mu,vol,maturity):
    return (np.log(spot/strike)+(mu+0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))

def d2(spot,strike,mu,vol,maturity):
    return (np.log(spot/strike)+(mu-0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))

def callBSM(spot,strike,mu,vol,maturity):
    return spot*norm.cdf(d1(spot,strike,mu,vol,maturity))-strike*np.exp(-mu*maturity)*norm.cdf(d2(spot,strike,mu,vol,maturity))

def putBSM(spot,strike,mu,vol,maturity):
    return -spot*norm.cdf(-d1(spot,strike,mu,vol,maturity))+strike*np.exp(-mu*maturity)*norm.cdf(-d2(spot,strike,mu,vol,maturity))

# To transform [str1, str2, str3, ...] into str1_str2_str3...
def stringCombine(anylist,seg='_'):
    output = str(anylist[0])    
    for string in anylist[1:]:
        output = output +'_'+str(string)
    return output

# Get the stocks' name, call and put's underlying name
def scanColumns(sheet):
    stockName = [name.split('_')[0] for name in sheet.columns if'CLOSE' in name]
    callName = [name.split('_')[0] for name in sheet.columns if 'CALL_PRICE' in name]
    putName = [name.split('_')[0] for name in sheet.columns if 'PUT_PRICE' in name]
    callT = [int(name.split('_')[-1]) for name in sheet.columns if 'CALL_PRICE' in name]
    putT = [int(name.split('_')[-1]) for name in sheet.columns if 'PUT_PRICE' in name]
    return stockName, callName, putName, callT, putT


