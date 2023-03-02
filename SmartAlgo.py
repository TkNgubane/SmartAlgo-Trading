"""
SmartAlgo Trading

Smart Algo is a software program that executes trades in financial markets based on pre-defined rules and 
algorithms. The robot uses historical data and real-time market data to analyze market trends, identify 
trading opportunities, and execute trades automatically without the need for human intervention. 
It can trade in various markets, including stocks, forex, futures, and options. The goal of a trading 
robot is to generate profits by taking advantage of market inefficiencies and price movements while 
minimizing risks and losses.

__author__ = "Ntokozo Ngubane"
__email__ = "tk19ngubane@gmail.com"
__website__= "ntokozongubane.com"
__credits__ = ["CodeTrading", "TraderPy", "Python for Trading"]
__version__ = "2022.01"
__status__ = "Development"
__maintainer__ = "Ntokozo Ngubane"

"""


import pandas as pd  
import pandas_ta as ta
import time
import pytz                                                         
import MetaTrader5 as mt5
import config
from datetime import datetime



now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time = ", current_time)



# ------------------- Support and Resistance --------------
def support(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.low[i]>df1.low[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.low[i]<df1.low[i-1]):
            return 0
    return 1

def resistance(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.high[i]<df1.high[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.high[i]>df1.high[i-1]):
            return 0
    return 1
# -------XXX------- Support and Resistance ------XXX-------



# -------------------------- Executing Trades --------------------------
def market_order(symbol, volume, trade_deviation, order_type, stoploss, **kwargs):
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "sl": stoploss,                                                                  # float
        "tp": 0.0,                                                                       
        "deviation": trade_deviation,
        "magic": 100,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)

    return order_result
# ------------XXX----------- Executing Trades ------------XXX-----------



# --------------------- Lot Size --------------------- 
def getBalanceGetVolume():    
    account_info = mt5.account_info()

    balance = account_info.balance
    
    if balance<=750.00:
        VOLUME = 0.03
    elif balance>=751.00 and balance<=1200.00:
        VOLUME = 0.02
    elif balance>=1201.00 and balance<=1400.00:
        VOLUME = 0.03
    elif balance>=1401.00 and balance<=1600.00:
        VOLUME = 0.04
    elif balance>=1601.00 and balance<=1800.00:
        VOLUME = 0.05
    elif balance>=1801.00 and balance<=2000.00:
        VOLUME = 0.06
    elif balance>=2001.00 and balance<=2500.00:
        VOLUME = 0.07
    elif balance>=2501.00 and balance<=3000.00:
        VOLUME = 0.08
    elif balance>=3001.00 and balance<=4000.00:
        VOLUME = 0.09
    elif balance>=4001.00 and balance<=5000.00:
        VOLUME = 0.10
    elif balance>=5001.00 and balance<=6000.00:
        VOLUME = 0.11
    elif balance>=6001.00 and balance<=7000.00:
        VOLUME = 0.12
    elif balance>=7001.00 and balance<=8000.00:
        VOLUME = 0.13
    elif balance>=9001.00 and balance<=10000.00:
        VOLUME = 0.14
    elif balance>=10001.00 and balance<=20000.00:
        VOLUME = 0.15
    elif balance>=20001.00 and balance<=50000.00:
        VOLUME = 0.20
    elif balance>=50001.00 and balance<=75000.00:
        VOLUME = 0.25
    elif balance>=75001.00 and balance<=100000.00:
        VOLUME = 0.30
    else:
        VOLUME = 0.35

    return balance, VOLUME
# --------------------- Lot Size ---------------------   



# -------------------------- Trailing Stoploss --------------------------
def handle_buy(myPos, THRESHOLD, MARGIN):
    position = myPos.ticket
    symbolName = myPos.symbol
    point = mt5.symbol_info(symbolName).point
    open_price = myPos.price_open 
    GOAL = open_price + point * THRESHOLD
    current_stoploss = myPos.sl                          # return stoploss 
    tickAsk = mt5.symbol_info_tick(symbolName).ask
    buy_trailing_stop = tickAsk - MARGIN * point

    if (tickAsk >= GOAL and buy_trailing_stop > current_stoploss):
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": myPos.ticket,
            "sl": buy_trailing_stop,
            "tp": 0.0,
            "magic": 100,
            "comment": "python market order",
        }
        sent_order = mt5.order_send(request)

    return position


def handle_sell(myPos, THRESHOLD, MARGIN):
    position = myPos.ticket
    symbolName = myPos.symbol
    point = mt5.symbol_info(symbolName).point
    open_price = myPos.price_open 
    GOAL = open_price + point * THRESHOLD
    current_stoploss = myPos.sl                          # return stoploss 
    tickBid = mt5.symbol_info_tick(symbolName).bid
    sell_trailing_stop = tickBid + MARGIN * point
    
    if (tickBid <= GOAL and sell_trailing_stop < current_stoploss):
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": myPos.ticket,
            "sl": sell_trailing_stop,
            "tp": 0.0,
            "magic": 100,
            "comment": "python market order",
        }
        sent_order = mt5.order_send(request)
    
    return position
# ----------XXX------------- Trailing Stoploss -----------XXX------------



# -------------------------- Printing Account Information --------------------------
def return_account_info():
    account_info = mt5.account_info()

    login_number = account_info.login
    balance = account_info.balance
    equity = account_info.equity
    profit = account_info.profit
    margin = account_info.margin

    print("\n \nMy Account Info")
    print('Balance: R' + str(balance))
    print('Equity: ' + str(equity))
    print('Profit: ' + str(profit))
    print('Margin: ' + str(margin))    

    return login_number, balance, equity, profit, margin
# -----------XXX------------ Printing Account Information -----------XXX------------


if __name__ == '__main__':

    # strategy parameters
    SYMBOL = "GOLD"
    TIMEFRAME = mt5.TIMEFRAME_M1
    LOOP_TIMEFRAME = 60                       # seconds

    DEVIATION = 10
    LATE_ENTRY_DEVIATION = 5
    
    MY_THRESHOLD = 30                          # points
    MY_MARGIN = 150                            # trailing stop distance =  +- 176 points


    # '''
    # =========================================== Trading Platform ===========================================
    try:     
        # -------------------------- Use your own account information --------------------------
        # mylogin = 00000000
        # mypassword = 'your_password'
        # myserver = 'your_platform_server'
        # mypath = "C://Paste Your File Path To The Terminal/FxPro - MetaTrader 5/terminal64.exe"
        # -----------XXX------------ Use your own account information -----------XXX------------


        # my information
        mypath = config.Myinfo().my_path
        mylogin = config.Myinfo().my_login
        myserver = config.Myinfo().my_server
        mypassword = config.Myinfo().my_password


        if not mt5.initialize(path=mypath, login=mylogin, server=myserver, password=mypassword):
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        
        authorized = mt5.login(mylogin, mypassword, myserver)  

        if authorized:
            print("Connected to Trading Account #{}".format(mylogin))
        else:
            print("Failed to connect at account #{}, error code: {}".format(mylogin, mt5.last_error()))
    except:
        print("\n\n\n---Could not connect to Metatrader---")
    # =====================XXX=================== Trading Plartform =====================XXX===================
    # '''    

    
    # set time zone to UTC
    timezone = pytz.timezone("Etc/UTC")

    while True:

        balance, VOLUME = getBalanceGetVolume()
        print("Account Balance: R" + str(balance))
        print("Lotsize: " + str(VOLUME) + "\n")

        # --------------------------- Seting up dataframe ---------------------------
        rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 150)                                              # geting bars from symbols
        df = pd.DataFrame(rates)                                                                                # create DataFrame out of the obtained data
        df['time']=pd.to_datetime(df['time'], unit='s')                                                         # convert time in seconds into the 'datetime' format
        # -----------XXX------------- Seting up dataframe ----------XXX--------------
        
        # identifying signal rows
        print("\nSignal Candle Number:")    
        print(len(df)-2)

        # -------------- Analysing Functions --------------
        length = len(df)
        high = list(df['high'])
        low = list(df['low'])
        close = list(df['close'])
        open = list(df['open'])
        bodydiff = [0] * length

        highdiff = [0] * length
        lowdiff = [0] * length
        ratio1 = [0] * length
        ratio2 = [0] * length

        
        def isEngulfing(l):                                                 # checking if its an engulfing candle
            row = l
            bodydiff[row] = abs(open[row]-close[row])
            if bodydiff[row]<0.400000:
                return 0

            bodydiffmin = 0.002
            if (bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
                open[row-1]<close[row-1] and
                open[row]>close[row] and 
                (open[row]-close[row-1])>=-0e-5 and close[row]<open[row-1]): #+0e-5 -5e-5
                return 1

            elif(bodydiff[row]>bodydiffmin and bodydiff[row-1]>bodydiffmin and
                open[row-1]>close[row-1] and
                open[row]<close[row] and 
                (open[row]-close[row-1])<=+0e-5 and close[row]>open[row-1]):#-0e-5 +5e-5
                return 2
            else:
                return 0
            
        
        def isStar(l):                                                          # Checking if its a star candle 
            bodydiffmin = 0.0020
            row = l
            highdiff[row] = high[row]-max(open[row],close[row])
            lowdiff[row] = min(open[row],close[row])-low[row]
            bodydiff[row] = abs(open[row]-close[row])

            if bodydiff[row]<0.010000:
                return 0

            ratio1[row] = highdiff[row]/bodydiff[row]
            ratio2[row] = lowdiff[row]/bodydiff[row]

            if (ratio1[row]>1 and lowdiff[row]<0.2*highdiff[row] and bodydiff[row]>bodydiffmin):# and open[row]>close[row]):
                return 1
            elif (ratio2[row]>1 and highdiff[row]<0.2*lowdiff[row] and bodydiff[row]>bodydiffmin):# and open[row]<close[row]):
                return 2
            else:
                return 0
            
        
        def closeResistance(l,levels,lim,df1):                                  # Checking if its close to resistance
            if len(levels)==0:
                return 0
            c1 = abs(df1.high[l]-min(levels, key=lambda x:abs(x-df1.high[l])))<=lim
            c2 = abs(max(df1.open[l],df1.close[l])-min(levels, key=lambda x:abs(x-df1.high[l])))<=lim
            c3 = min(df1.open[l],df1.close[l])<min(levels, key=lambda x:abs(x-df1.high[l]))
            c4 = df1.low[l]<min(levels, key=lambda x:abs(x-df1.high[l]))
            if( (c1 or c2) and c3 and c4 ):
                return 1
            else:
                return 0
            
                
        def closeSupport(l,levels,lim,df1):                                       # Checking if its close to support
            if len(levels)==0:
                return 0
            c1 = abs(df1.low[l]-min(levels, key=lambda x:abs(x-df1.low[l])))<=lim
            c2 = abs(min(df1.open[l],df1.close[l])-min(levels, key=lambda x:abs(x-df1.low[l])))<=lim
            c3 = max(df1.open[l],df1.close[l])>min(levels, key=lambda x:abs(x-df1.low[l]))
            c4 = df1.high[l]>min(levels, key=lambda x:abs(x-df1.low[l]))
            if( (c1 or c2) and c3 and c4 ):
                return 1
            else:
                return 0
                     
        slow_sma_perriod = 100
        fast_sma_perriod = 10

        df['slow_sma'] = df['close'].rolling(slow_sma_perriod).mean()
        df['fast_sma'] = df['close'].rolling(fast_sma_perriod).mean()

        fast_sma = list(df['fast_sma'])
        slow_sma = list(df['slow_sma'])

        def find_crossover(l):
            row=l

            if fast_sma[row] >= slow_sma[row]:
                return 2
            elif fast_sma[row] <= slow_sma[row]:
                return 1
            else:
                return 0

        # Adding ATR
        df['ATR'] = ta.atr(high=df.high, low=df.low, close=df.close, length=14)
    
        # -----XXX------ Analysing Functions -----XXX------



        # ------------------------- Trading Logic -------------------------
        n1 = 2
        n2 = 2
        backCandles = 120
        signal = [0] * length

        try:
            for row in range(backCandles, len(df)-n2):
                ss = []
                rr = []
                for subrow in range(row-backCandles+n1, row+1):
                    if support(df, subrow, n1, n2):
                        ss.append(df.low[subrow])
                    if resistance(df, subrow, n1, n2):
                        rr.append(df.high[subrow])
                                                    
        except KeyError:
            print("\n---An error occured---")

        finally:
            print("\n \t\t\t\t\t\t\t\t\t Analyzing... ")

    
        atr_f = 0.4
        ATR = list(df['ATR'])
        stopsLosses = [0] * length

        for row in range(len(df)-5, len(df)):         
            if ((isEngulfing(row)==1 or isStar(row)==1) and closeResistance(row, rr, 150e-5, df)):       #and df.RSI[row]<30    /   and find_crossover(row)==1     and df.RSI[lastCandle]<70
                signal[row] = 1
                stopsLosses[row] = df.close[row] + df.ATR[row]/atr_f

            elif((isEngulfing(row)==2 or isStar(row)==2) and closeSupport(row, ss, 150e-5, df)):         #and df.RSI[row]>70    /   and find_crossover(row)==2     and df.RSI[lastCandle]>30
                signal[row] = 2
                stopsLosses[row] = df.close[row] - df.ATR[row]/atr_f

            else:
                signal[row] = 0
                stopsLosses[row] = 0
        # ------------XXX---------- Trading Logic -------------XXX---------



        # ----------------- Printing Dataframe -----------------
        print("\nDataframe with signal:")               
        df['Stop_Losses'] = stopsLosses                 # 176 points behind
        df['signal'] = signal        
        print(df.tail(3))
        # -------XXX------- Printing Dataframe ------XXX--------



        # -------------------------------------------------- !!! EXECUTING TRADES !!! -----------------------------------------------------        
        # identifying signal candle
        signalCandle = df.iloc[-2].signal
        signalCandleSL = df.iloc[-2].Stop_Losses

        signalCandle_LateEntry = df.iloc[-3].signal
        signalCandleSL_LateEntry = df.iloc[-3].Stop_Losses

        if signalCandle == 1 or signalCandle_LateEntry == 1:                            # BUY signal
            direction = 'sell'

            if signalCandle == 1:
                market_order(SYMBOL, VOLUME, DEVIATION, direction, signalCandleSL)
            else:
                market_order(SYMBOL, VOLUME, LATE_ENTRY_DEVIATION, direction, signalCandleSL_LateEntry)

            try:
                order_opened = mt5.positions_get()[-1].price_open
                print("\n---" + str(SYMBOL) + " sold @" + str(order_opened) + "---")
            except IndexError:
                print("\n---An error occured---")
            finally:
                print("\n---" + str(SYMBOL) + " sold---")

            login_number, balance, equity, profit, margin = return_account_info()

            time.sleep(5)

        elif signalCandle == 2 or signalCandle_LateEntry == 2:                          # SELL signal
            direction = 'buy'

            if signalCandle == 2:
                market_order(SYMBOL, VOLUME, DEVIATION, direction, signalCandleSL)
            else:
                market_order(SYMBOL, VOLUME, LATE_ENTRY_DEVIATION, direction, signalCandleSL_LateEntry)

            try:
                order_opened = mt5.positions_get()[-1].price_open
                print("\n---" + str(SYMBOL) + " bought @" + str(order_opened) + "---")
            except IndexError:
                print("\n---An error occured---")
            finally:
                print("\n---" + str(SYMBOL) + " bought---")

            account_info = mt5.account_info()
            
            login_number, balance, equity, profit, margin = return_account_info()

            time.sleep(5)

        # -------------------------------------------------------------------------------------------------------------------------------
      

        # ----------------------- Trail Stop ----------------------- 
        third_to_last = df.iloc[-3].close
        second_to_last = df.iloc[-2].close

        num_trades = mt5.positions_total()
        print("Total number of trades == " + str(num_trades))

        all_positions = mt5.positions_get()
        for pos in all_positions:
            if pos.type == 1 and (second_to_last < third_to_last):
                position = handle_sell(pos, MY_THRESHOLD, MY_MARGIN)
                print("Position " + str(position) + ", Modified Stoploss == " + str(pos.sl))
            elif pos.type == 0 and (second_to_last > third_to_last):
                position = handle_buy(pos, MY_THRESHOLD, MY_MARGIN)
                print("Position " + str(position) + ", Modified Stoploss == " + str(pos.sl))
            else:
                print('Waiting to trailstop position ' + str(pos.ticket) + '...')
        # ----------XXX---------- Trail Stop ---------XXX----------- 
        

        end = datetime.now()
        end_time = end.strftime("%H:%M:%S")
        print("\nLoop Ending Time =", end_time)
        print("------------------------------------------------------------------------------------\n")
        
        time.sleep(LOOP_TIMEFRAME)

mt5.shutdown()
print("*********** Trading Robot Shutdown ***********")
