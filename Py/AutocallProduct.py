from .ResultSimulation import *
from .Utils import *
import numpy as np
import enum
import pandas as pd
from .Parameter import *
from .Utils import *
from .BaseProduct import *

### https://bookdown.org/maxime_debellefroid/MyBook/autocallables.html
class AutocallProduct(BaseProduct):
    def __init__(self,spotRef,maturity,acBarrierLevel,coupon,cpnBarrier,dipStrike,dipBarrier,Nominal = 100,isDipAmerican = False,
                 cpnFrequency = Frequency.BiAnnualy,isIncrementalFeature = False,isPhoenixMemory = False,hasRedemption = True):        
        super(AutocallProduct,self).__init__(maturity)
        
        self.spotRef = spotRef
        #self.maturity = maturity
        self.acBarrierLevel = acBarrierLevel
        self.coupon = coupon
        self.cpnBarrier = cpnBarrier
        self.dipStrike = dipStrike
        self.dipBarrier = dipBarrier
        self.isDipAmerican = isDipAmerican
        self.cpnFrequency = cpnFrequency
        
        self.isIncrementalFeature = isIncrementalFeature
        
        if cpnBarrier == acBarrierLevel:
            self.isIncrementalFeature = isIncrementalFeature
            self.isPhoenixMemory = False
        else:
            self.isIncrementalFeature = False
        
        if cpnBarrier < acBarrierLevel: ## We are in phoenix case
            self.isPhoenixMemory = isPhoenixMemory
            self.isIncrementalFeature = False
        else:
            self.isPhoenixMemory = False
    
        self.counponsObservationDates = self.__buildScheduleCoupon()
        self.Nominal = Nominal
        self.hasRedemption = hasRedemption
        
    def counponsSimulDates(self):
        return self.counponsObservationDates
        
    def __buildScheduleCoupon(self):
        
        tmp = 365
        
        if self.cpnFrequency == Frequency.Daily:
            tmp = 365
        elif self.cpnFrequency == Frequency.Weekly:
            tmp = 52
        elif self.cpnFrequency == Frequency.BiMonthly:
            tmp = 2*12
        elif self.cpnFrequency == Frequency.Monthly:
            tmp = 12
        elif self.cpnFrequency == Frequency.Quaterly:
            tmp = 4
        elif self.cpnFrequency == Frequency.BiAnnualy:
            tmp = 2
        else:   
            tmp = 1
      
        refNb = int(tmp*self.maturity)    
        dt_tmp = 1/tmp
        
        reliquat =self.maturity - refNb*dt_tmp
        
        res = []
        
        ti = reliquat
        if ti >0:
            res.append(ti)
        
        while ti < self.maturity:
            ti = ti+dt_tmp
            res.append(ti)
            
        
        return res