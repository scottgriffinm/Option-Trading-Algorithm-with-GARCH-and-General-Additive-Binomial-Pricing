from pred_volatility import pred_volatility
from price_option import general_additive_binomial_valuation_american as price_option
import yfinance as yf
import csv

# Written by Scott Griffin in Python3 5/10/23

# ---------------------- Index ----------------------- #
# a. CONSTANTS                                         
# b. LOAD DATA
# c. SIMULATION
# ---------------------------------------------------- #

# ---------------------------------------------------- #
# ----------------  a. CONSTANTS  -------------------- #
# ---------------------------------------------------- #

# trading algorithm
EXCERCISE_LAG = 3
BUY_IF_UNDERPRICED_BY_PCT = 0.1
# garch model
GARCH_HIST_YEARS = 1
GARCH_P = 1
GARCH_Q = 1
GARCH_DISTRIBUTION = 't'
# risk free rate
RISK_FREE_ANNUAL = 0.035

# ---------------------------------------------------- #
# ----------------  b. LOAD DATA  -------------------- #
# ---------------------------------------------------- #

# import option data
with open('option_data.csv', newline='') as csvfile:
    option_data = []
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        option_data.append(row)
    csvfile.close()
option_data[0][0] = "data_date" # fix first header (csv start symbol at beginning)

# split into option chains
option_data = option_data[1:]
option_chains = []
temp_chain = [option_data[0]]
for row in option_data:
    if (row[0],row[3]) == (temp_chain[-1][0],temp_chain[-1][3]):
        temp_chain.append(row)
    else:
        option_chains.append(temp_chain.copy())
        temp_chain = [row]


# ---------------------------------------------------- #
# ----------------- c. SIMULATION  ------------------- #
# ---------------------------------------------------- #

# start simulation
print("Starting simulation...")
account_value = 0
RISK_FREE_MONTHLY = RISK_FREE_ANNUAL**(1/12)

# for each option chain
for option_chain in option_chains:
    asset = option_chain[0][3]
    data_date = option_chain[0][0]
    strike_date = option_chain[0][4]
    future_prices = yf.Ticker(asset).history(start=data_date, end=strike_date)
    S = round(float(future_prices['Close'][0]),2)

    # predict volatility on the underlying asset
    predicted_volatility = pred_volatility(asset, data_date, years=GARCH_HIST_YEARS, p=GARCH_P, q=GARCH_Q, dist=GARCH_DISTRIBUTION)

    # calculate prices for each option listing
    calculated_prices = []
    for option in option_chain:
        K = float(option[1])
        option_type = option[5].lower()
        calculated_prices.append(round(price_option(K,1,S,predicted_volatility,RISK_FREE_MONTHLY,1,option_type),2))

    for i in range(len(option_chain)):
        # for each option in the option chain
        print(f'''\n{option_chain[i][2]}:''')
        print(f'''Today = {data_date}, S = {S}''')
        broker_price = round(float(option_chain[i][6]),2)
        print(f'''Broker Price = {broker_price}\nCalculated Price = {calculated_prices[i]}\nCalculated Volatility = {predicted_volatility}''')
        # if underpriced
        if calculated_prices[i] > broker_price*(1+BUY_IF_UNDERPRICED_BY_PCT):
            cost = round(broker_price*100,2)
            print(f"ACTION = BUY (-${cost})")
            account_value -= cost
            K = round(float(option_chain[i][1]),2)
            lag = 0
            days = 0
            excercised = False
            # step through future daily prices and excercise if profitable after lag
            for asset_price in future_prices['Close']:
                asset_price = round(asset_price,2)
                days +=1
                if option_type == 'call':
                    if asset_price > K:
                        lag += 1
                        if lag >= EXCERCISE_LAG:
                            profit = round((asset_price - K)*100,2)
                            print(f"Excercised at {asset_price} after {days} days (+${profit})")
                            excercised = True
                            account_value += profit
                            account_value = round(account_value,2)
                            print(f"Account Value = {account_value}")
                            break
                    else:
                        lag = 0
                elif option_type == 'put':
                    if asset_price < K:
                        lag += 1
                        if lag >= EXCERCISE_LAG:
                            profit = round((K - asset_price)*100,2)
                            print(f"Excercised at {asset_price} after {days} days (+${profit})")
                            excercised = True
                            account_value += profit
                            account_value = round(account_value,2)
                            print(f"Account Value = {account_value}")
                            break
                    else:
                        lag = 0
            if excercised == False:
                print(f"Option expired without excercise")
                print(f"Account Value = {account_value}")

        # if overpriced
        else:
            print("ACTION: NONE")
            print(f"Account Value = {account_value}")
            continue

print(f'''\n--------------------------------------------
Final Account Value = {account_value}
--------------------------------------------''')