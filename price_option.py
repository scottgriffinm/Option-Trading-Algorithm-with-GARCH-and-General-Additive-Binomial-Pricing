import math

# Page 24 of Implementing Derivatives Models (Clewlow, Strickland, 1998)
# Implemented in Python3 by Scott Griffin Jr., University of Iowa, 2023

def general_additive_binomial_valuation_american(K,T,S,sig,r,N,option_type):
    '''
    Price an American option using the General Additive Binomial Model.

    Parameters
    ----------
    K : float
        Strike price of the option.
    T : float
        Time to maturity of the option.
    S : float
        Current price of the underlying asset.
    sig : float                                                                                                                                                                    
        Volatility of the underlying asset.
    r : float
        Risk-free interest rate.
    N : int
        Number of time steps.
    option_type : str
        Type of option, either 'call' or 'put'.

    Returns
    -------
    C : float
        Price of the option.
    '''

    # check option type
    if option_type not in ['call', 'put']:
        raise ValueError("option_type must be either 'call' or 'put'")

    # set coefficents
    dt = T/N
    nu = r - 0.5*sig**2
    dxu = math.sqrt(sig**2*dt + (nu*dt)**2)
    dxd = -dxu
    pu = 0.5 + 0.5*(nu*dt/dxu)
    pd = 1-pu

    # precompute constants
    disc = math.exp(-r*dt)
    dpu = disc*pu
    dpd = disc*pd
    edxud = math.exp(dxu-dxd)
    edxd = math.exp(dxd)

    # initialize asset prices at maturity N
    St = [0]*(N+1)
    St[0] = S*math.exp(N*dxd)
    for i in range(1,N+1):
        St[i] = St[i-1]*edxud
    
    # initialize option values at maturity
    C = [0]*(N+1)
    if option_type == 'put':
        for i in range(0,N+1):
            C[i] = max(0,K-St[i])
    elif option_type == 'call':
        for i in range(0,N+1):
            C[i] = max(0,St[i]-K)
        
    # step back through the tree applying early exercise condition
    for i in range(N,-1,-1):
        for j in range(0,i):
            C[j] = dpu*C[j+1] + dpd*C[j]
            # adjust asset price to current time step
            St[j] = St[j]/edxd
            # apply early exercise condition
            if option_type == 'put':
                C[j] = max(C[j], K-St[j])
            elif option_type == 'call':
                C[j] = max(C[j], St[j]-K)
                
    return C[0]

# Textbook example
# K = 100
# T = 1
# S = 100
# sig = 0.2
# r = 0.06
# N = 3
# print("put: ",general_additive_binomial_valuation_american(K,T,S,sig,r,N,option_type='put'))
# print("call: ",general_additive_binomial_valuation_american(K,T,S,sig,r,N,option_type='call'))