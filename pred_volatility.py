import yfinance as yf
from arch import arch_model


# ticker, data_date, years
def pred_volatility(asset, data_date, years=5, p=1, q=1, dist='t', mean='Zero', vol='GARCH'):
    '''
    Predicts the volatility of an asset using GARCH model.
    
    Parameters
    ----------
    asset : str
        Ticker symbol of asset.
    data_date : str
        Date of option data in format YYYY-MM-DD.
    years : int
        Number of years of historical data to use.
    p : int
        Number of lags of the conditional variance.
    q : int
        Number of lags of the conditional volatility.
    dist : str
        Distribution of the returns.
    mean : str
        Mean model of the returns.
    vol : str
        Volatility model of the returns.

    Returns
    -------
    predicted_volatility : float
        Predicted volatility of the asset.
        '''
    
    # download historical data
    start_date = str(int(data_date[:4])-years) + data_date[4:]
    ticker = yf.Ticker(asset)
    hist = ticker.history(interval="1mo", start=start_date, end=data_date)

    # calculate returns
    returns = hist['Close'].pct_change().dropna()

    # fit GARCH model
    model = arch_model(returns, mean=mean, vol=vol, dist=dist, p=p, q=q, rescale=False)
    fitted_model = model.fit(disp="off")

    # predict next months volatility
    forecasts = fitted_model.forecast(horizon=1, reindex=False)
    predicted_volatility = forecasts.variance.values[-1][0]

    return predicted_volatility