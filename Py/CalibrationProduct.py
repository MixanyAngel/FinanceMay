import numpy as np
import enum
import pandas as pd
from scipy.stats import norm
from .BS import *

class TypeProduct(enum.Enum):
    VanillaCall = 1
    VarSwap = 2    
    
class BaseCalibrationProduct:
    def __init__(self,typeProduct):        
        if not isinstance(typeProduct,TypeProduct):
            raise Exception("Sorry, TypeProduct is not well specified !")
            
        self.typeProduct = typeProduct
        self.value = 0.0
        
    def typeProduct(self):
        return self.typeProduct
    
    def value(self):
        return self.value

class VanillaProduct(BaseCalibrationProduct):
    def __init__(self,K,T,marketObj,sens = 1):
        super(VanillaProduct,self).__init__(TypeProduct.VanillaCall)
        
        self.K = K
        self.T = T
        self.marketObj = marketObj
        self.sens = sens
        self.value = self.blackPrice()        
        
    def blackPrice(self):
        T = self.T
        D = self.marketObj.discount(T)
        F = self.marketObj.forwardSpot(T)
        vol = self.marketObj.getVol(self.K,self.T)
        stddev = np.sqrt(vol*vol*self.T)
        K = self.K     
        
        if self.sens == 1:            
            return BS_CALL(D,F, K, vol,T)
        else:            
            return BS_PUT(D,F, K, vol,T) 