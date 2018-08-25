# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 14:56:29 2018

@author: 한승표
주제: svxy pricing 모델 공부
프라이싱 방법론 출처: 
#http://investing.kuchita.com/2014/05/11/svxy-historical-data-and-pricing-model-since-vix-futures-are-available-2004/
#http://investing.kuchita.com/2011/08/16/how-the-vxx-is-calculated-and-why-backwardation-amplfies-it/

SVXY: 시작- 근원물만 매도, 다음날부터 2nd 선물 매도, 1st 선물 매수(매도량 줄여나가는)-->즉 계속 1st, 2nd 매도
1. R(n) = (n-1)~n일까지 1st, 2nd VIX 선물 매도 포지션 Combination 홀딩 시 얻는 수익
2. SVXY(n+1) = SVXY(n)+SVXY(n)*R(n+1) --> 추정
   SVXY(n+1)_market =SVXY(n+1)*F --> 일일 트레킹 에러

VXX pricing model
VXX(t) = (p1(t)*n1(t)+p2(t)*n2(t))/c(t)   
p1: 1st Futures Price, p2: 2nd Futures price
n1: number of 1st Futrues contracts, n2 : number of 2nd futrues contracts
r: the number of remaining days until the expiration of the first future

n2(t+1) = n2(t)+(n1(t)/r)*(p1(t)/p2(t))
n1(t+1) = n1(t)-n1(t)/r(t) --> last day의 잔존 만기일. 
c(t+1) = (n1(t)*p1(t)+n2(t)*p2(t))/VXX_M(t)
Q: 1st와 2nd를 결합하여 잔존 만기를 계속 1M를 유지해야하는데, 위의 공식으로하면 유지가 되는가? 
yes 그거를 맞춰주는 공식인듯
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import pandas as pd
import os
from  datetime import datetime
os.chdir('C:\\Users\한승표\Desktop\SVXY조사')
tot_data = pd.read_excel('vix-funds-models-no-formulas.xls', sheetname = 'Models', index_col = 0)
cal_data = pd.read_excel(r'vix-funds-models-no-formulas.xls', sheetname = 'cal_vxx', index_col = 0)

#%%1.VXX pricng
#n1. n2 구하기
# 매달 3번째 수요일에 리셋.--> r=1이면 다음날에 리셋하는 것으로 코딩
# n2=0으로 시작, n1 값은 랜덤하게. -> 랜덤하게 어떻게 추출? 직전일의 합 = n1도록 코딩

for i in range(len(cal_data)-1):
    if cal_data.iloc[:,-2][i] ==1:
        cal_data.iloc[:,3][i+1] =0
        cal_data.iloc[:,2][i+1] = cal_data.iloc[:,4][i-1]
        cal_data.iloc[:,4][i] = cal_data.iloc[:,2][i]+cal_data.iloc[:,3][i]
    if cal_data.iloc[:,-2][i] != 1:
        cal_data.iloc[:,2][i+1] = cal_data.iloc[:,2][i]-(cal_data.iloc[:,2][i]/cal_data.iloc[:,-2][i]) #n1(t+1)
        cal_data.iloc[:,3][i+1] = cal_data.iloc[:,3][i]+(cal_data.iloc[:,2][i]/cal_data.iloc[:,-2][i])*(cal_data.iloc[:,0][i]/cal_data.iloc[:,1][i]) #n2(t+1)
        cal_data.iloc[:,4][i] = cal_data.iloc[:,2][i]+cal_data.iloc[:,3][i]
        continue

#c, vxx 값 구하기
for i in range(len(cal_data)-1):
    cal_data.iloc[:,6][i] = (cal_data.iloc[:,2][i]*cal_data.iloc[:,0][i]+cal_data.iloc[:,3][i]*cal_data.iloc[:,1][i])/cal_data.iloc[:,-1][i]
    cal_data.iloc[:,-1][i+1] = (cal_data.iloc[:,2][i]*cal_data.iloc[:,0][i]+cal_data.iloc[:,3][i]*cal_data.iloc[:,1][i])/cal_data.iloc[:,-3][i]


#backwardation or contango
bacwardation = 0
contango = 0
for i in range(len(cal_data)-1):
    if cal_data.iloc[:,0][i]/cal_data.iloc[:,1][i]>1 :
        bacwardation = bacwardation+1
    elif cal_data.iloc[:,0][i]/cal_data.iloc[:,1][i]<1:
        contango = contango +1


#%%SVXY pricing# n1,n2구하기
#cal_data_svxy = pd.read_excel(r'vix-funds-models-no-formulas.xls', sheetname = 'cal_svxy', index_col = 0)
cal_data_svxy = cal_data.copy()
cal_data_svxy.rename(columns={'vxx':'ret','VXX market':'svxy'}, inplace=True)
cal_data_svxy.iloc[:,-3][0] = 5.75 #블로그에서 알려준 첫 설정 값
#n1,n2 값 구하기(vxx와 반대)
cal_data_svxy.iloc[:,2] = cal_data_svxy.iloc[:,2] *(-1)
cal_data_svxy.iloc[:,3] = cal_data_svxy.iloc[:,3]*(-1)
cal_data_svxy.iloc[:,4] = cal_data_svxy.iloc[:,2]+cal_data_svxy.iloc[:,3]

#선물 holding 하면서 얻는 ret
for i in range(len(cal_data_svxy)-1):
    cal_data_svxy.iloc[:,6][i] = (cal_data_svxy.iloc[:,2][i]*cal_data_svxy.iloc[:,0][i]+cal_data_svxy.iloc[:,3][i]*cal_data_svxy.iloc[:,1][i])
 
cal_data_svxy['ret'] = -cal_data_svxy['ret'].pct_change()

#svxy(n+1) = svxy(n) + svxy(n)*r(n+1)
for i in range(len(cal_data_svxy)-1):
    cal_data_svxy.iloc[:,-3][i+1] = cal_data_svxy.iloc[:,-3][i]*(1+cal_data_svxy.iloc[:,6][i+1])
#tracking error
