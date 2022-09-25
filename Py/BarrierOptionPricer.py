from .BS import TypeOptionVanilla
import pandas as pd
from .Market import *
from .BarrierOptionProduct import *
from .BasePricer import *
import numpy as np

from .ResultSimulation import *
from .Utils import *


class BarrierOptionPricer(BasePricer):
    def __init__(self,product,simulationRes,discountCurve):
        super(BarrierOptionPricer,self).__init__(product,simulationRes,discountCurve)
        
        spotref = product.spotRef
        simulTmp = simulationRes.getSimulUpTo(product.maturity)/spotref
        
        eventCoupon = simulTmp
        ST = simulTmp[product.maturity]
        #print(ST)
        sens = 1 if product.typeOption == TypeOptionVanilla.Call else -1
        
        self.optionPayoffCoupon = np.maximum(sens*(ST-product.strikeOption),0)
        
        if product.typeBarrier == TypeBarrier.UpAndIn:            
            eventCoupon  = (eventCoupon.max(axis = 1) >= product.BarrierLevel)*1 
            self.eventBarrierTouched = pd.DataFrame(eventCoupon,columns=[product.maturity]) ### 1    
            self.eventRebate = pd.DataFrame(1-eventCoupon)
            
        elif product.typeBarrier == TypeBarrier.UpAndOut:
            
            eventCoupon  = (eventCoupon.max(axis = 1) < product.BarrierLevel)*1 
            self.eventBarrierTouched = pd.DataFrame(eventCoupon,columns=[product.maturity]) ### 1
            self.eventRebate = pd.DataFrame(1-eventCoupon)
        
        elif product.typeBarrier == TypeBarrier.DownAndIn:             
            eventCoupon  = (eventCoupon.min(axis = 1) <= product.BarrierLevel)*1 
            #print(eventCoupon)
            self.eventBarrierTouched = pd.DataFrame(eventCoupon,columns=[product.maturity]) ### 1
            self.eventRebate = pd.DataFrame(1-eventCoupon)
        else:
            eventCoupon  = (eventCoupon.min(axis = 1) > product.BarrierLevel)*1             
            self.eventBarrierTouched = pd.DataFrame(eventCoupon,columns=[product.maturity]) ### 1
            self.eventRebate = pd.DataFrame(1-eventCoupon)
            
        
        self.probaBarrierTouched = float(self.eventBarrierTouched.mean())  
        #print(self.probaBarrierTouched)
        #print(self.eventBarrierTouched)
        #print(self.optionPayoffCoupon)
        
        self.couponsEvent = self.eventBarrierTouched*pd.DataFrame(self.optionPayoffCoupon)
        #print( self.couponsEvent)
        #print(type( self.couponsEvent))
        self.rebatePrice = float(product.Nominal*product.rebateCpn*np.mean(self.eventRebate))
        
        self.price = (float(discountCurve(product.maturity)* product.Nominal* np.mean(self.couponsEvent)))+self.rebatePrice