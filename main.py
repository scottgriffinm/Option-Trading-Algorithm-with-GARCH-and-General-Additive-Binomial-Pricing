from price_option import general_additive_binomial_valuation_american as option_price
import yfinance as yf
import csv
from arch import arch_model
from datetime import date
import sys

YEARS_IN_TRAINING_DATA = 5
#RISK_FREE_RATE = 0.06

#import csv of option data
with open('option_data.csv', newline='') as csvfile:
    option_data = []
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        option_data.append(row)
    csvfile.close()
option_data[0][0] = "data_date" # fix first header (csv start symbol at beginning)

first_row = option_data[20]

K = first_row[1]
asset = first_row[3]
option_type = first_row[5].lower()
data_date = first_row[0]
strike_date = first_row[4]
# NEED S
# NEED scaled risk free rate

start_date = str(int(data_date[:4])-YEARS_IN_TRAINING_DATA) + data_date[4:]
print(data_date)
# get stock data
ticker = yf.Ticker(asset)
hist = ticker.history(interval="1mo", start=start_date, end=data_date)
returns = hist['Close'].pct_change().dropna()

# asset prices in range of data date to option strike date
asset_prices = ticker.history(start=data_date, end=strike_date)
print(asset_prices)
sys.exit()

# fit GARCH model and predict next months volatility
model = arch_model(returns, mean='Zero', vol='GARCH', dist='t', p=1, q=1)
fitted_model = model.fit()
print(fitted_model.summary())
predicted_vol = fitted_model.forecast(horizon=1)

# price option

