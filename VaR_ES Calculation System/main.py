import os
import pandas as pd
import numpy as np
from scipy.stats import norm
import itertools as it
import heapq

import parametric as pa
import montecarlo as mc
import historical as hi


# Places changed: 1 remove Calibration &gf
# 2. unweighted removed
# 3. Running time removed
# 4. Change fixed calculation period 10 years to user input
# 5. function d1 d2 deleted
# 6. ScanColumns() Function
# 7. curr_port_value() Function calculateFutureOptionValue() fut_port_value()
# 8. historical.py modified
# 9. Correlation deleted in montecarlo


# Set global variables
var_per = 0.99
es_per = 0.975
windows = [2]
testyears = [5]
lambdas = [0.9976]
rr = 0.005
day_num = 5.0
path_num = 1000
np.random.seed(123)

# Set input path and get all the input data
inputPath = os.getcwd()+'\\inputs\\'
fileNames = os.listdir(inputPath)

# Folder name is based on start running time
outputFolderName = "TestResult"

# Print out the files that we are working on
print "Going to work on "+fileNames









# To transform [str1, str2, str3, ...] into str1_str2_str3...
def stringCombine(inputlist,seg='_'):
    output = str(inputlist[0])    
    for string in inputlist[1:]:
        output = output +'_'+str(string)
    return output

# Get the stocks' name, c and p's underlying name
def scanColumns(df):
    ticker=[]
    c_name=[]
    p_name=[]
    cT=[]
    pT=[]
    for name in df.columns:
        if 'close' in name:
            ticker.append(name.split('_')[0])
        if 'c_px' in name:
            c_name.append(name.split('_')[0])
        if 'p_px' in name:
            p_name.append(name.split('_')[0])
        if 'c_px' in name:
            cT.append(name.split('_')[-1])
        if 'p_px' in name:
            pT.append(name.split('_')[-1])
    return ticker, c_name, p_name, cT, pT



# Basic BSM Functions
# BSM_c is the price of c option given parameters, the same as BSM_p
def BSM_c(spot,strike,mu,vol,maturity):
    return spot*norm.cdf(np.log(spot/strike)+(mu+0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))-strike*np.exp(-mu*maturity)*norm.cdf(np.log(spot/strike)+(mu-0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity))

def BSM_p(spot,strike,mu,vol,maturity):
    return -spot*norm.cdf(-(np.log(spot/strike)+(mu+0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity)))+strike*np.exp(-mu*maturity)*norm.cdf(-(np.log(spot/strike)+(mu-0.5*vol*vol)*maturity)/(vol*np.sqrt(maturity)))





# Functions using for Calibration
# Calculate current stock value, c and p value and portfolio value


# remove zip
# not sure about the syntax
def curr_port_value(df,ticker,c_name,p_name,c_maturity,p_maturity,day_num):
    stock_col=[]
    c_col=[]
    p_col=[]
    for stock in ticker:
        df[str(stock)+'_s_cur_value'] = df[str(stock)+'_close']*df[str(stock)+'_share']
        stock_col.append[str(stock)+'_s_cur_value']
    for c in c_name:
        for maturity in c_maturity:
            df[str(c)+'_c_cur_value']=df[str(c)+'_c_px_'+str(maturity)]*df[str(c)+'_c_share']
            c_col.append[str(c)+'_s_cur_value']
    for p in p_name:
        for maturity in p_maturity:
            df[str(p)+'_p_cur_value']=df[str(p)+'_p_px_'+str(maturity)]*df[str(p)+'_p_share']
            p_col.append[str(p)+'_s_cur_value']
            
#    stock_col = [name + '_s_cur_value' for name in ticker]
#    c_col = [name + '_c_cur_value' for name in c_name]
#    p_col = [name + '_p_cur_value' for name in p_name]
    df['port_cur_value'] = df[stock_col+c_col+p_col].sum(1)

# Calculate c and p price after day_num using BS

def fut_op_px(df,c_name,p_name,c_maturity,p_maturity,r,day_num):    
    for c_underlying in c_name:
        for maturity in c_maturity:
            spot = df[str(c_underlying)+'_close'].shift(day_num)
            spot_next = df[str(c_underlying)+'_close'].shift(1)
            strike = df[str(c_underlying)+'_close']
            vol = df[str(c_underlying)+'_c_imp_vol_'+str(maturity)].shift(day_num)/100.0
            vol_next = df[str(c_underlying)+'_c_imp_vol_'+str(maturity)].shift(1)/100.0
            df[str(c_underlying)+'_fut_c_px'+str(maturity)]\
            = BSM_c(spot,strike,r,vol,maturity/12.0-day_num/252.0)
            df[str(c_underlying)+'_next_c_px_'+str(maturity)]\
            = BSM_c(spot_next,strike,r,vol_next,maturity/12.0-1/252.0)
    for p_underlying in p_name:
        for maturity in p_maturity:
            spot = df[str(p_underlying)+'_close'].shift(day_num)
            spot_next = df[str(p_underlying)+'_close'].shift(1)
            strike = df[str(p_underlying)+'_close']
            vol = df[str(p_underlying)+'_p_imp_vol_'+str(maturity)].shift(day_num)/100.0
            vol_next = df[str(p_underlying)+'_p_imp_vol_'+str(maturity)].shift(1)/100.0
            df[str(p_underlying)+'_fut_p_px_'+str(maturity)]\
            = BSM_p(spot,strike,r,vol,maturity/12.0-day_num/252.0)
            df[str(p_underlying)+'_next_p_px_'+str(maturity)]\
            = BSM_p(spot_next,strike,r,vol_next,maturity/12.0-1/252.0)

# Calculate current stock value, c and p value and portfolio value after day_num
# Same structure as changing curr_port_value

def fut_port_value(df,ticker,c_name,p_name,c_maturity,p_maturity,day_num):
    fut_stock_col=[]
    fut_c_col=[]
    fut_p_col=[]
    next_stock_col=[]
    next_c_col=[]
    next_p_col=[]

    for stock in ticker:
        df[str(stock)+'_s_fut_value']=df[str(stock)+'_close'].shift(day_num)*df[str(stock)+'_share']
        df[str(stock)+'_s_next_value']=df[str(stock)+'_close'].shift(1)*df[str(stock)+'_share']
        fut_stock_col.append[str(stock)+'_s_fut_value']
        next_stock_col.append[str(stock)+'_s_next_value']
    for c in c_name:
        for maturity in c_maturity:
            df[str(c)+'_c_fut_value']=df[str(c)+'_fut_c_px'+str(maturity)]*df[str(c)+'_c_share']
            df[str(c)+'_c_next_value']=df[str(c)+'_next_c_px_'+str(maturity)]*df[str(c)+'_c_share']
            fut_c_col.append[str(c)+'_s_fut_value']
            next_c_col.append[str(c)+'_s_next_value']   
    for p in p_name:
        for maturity in p_maturity:
            df[str(p)+'_p_fut_value']=df[str(p)+'_fut_p_px_'+str(maturity)]*df[str(p)+'_p_share']
            df[str(p)+'_p_next_value']=df[str(p)+'_next_p_px_'+str(maturity)]*df[str(p)+'_p_share']
            fut_p_col.append[str(p)+'_s_fut_value']
            next_p_col.append[str(p)+'_s_next_value']
        
    df['port_fut_value'] = df[fut_stock_col+fut_c_col+fut_p_col].sum(1)
    df['port_next_value'] = df[next_stock_col+next_c_col+next_p_col].sum(1)

# Calibrate stock and portfolio weighted drift(mu) and volatility(sigma)
# any other way to compe Mu or Sigma ???


def est_mu_sigma(df,ticker,years,lambdas):
    cols = ['avg_lg_rtn','avg_lg_rtn_sq','std_lg_rtn','mu','sigma']
    df['port_lg_rtn']=np.log(df['port_next_value']/df['port_cur_value']).shift(-1)
    for stock,year in it.product(ticker,years):
        df[str(stock)+'_lg_rtn']=np.log(df[str(stock)+'_close']/df[str(stock)+'_close'].shift(-1))
    
    # cakcykate 
    for (year,lmbd) in zip(years,lambdas):
        df[str(year)+'']=np.power(lmbd,df.index)*(1-lmbd)
        df[str(year)+'']=df[str(year)+''].shift(3800)        
    for stock,col,year in it.product(ticker+['port'],cols,years):
            df[str(stock)+'_'+col+'_'+str(year)]=0
    for (stock,(year,lmbd)) in it.product(ticker+['port'],zip(years,lambdas)):
        df.ix[3800,str(stock)+'_'+'avg_lg_rtn'+'_'+str(year)]=np.sum(df[str(year)+''][3800:3800+year*252]*df[str(stock)+'_lg_rtn'][3800:3800+year*252])
        df.ix[3800,str(stock)+'_'+'avg_lg_rtn_sq'+'_'+str(year)]=np.sum(df[str(year)+''][3800:3800+year*252]*np.power(df[str(stock)+'_lg_rtn'][3800:3800+year*252],2))
        for i in range(3800):
            df.ix[3799-i,str(stock)+'_'+'avg_lg_rtn'+'_'+str(year)]\
            =df.ix[3800-i,str(stock)+'_'+'avg_lg_rtn'+'_'+str(year)]*lmbd + df.ix[3799-i,str(stock)+'_lg_rtn']*(1-lmbd)
            df.ix[3799-i,str(stock)+'_'+'avg_lg_rtn_sq'+'_'+str(year)]\
            =df.ix[3800-i,str(stock)+'_'+'avg_lg_rtn_sq'+'_'+str(year)]*lmbd + np.power(df.ix[3799-i,str(stock)+'_lg_rtn'],2)*(1-lmbd)
        df.loc[:3801,str(stock)+'_'+'std_lg_rtn'+'_'+str(year)]=np.sqrt(df.loc[:3801,str(stock)+'_'+'avg_lg_rtn_sq'+'_'+str(year)]-np.power(df.loc[:3801,str(stock)+'_'+'avg_lg_rtn'+'_'+str(year)],2))
        df.loc[:3801,str(stock)+'_'+'mu'+'_'+str(year)]=(df.loc[:3801,str(stock)+'_'+'avg_lg_rtn'+'_'+str(year)]+0.5*np.power(df.loc[:3801,str(stock)+'_'+'std_lg_rtn'+'_'+str(year)],2))*252
        df.loc[:3801,str(stock)+'_'+'sigma'+'_'+str(year)]=df.loc[:3801,str(stock)+'_'+'std_lg_rtn'+'_'+str(year)]*np.sqrt(252)        



# Calculate the random term dWt (increment equals one day) and calibrate correlation matrix of dWt

def getdWt(daily_lg_rtn,mu,sigma):
    return (daily_lg_rtn - (mu-0.5*sigma*sigma)/252)/sigma















# Start Working!#
print "======== Start Running ========"
# Calculate VaR and ES in different methods for different input
for fileName in fileNames:
    
    # Set output path and generate folders for output storage
    outputPath = os.getcwd()+'\\outputs\\'+outputFolderName+'\\'+fileName+'\\'
    if not os.path.isdir(outputPath):
        os.makedirs(outputPath)
    
    # Load data from input path  
    inputFile = pd.read_csv(inputPath+fileName)
    inputFile['DATE']=pd.to_datetime(inputFile['DATE'])
    
    # Scan column names of input data and read asset class and name    

    stock_list, c_list, p_list, cT, pT = scanColumns(inputFile)

        
    # Step 1 Calculate prerequisite parameters or values
    print ">>>>>>>> Calibration Process of " + fileName +" is working. >>>>>>>>"    
    curr_port_value(inputFile,stock_list,c_list,p_list,cT,pT,day_num)
    fut_op_px(inputFile,c_list,p_list,cT,pT,rr,day_num)
    fut_port_value(inputFile,stock_list,c_list,p_list,cT,pT,day_num)        
    est_mu_sigma(inputFile,stock_list,windows,lambdas)
            
    print "======== Calibration Process of " + fileName +" is done. ========"

    # Step 2 Calculate historical VaR/ES and save it in 'output' folders
    historical_var_es_df = pd.DataFrame()
    inputFile['port_loss'] = inputFile['port_cur_value']-inputFile['port_fut_value']    
    print ">>>>>>>> Historical VaR/ES Calculation Process of " + fileName +" is working. >>>>>>>>"
    historical_var_es_df = hi.historical_VaR_ES_Calculation(inputFile,windows,testyears,var_per,es_per, day_num)
    print "======== Historical VaR/ES calculation  of " + fileName + " is done. ========"

    
    # Step 3 Calculate parametric VaR/ES and save it to 'output' folders
    parametric_var_es_df = pd.DataFrame()    
    print ">>>>>>>> Parametric VaR/ES Calculation Process of " + fileName +" is working. >>>>>>>>"
    parametric_var_es_df = pa.parametric_VaR_ES_Calculation(inputFile,day_num,var_per,es_per,windows, testyears)
    print "======== Parametric VaR/ES calculation is done. ========"

    # Step 4 calculate Monte Carlo VaR/ES and save it in 'output' folders
    montecarlo_var_es_df = pd.DataFrame()
    print ">>>>>>>> MonteCarlo VaR/ES Calculation Process of " + fileName +" is working. >>>>>>>>"
    montecarlo_var_es_df = mc.monteCarlo_VaR_ES_Calculation(inputFile,rr,day_num,var_per,es_per,windows,path_num,stock_list,c_list,p_list,cT,pT, testyears)
    print "======== MonteCarlo VaR/ES calculation is done. ========"

    # Step 5 Merge 3 kinds of methods' results and portfolio day_num loss together using the common key 'DATE'
    VaR_ES_df = inputFile[['DATE','port_loss']][:252*testyears]
    VaR_ES_df = pd.merge(left = VaR_ES_df, right = historical_var_es_df)
    VaR_ES_df = pd.merge(left = VaR_ES_df, right = parametric_var_es_df)
    VaR_ES_df = pd.merge(left = VaR_ES_df, right = montecarlo_var_es_df)
    VaR_ES_df.to_csv(outputPath+"VaR & ES.csv",index = False)

    # Step 6 Backest VaR
    # further implement the Backtest???
    day_num = int(day_num)
    VaR_cols = [column for column in VaR_ES_df.columns if 'VaR' in column]
    compareResult = (np.array(VaR_ES_df[VaR_cols][day_num:])>np.array(VaR_ES_df['port_loss'][day_num:]).reshape(2520-day_num,1)).mean(axis=0)
    compareResult = pd.DataFrame(compareResult, index=VaR_cols, columns = ['loss_under_VaR_rate'])
    compareResult.to_csv(outputPath+"VaR_Backtesting.csv",index=True)

print ""
print "======== Running successfully ========"

