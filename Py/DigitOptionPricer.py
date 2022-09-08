import pandas as pd
from .Market import *
from .ResultSimulation import *
#import DigitOptionProduct
from .DigitOptionProduct import *
#import BasePricer
from .BasePricer import *
import numpy as np


class DigitOptionPricer(BasePricer):
    def __init__(self,product,simulationRes,discountCurve):
        super(DigitOptionPricer,self).__init__(product,simulationRes,discountCurve)
        
        spotref = product.spotRef
        
        if product.typeDigit == TypeDigit.European:
            ST = simulationRes.getSimul(product.maturity)/spotref
            eventCoupon  = (ST > product.strike)*1
            self.eventRebate = pd.DataFrame(1-eventCoupon) 
            self.eventStrikeisTouched = pd.DataFrame(eventCoupon,columns=[product.maturity])
        else:
            simulTmp = simulationRes.getSimulUpTo(product.maturity)/spotref
            eventCoupon = simulTmp
            eventCoupon  = (eventCoupon.max(axis = 1) >= product.strike)*1 
            self.eventStrikeisTouched = pd.DataFrame(eventCoupon,columns=[product.maturity]) ### 1    
            self.eventRebate = pd.DataFrame(1-eventCoupon)
            
        self.probaStrikeisTouched = float(self.eventStrikeisTouched.mean()) 
        self.rebatePrice = float(product.Nominal*product.rebateCpn*np.mean(self.eventRebate))
        
        self.price = (float(discountCurve(product.maturity)* product.Nominal* self.probaStrikeisTouched))+self.rebatePrice