import pandas as pd
import numpy as np
import itertools as it
import genericFunction as gf

# Calculate current stock value, call and put value and portfolio value
def calculateCurrentPortValue(sheet,stockName,callName,putName,callMaturity,putMaturity,n_day):
        
    for stock in stockName:
        sheet[str(stock)+'_sCurrentValue'] = sheet[str(stock)+'_CLOSE']*sheet[str(stock)+'_SHARE']
    for call,maturity in zip(callName,callMaturity):
        sheet[str(call)+'_cCurrentValue']=sheet[str(call)+'_CALL_PRICE_'+str(maturity)]*sheet[str(call)+'_CALL_SHARE']
    for put,maturity in zip(putName,putMaturity):
        sheet[str(put)+'_pCurrentValue']=sheet[str(put)+'_PUT_PRICE_'+str(maturity)]*sheet[str(put)+'_PUT_SHARE']
    stockCol = [name + '_sCurrentValue' for name in stockName]
    callCol = [name + '_cCurrentValue' for name in callName]
    putCol = [name + '_pCurrentValue' for name in putName]
    sheet['PORT_CurrentValue'] = sheet[stockCol+callCol+putCol].sum(1)

# Calculate call and put price after n_day using BS
def calculateFutureOptionPrice(sheet,callName,putName,callMaturity,putMaturity,r,n_day):    
    for (callUnderlying, maturity) in zip(callName,callMaturity):
        spot = sheet[str(callUnderlying)+'_CLOSE'].shift(n_day)
        spot_nextday = sheet[str(callUnderlying)+'_CLOSE'].shift(1)
        strike = sheet[str(callUnderlying)+'_CLOSE']
        vol = sheet[str(callUnderlying)+'_CALL_IMPVOL_'+str(maturity)].shift(n_day)/100.0
        vol_nextday = sheet[str(callUnderlying)+'_CALL_IMPVOL_'+str(maturity)].shift(1)/100.0
        sheet[str(callUnderlying)+'_FUTURE_CALL_PRICE_'+str(maturity)]\
        = gf.callBSM(spot,strike,r,vol,maturity/12.0-n_day/252.0)
        sheet[str(callUnderlying)+'_NextDay_CALL_PRICE_'+str(maturity)]\
        = gf.callBSM(spot_nextday,strike,r,vol_nextday,maturity/12.0-1/252.0)
    for (putUnderlying, maturity) in zip(putName,putMaturity):
        spot = sheet[str(putUnderlying)+'_CLOSE'].shift(n_day)
        spot_nextday = sheet[str(putUnderlying)+'_CLOSE'].shift(1)
        strike = sheet[str(putUnderlying)+'_CLOSE']
        vol = sheet[str(putUnderlying)+'_PUT_IMPVOL_'+str(maturity)].shift(n_day)/100.0
        vol_nextday = sheet[str(putUnderlying)+'_PUT_IMPVOL_'+str(maturity)].shift(1)/100.0
        sheet[str(putUnderlying)+'_FUTURE_PUT_PRICE_'+str(maturity)]\
        = gf.putBSM(spot,strike,r,vol,maturity/12.0-n_day/252.0)
        sheet[str(putUnderlying)+'_NextDay_PUT_PRICE_'+str(maturity)]\
        = gf.putBSM(spot_nextday,strike,r,vol_nextday,maturity/12.0-1/252.0)

# Calculate current stock value, call and put value and portfolio value after n_day

def calculateFuturePortValue(sheet,stockName,callName,putName,callMaturity,putMaturity,n_day):

    for stock in stockName:
        sheet[str(stock)+'_sFutureValue']=sheet[str(stock)+'_CLOSE'].shift(n_day)*sheet[str(stock)+'_SHARE']
        sheet[str(stock)+'_sNextDayValue']=sheet[str(stock)+'_CLOSE'].shift(1)*sheet[str(stock)+'_SHARE']
    for call,maturity in zip(callName,callMaturity):
        sheet[str(call)+'_cFutureValue']=sheet[str(call)+'_FUTURE_CALL_PRICE_'+str(maturity)]*sheet[str(call)+'_CALL_SHARE']
        sheet[str(call)+'_cNextDayValue']=sheet[str(call)+'_NextDay_CALL_PRICE_'+str(maturity)]*sheet[str(call)+'_CALL_SHARE']
    for put,maturity in zip(putName,putMaturity):
        sheet[str(put)+'_pFutureValue']=sheet[str(put)+'_FUTURE_PUT_PRICE_'+str(maturity)]*sheet[str(put)+'_PUT_SHARE']
        sheet[str(put)+'_pNextDayValue']=sheet[str(put)+'_NextDay_PUT_PRICE_'+str(maturity)]*sheet[str(put)+'_PUT_SHARE']
    stockCol = [name + '_sFutureValue' for name in stockName]
    callCol = [name + '_cFutureValue' for name in callName]
    putCol = [name + '_pFutureValue' for name in putName]
    sheet['PORT_FutureValue'] = sheet[stockCol+callCol+putCol].sum(1)
    stockCol = [name + '_sNextDayValue' for name in stockName]
    callCol = [name + '_cNextDayValue' for name in callName]
    putCol = [name + '_pNextDayValue' for name in putName]
    sheet['PORT_NextDayValue'] = sheet[stockCol+callCol+putCol].sum(1)

# Calibrate stock and portfolio weighted drift(mu) and volatility(sigma)

def calibrateMuSigma(sheet,stockName,years,lambdas):
    cols = ['lgrtnavg','lgrtnavg^2','lgrtnstd','mu','sigma']
    sheet['PORT_lgrtn']=np.log(sheet['PORT_NextDayValue']/sheet['PORT_CurrentValue']).shift(-1)
    for stock,year in it.product(stockName,years):
        sheet[str(stock)+'_lgrtn']=np.log(sheet[str(stock)+'_CLOSE']/sheet[str(stock)+'_CLOSE'].shift(-1))
    
    # cakcykate 
    for (year,lmbd) in zip(years,lambdas):
        sheet[str(year)+'']=np.power(lmbd,sheet.index)*(1-lmbd)
        sheet[str(year)+'']=sheet[str(year)+''].shift(3800)        
    for stock,col,year in it.product(stockName+['PORT'],cols,years):
            sheet[str(stock)+'_'+col+'_'+str(year)]=0
    for (stock,(year,lmbd)) in it.product(stockName+['PORT'],zip(years,lambdas)):
        sheet.ix[3800,str(stock)+'_'+'lgrtnavg'+'_'+str(year)]=np.sum(sheet[str(year)+''][3800:3800+year*252]*sheet[str(stock)+'_lgrtn'][3800:3800+year*252])
        sheet.ix[3800,str(stock)+'_'+'lgrtnavg^2'+'_'+str(year)]=np.sum(sheet[str(year)+''][3800:3800+year*252]*np.power(sheet[str(stock)+'_lgrtn'][3800:3800+year*252],2))
        for i in range(3800):
            sheet.ix[3799-i,str(stock)+'_'+'lgrtnavg'+'_'+str(year)]\
            =sheet.ix[3800-i,str(stock)+'_'+'lgrtnavg'+'_'+str(year)]*lmbd + sheet.ix[3799-i,str(stock)+'_lgrtn']*(1-lmbd)
            sheet.ix[3799-i,str(stock)+'_'+'lgrtnavg^2'+'_'+str(year)]\
            =sheet.ix[3800-i,str(stock)+'_'+'lgrtnavg^2'+'_'+str(year)]*lmbd + np.power(sheet.ix[3799-i,str(stock)+'_lgrtn'],2)*(1-lmbd)
        sheet.loc[:3801,str(stock)+'_'+'lgrtnstd'+'_'+str(year)]=np.sqrt(sheet.loc[:3801,str(stock)+'_'+'lgrtnavg^2'+'_'+str(year)]-np.power(sheet.loc[:3801,str(stock)+'_'+'lgrtnavg'+'_'+str(year)],2))
        sheet.loc[:3801,str(stock)+'_'+'mu'+'_'+str(year)]=(sheet.loc[:3801,str(stock)+'_'+'lgrtnavg'+'_'+str(year)]+0.5*np.power(sheet.loc[:3801,str(stock)+'_'+'lgrtnstd'+'_'+str(year)],2))*252
        sheet.loc[:3801,str(stock)+'_'+'sigma'+'_'+str(year)]=sheet.loc[:3801,str(stock)+'_'+'lgrtnstd'+'_'+str(year)]*np.sqrt(252)        

# Calculate the random term dWt and calibrate correlation matrix of dWt

def getdWt(daily_lgrtn,mu,sigma):
    return (daily_lgrtn - (mu-0.5*sigma**2)/252)/sigma

def calibrateCorrelation(sheet,year,stockName):
    for stock in stockName:
        sheet[stock+'_dWt_'+str(year)]\
        = getdWt(sheet[stock+'_lgrtn'],sheet[stock+'_mu_'+str(year)],sheet[stock+'_sigma_'+str(year)])           
    colsNeeded = [stock+'_dWt_'+str(year) for stock in stockName]
    rollingCorr = pd.rolling_corr(sheet[colsNeeded],window=252*year)
    return rollingCorr