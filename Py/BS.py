import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar   
import pandas as pd
import pandas_datareader.data as web
import datetime as dt
N = norm.cdf
import enum 

class TypeOptionVanilla(enum.Enum):
    Call = 1
    Put = 2

def BS_CALL(D,F, K, vol,T):
    stddev = np.sqrt(vol*vol*T)
    
    if vol == 0:
        return D*max(F-K,0)
    
    if K == 0:
        return D*F
    
    dpos = (np.log(F/K)/stddev)+0.5*stddev
    dneg = dpos -stddev
        
    npos = norm.cdf(dpos)
    nneg = norm.cdf(dneg)
        
    return D*(F*npos - K*nneg)

def BS_PUT(D,F, K, vol,T):
    
    callPrice = BS_CALL(D,F, K, vol,T)
    return callPrice - D*(F-K)

def implied_vol(opt_value, D, F, K, T, type_=TypeOptionVanilla.Call):
    
    def call_obj(vol):
        return abs(BS_CALL(D,F, K, vol,T) - opt_value)
    
    def put_obj(vol):
        return abs(BS_PUT(D,F, K, vol,T) - opt_value)
    
    if type_ == TypeOptionVanilla.Call:
        res = minimize_scalar(call_obj, bounds=(0.01,6), method='bounded')
        return res.x
    elif type_ == TypeOptionVanilla.Put:
        res = minimize_scalar(put_obj, bounds=(0.01,6),
                              method='bounded')
        return res.x
    else:
        raise ValueError("type_ must be 'put' or 'call'")