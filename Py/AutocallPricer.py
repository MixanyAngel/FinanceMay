import pandas as pd
from .Market import *
from .ResultSimulation import *
from .BasePricer import *
import numpy as np

import enum
from .BS import TypeOptionVanilla
from .AutocallProduct import *


class AutocallPricer(BasePricer):
    def __init__(self,autocallProduct,simulationRes,discountCurve):
        super(AutocallPricer,self).__init__(autocallProduct,simulationRes,discountCurve)
        
        obsvdates = autocallProduct.counponsObservationDates
        obsdatesAc = []
        obsdatesAc.append(0)
        
        obsdatesAc.extend(obsvdates[0:-1])
        
        spotref = autocallProduct.spotRef
        simulTmp = simulationRes.getSimulVector(obsvdates)/spotref
        
        self.eventsCoupon = simulTmp
        self.eventsRedemption = simulTmp
        
        self.eventsCoupon = (self.eventsCoupon >=autocallProduct.cpnBarrier)*1
        self.eventsRedemption = (self.eventsRedemption >=autocallProduct.acBarrierLevel)*1
        
        self.eventsNotAC = simulationRes.getSimulVector(obsdatesAc)/spotref        
        
        self.eventsNotAC = (self.eventsNotAC <= autocallProduct.acBarrierLevel)*1
        self.eventsNotAC = self.eventsNotAC.cumprod(axis = 1)
        self.eventsNotAC.columns = obsvdates
        
        self.eventsCoupon = self.eventsCoupon*self.eventsNotAC ### 1 if coupon is paid               
        
        self.eventsRedemption = self.eventsRedemption*self.eventsNotAC ###1 if redemption paid
        
        self.probaAutocall = (1.0-self.eventsNotAC).mean(axis = 0)
        self.probaCoupon = self.eventsCoupon.mean(axis = 0)
        self.probaRedemption = self.eventsRedemption.mean(axis = 0)
        
        ST = simulationRes.getSimulVector([autocallProduct.maturity])/spotref
        
        if autocallProduct.isDipAmerican:
            
            refinedSimul = simulationRes.getSimulUpTo(autocallProduct.maturity)/spotref        
            eventDip = refinedSimul
            eventDip  = (eventDip.min(axis = 1) <= autocallProduct.dipBarrier)*1             
            eventDip = pd.DataFrame(eventDip,columns=[autocallProduct.maturity]) 
            
            self.eventDipTouched = eventDip*pd.DataFrame(self.eventsNotAC[autocallProduct.maturity]) ### 1 if DIP is paid
            self.probaDipTouched = float(self.eventDipTouched.mean())
        else:
            
            eventDip = (ST<=autocallProduct.dipBarrier)*1
            self.eventDipTouched = eventDip* pd.DataFrame(self.eventsNotAC[autocallProduct.maturity]) ### 1 if DIP is paid
            self.probaDipTouched = float(self.eventDipTouched.mean())           
            
        self.discountedCouponsPrice = dict()
        self.discountedRedemptionPrice = dict()
        self.DIPLegPrice = float(discountCurve(autocallProduct.maturity)* autocallProduct.Nominal*((1.0-self.eventDipTouched*np.maximum(autocallProduct.dipStrike-ST,0)).mean()))
        ##self.DIPLegPrice = float(discountCurve(autocallProduct.maturity)* autocallProduct.Nominal*((0-self.eventDipTouched*np.maximum(autocallProduct.dipStrike-ST,0)).mean()))
        
        self.price = 0
        cpnsdiscounted = 0
        rdmpiondiscounted = 0
        
        dfs = np.array([discountCurve(u) for u in obsvdates])
        
        cpn = autocallProduct.coupon
        
        if not (autocallProduct.isIncrementalFeature or autocallProduct.isPhoenixMemory):
            cpns = (autocallProduct.Nominal*cpn*self.eventsCoupon).mean(axis = 0)   
            rdmption = (autocallProduct.Nominal*self.eventsRedemption).mean(axis = 0)
                        
            #dfs = np.array([discountCurve(u) for u in obsvdates])
            
            cpnsdiscounted = np.multiply(cpns,dfs)
            rdmpiondiscounted = np.multiply(rdmption,dfs)
            
            self.discountedCouponsPrice = dict(zip(obsvdates,cpnsdiscounted))
            
            if autocallProduct.hasRedemption:
                self.discountedRedemptionPrice = dict(zip(obsvdates,rdmpiondiscounted))
                        
        elif autocallProduct.isIncrementalFeature:
            
            rdmption = (autocallProduct.Nominal*self.eventsRedemption).mean(axis = 0)
            #print(rdmption)
            
            rdmpiondiscounted = np.multiply(rdmption,dfs)
            
            if autocallProduct.hasRedemption:
                self.discountedRedemptionPrice = dict(zip(obsvdates,rdmpiondiscounted))
            
            cpns = np.array([autocallProduct.Nominal*i*cpn for i in range(1,len(obsvdates)+1)])
            cpns = np.multiply(cpns,self.eventsCoupon).mean(axis = 0)
            cpnsdiscounted = np.multiply(cpns,dfs)            
            self.discountedCouponsPrice = dict(zip(obsvdates,cpnsdiscounted))
            
        else:
            rdmption = (autocallProduct.Nominal*self.eventsRedemption).mean(axis = 0)
            rdmpiondiscounted = np.multiply(rdmption,dfs)
            
            if autocallProduct.hasRedemption:
                self.discountedRedemptionPrice = dict(zip(obsvdates,rdmpiondiscounted))
            
            cpnsPart1 = np.array([autocallProduct.Nominal*i*cpn for i in range(1,len(obsvdates)+1)])
            cpnsPart1 = np.multiply(cpnsPart1,self.eventsCoupon)
            
            cpnsPart2 = autocallProduct.Nominal*cpn*self.eventsCoupon
            
            cpnsPart3 = cpnsPart2.cumsum(axis = 1)-cpnsPart2
            
            cpns = cpnsPart1-cpnsPart3
            cpns = cpns.mean(axis = 0)
            
            cpnsdiscounted = np.multiply(cpns,dfs)
            self.discountedCouponsPrice = dict(zip(obsvdates,cpnsdiscounted)) 
            
        coupnPrice = float(np.sum(cpnsdiscounted))
        rdmpPrice = float(np.sum(rdmpiondiscounted)) 
        
        if not autocallProduct.hasRedemption:
            rdmpPrice = 0
        
        #print(coupnPrice)
        #print(rdmpPrice)
        
        self.price = float(coupnPrice) + float(rdmpPrice)+self.DIPLegPrice
        #self.Price = self.Price + self.DIPLegPrice