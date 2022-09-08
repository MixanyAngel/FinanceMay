import numpy as np
import scipy.optimize
from scipy.optimize import Bounds
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint
import enum
import pandas as pd
from scipy.stats import norm



class Market:
    def __init__(self,spot):
        self.spot = spot
    
    def initBlack(self,r,repo,vol):
        #self.volKT = (lambda K,T : np.minimum(np.maximum(vol-0.5*np.log(K/100)+0.05*0.5*np.log(K/100)**2,0.06),1.8))
        self.volKT = (lambda K,T : vol)
        self.repoCurve = lambda T: np.exp(-repo*T)
        self.discountCurve = lambda T : np.exp(-r*T)
        self.zcDriftCurve = lambda T : self.repoCurve(T)/self.discountCurve(T)
        ##self.yield
    
    def __copyRef(self):
        
        newMarket = Market(self.spot)
        newMarket.volKT = self.volKT      
        newMarket.repoCurve = self.repoCurve
        newMarket.discountCurve = self.discountCurve
        newMarket.zcDriftCurve = self.zcDriftCurve
        
        return newMarket
        
    def getVol(self,K,T):        
        return self.volKT(K,T)
    
    def discount(self,T):
        return self.discountCurve(T)
    
    def repo(self,T):
        return self.repoCurve(T)
    
    def forwardSpot(self,T):                
        return self.spot *self.zcDriftCurve(T)    
    
    def getMarketsSpotRange(self,listSpots,isInPercentage = True):        
        dictRes = dict()
        for spot in listSpots:
            if not isInPercentage:
                shock = (spot/self.spot)-1
            else:                
                shock = spot-1
                
            dictRes[spot] = self.shockSpot(shock)
        
        return dictRes        
    
    def shockSpot(self,epsilonShock,isRelative = True):
        
        spotShocked = epsilonShock*self.spot if isRelative else epsilonShock
        spotShocked = spotShocked+self.spot
        
        newMarket = self.__copyRef()
        newMarket.spot = spotShocked
        
        return newMarket
    
    def shockVol(self,epsilonShock,isRelative = True):
        
        funcRel = (lambda K,T : self.volKT(K,T)*(1.0+epsilonShock))
        funcAbs = (lambda K,T : self.volKT(K,T)+epsilonShock)
        
        newMarket = self.__copyRef()
        newMarket.volKT = funcRel if isRelative else funcAbs      
        
        return newMarket
    
    def shockRepoCurve(self,epsilonShock,isAbsolute = True):
        logRepo = lambda T : -np.log(self.repoCurve(T))
        
        funcRel = (lambda T : logRepo(T)*(1.0+epsilonShock))
        funcAbs = (lambda T : logRepo(T)+epsilonShock*T)
        func = funcAbs if isAbsolute else funcRel
        
        funcRepo = lambda T : np.exp(-func(T))
        
        newMarket = self.__copyRef()
        newMarket.repoCurve = funcRepo 
        newMarket.zcDriftCurve = lambda T : newMarket.repoCurve(T)/newMarket.discountCurve(T)
        
        return newMarket
    
    def shockDiscountCurve(self,epsilonShock,isAbsolute = True):
        logD = lambda T : -np.log(self.discountCurve(T))
        
        funcRel = (lambda T : logD(T)*(1.0+epsilonShock))
        funcAbs = (lambda T : logD(T)+epsilonShock*T)
        func = funcAbs if isAbsolute else funcRel
        
        funcD = lambda T : np.exp(-func(T))
        
        newMarket = self.__copyRef()
        newMarket.discountCurve = funcD 
        newMarket.zcDriftCurve = lambda T : newMarket.repoCurve(T)/newMarket.discountCurve(T)
        
        return newMarket