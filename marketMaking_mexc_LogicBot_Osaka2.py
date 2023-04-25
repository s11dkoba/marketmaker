#!/usr/bin/env python
# coding: utf-8

# In[4]:


#!/usr/bin/env python
# coding: utf-8

#オーダー創設

import hashlib
import hmac
import requests
import datetime
import json
import base64
import time
import urllib.parse
import random
from pycoingecko import CoinGeckoAPI
import operator
import pprint
import pandas as pd
import ccxt
from pprint import pprint

#-----------全体の変数-----------
# APIキー＆シークレットキー
API_KEY    = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"

# MEXCのインスタンス作成
mexc = ccxt.mexc({'apiKey':API_KEY,'secret':SECRET_KEY})

market_pair='XWIN_USDT'
hurdle_ratio=0.15

#-----------提示レート決定-----------
if True:
    cg = CoinGeckoAPI()
    xwin=cg.get_price(ids='xwin-finance', vs_currencies=['usd', 'btc'])['xwin-finance']['usd']  
    xwin_address='0xd88ca08d8eec1e9e09562213ae83a7853ebb5d28'
    busd_address='0xe9e7cea3dedca5984780bafc599bd69add087d56'
    sxp_address='0x47bead2563dcbf3bf2c9407fea4dc236faba485a'
    btcb_address='0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c'

    maisu =50
    maisu =10**18*maisu
    num = str(maisu)
    pathOneinch_url="https://api.1inch.exchange/v3.0/56/quote?fromTokenAddress="
    r = requests.get(pathOneinch_url + busd_address + "&toTokenAddress=" + xwin_address + "&amount=" + num)
    j = r.json()
    Buy_Price=float(j["fromTokenAmount"])/float(j["toTokenAmount"])

    r = requests.get(pathOneinch_url+ xwin_address + "&toTokenAddress=" + busd_address + "&amount=" + num)
    j = r.json()
    Sell_Price=float(j["toTokenAmount"])/float(j["fromTokenAmount"])

    #1inchの買いオーダー    
    if xwin*(1-hurdle_ratio) <= Buy_Price < xwin*(1+hurdle_ratio)and Sell_Price < Buy_Price*(1+hurdle_ratio*.2) :
        Buy_Price=round(Buy_Price,4)
    Buy_Price_text=str(Buy_Price)

    #1inchの売りオーダー
    if xwin*(1-hurdle_ratio) <= Sell_Price < xwin*(1+hurdle_ratio) and Sell_Price < Buy_Price*(1+hurdle_ratio*.2) :
        Sell_Price=round(Sell_Price,4)
    Sell_Price_text=str(Sell_Price)
    
    #基準価格の決定
    SpreadMean=(Buy_Price+Sell_Price)/2
    Buy_Base_Rate=max(Buy_Price,SpreadMean)
    Sell_Base_Rate=min(Sell_Price,SpreadMean)

    half_spread1=0.0015  #basis
    price_skew=0.0006  #絶対額
    scale_factor=0.0134  #basis
    
    crypto_ask=max(Buy_Base_Rate,SpreadMean*(1+half_spread1))+price_skew+round(random.uniform(-0.0029,0.0049),4)
    crypto_bid=min(Sell_Base_Rate,SpreadMean*(1-half_spread1))+price_skew-round(random.uniform(-0.0029,0.0049),4)

    New_Ask= crypto_ask+0.84
    New_Bid= crypto_bid-0.84
    print(New_Ask)
    print(New_Bid)
    

# 注文照会
trade_info = mexc.fetchOpenOrders(symbol = market_pair, since = 0, limit = 50)
#print(trade_info[0])
# 出力
#for num in range(len(trade_info)):
#    pprint(str(trade_info[num]['timestamp']) + ' ' + trade_info[num]['side'] + ' ' + str(trade_info[num]['price'])+ ' ' + str(trade_info[num]['amount']))
result1 = sorted(trade_info, key=lambda k: k['price'], reverse=True)
print('-----------------------')

order_num=int(len(result1)/2)
Order_frame = pd.DataFrame( columns=['Num','price','side','amount','OrderID'] )
for result2 in range(0,order_num*2):
    price=str(result1[result2]['price'])
    side=result1[result2]['side']
    amount=str(result1[result2]['amount'])
    orderID=str(result1[result2]['id'])
    
    if result2<order_num:
        print(str(order_num-result2-1) + ' ' + price + ' ' + side + ' ' + amount + ' ' + orderID)
    else:
        print(str(result2-order_num) + ' ' + price + ' ' + side + ' ' + amount + ' ' + orderID) 


        
result1 = sorted(trade_info, key=lambda k: k['price'], reverse=True)
order_num=int(len(result1)/2)
Order_frame = pd.DataFrame( columns=['Num','price','side','amount','OrderID'] )
for result2 in range(0,order_num*2):
    price=result1[result2]['price']
    side=result1[result2]['side']
    amount=result1[result2]['amount']
    orderID=str(result1[result2]['id'])
    if result2<order_num:
        tmp_se = pd.Series( [ order_num-result2-1, float(price), side, amount, orderID ], index=Order_frame.columns )
        Order_frame = Order_frame.append( tmp_se, ignore_index=True )
    else:
        tmp_se = pd.Series( [ result2-order_num, float(price), side, amount, orderID ], index=Order_frame.columns )
        Order_frame = Order_frame.append( tmp_se, ignore_index=True )
        
        
print(Order_frame.query('price < @New_Ask & side == "sell"'))
OrderID_ask=Order_frame.query('price < @New_Ask & side == "sell"')['OrderID']
print(len(OrderID_ask))
print(Order_frame.query('price > @New_Bid & side == "buy"'))
OrderID_bid=Order_frame.query('price > @New_Bid & side == "buy"')['OrderID']
print(len(OrderID_bid))
print(OrderID_bid)
print('------------------------------------')
    
#-----------キャンセル-----------
for o_id in OrderID_ask:
    #①キャンセルの内容（ボディ）
    cancel_order = mexc.cancel_order(symbol = market_pair,  # 取引通貨
                                     id = o_id,    # 注文ID
                                    )
for o_id in OrderID_bid:
    #①キャンセルの内容（ボディ）
    cancel_order = mexc.cancel_order(symbol = market_pair,  # 取引通貨
                                     id = o_id,    # 注文ID
                                    )

for counter1 in range(0,1):
    crypto_ask=crypto_ask*(1+scale_factor)
    amount=str(round(random.uniform(40,62.5),1))
    if counter1 == 0:
        amount=str(round(random.uniform(24.6,29.9),1))
    else:
        crypto_ask=crypto_ask*(1+scale_factor)
        amount=str(round(random.uniform(38,67.5),1)) #'0.1'

    #①発注の内容（ボディ）--------------------------------------
    crypto_ask = "{:.3}".format(crypto_ask-0.02)
    order_string=str(crypto_ask)
    crypto_ask = float(crypto_ask)
    order = mexc.createLimitOrder(
                    symbol = market_pair,   # 取引通貨
                    price  = order_string,  # 指値価格
                    side   = 'sell',        # 購入(buy) or 売却(sell)
                    amount = amount,        # 購入数量[XWIN]
                    )

for counter in range(0,1): #len(OrderID_bid)+1
    if counter==0:
        amount=str(round(random.uniform(24.6,29.9),1))
    if counter!=0:
        crypto_bid=crypto_bid*(1-scale_factor)
        amount=str(round(random.uniform(38,67.5),1)) #'0.1'
    #①発注の内容（ボディ）--------------------------------------
    crypto_bid = "{:.3}".format(crypto_bid+0.04)
    order_string=str(crypto_bid)
    crypto_bid = float(crypto_bid)
    order = mexc.createLimitOrder(
                    symbol = market_pair,   # 取引通貨
                    price  = order_string,  # 指値価格
                    side   = 'buy',        # 購入(buy) or 売却(sell)
                    amount = amount,        # 購入数量[XWIN]

fetchClosedOrders  = mexc.fetchClosedOrders (symbol = market_pair                                 )
print(fetchClosedOrders)


# In[ ]:





# In[ ]:




