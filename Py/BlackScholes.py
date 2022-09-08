import numpy as np

import scipy.optimize
from scipy.optimize import Bounds
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint
import enum
from scipy.stats import norm

from .BS import *
import pandas as pd
from .Parameter import *

from .Market import *
from .ResultSimulation import *
from .Utils import *
from .BaseModel import *
from .CalibrationProduct import *




class BlackScholesModel(BaseModel):
    def __init__(self,marketObj, sigma = 0.2): 
        super(BlackScholesModel,self).__init__(marketObj)
        self.dictParams_ = dict()
        self.dictParams_['sigma'] = Parameter(sigma,BoundaryConstraint(0,5,strictLow = False,strictUp = False),name = 'sigma')            
        self.marketObj = marketObj
        
    def sigma(self):
        return self.dictParams_['sigma'].value
    
    def recalibrate(self):
        K = self.marketObj.spot
        T = 1
        self.dictParams_['sigma'].update(self.marketObj.getVol(K,T))       
        
    
    def generatePaths(self,T,discretStep =  Frequency.Monthly, listT = [], Npaths = 50000,isAntithetic = False):
        return self.generate_paths(T,discretStep, listT, Npaths,isAntithetic)
        
    def generate_paths(self,T,discretStep =  Frequency.Monthly, listT = [], Npaths = 50000,isAntithetic = False):
        
        tmp = getNbStepInAyear(discretStep)
      
        refNb = int(tmp*T)
    
        dt_tmp = T/refNb
        
        steps = [ i*dt_tmp for i in range(refNb+1)]
        steps.extend(listT)
        steps = list(sorted(list(set(steps))))  
        
        if not isAntithetic:
            size = (Npaths, len(steps))
            
        else:
            size = (2*Npaths, len(steps))
            
        St = np.zeros(size)
        
        # Assign first value of all Vt to sigma
        St = dict()        
        
        St[0] = [self.marketObj.spot] *size[0]
        S_t = self.marketObj.spot
        
        np.random.seed(0)
        
        vol = self.sigma()
        
        #v_t = self.sigma()**2
        
        for i in range(1,len(steps)):
            
            ti_prev = steps[i-1]
            ti = steps[i]
            
            dt = ti - ti_prev
            
            if dt == 0:
                continue
            
            
            r = (1/dt)*(np.log(self.marketObj.zcDriftCurve(ti))-np.log(self.marketObj.zcDriftCurve(ti_prev))) 
            WT = np.random.normal(0,1,size=Npaths) * np.sqrt(dt)            
            if isAntithetic:
                WT = np.concatenate((WT,-1*WT))

            ln_S_t = np.log(S_t)+ r*dt -0.5*vol*vol*dt+ vol*WT
            
            S_t = np.exp(ln_S_t)             
            St[ti] = S_t
            
    
        return ResultSimulation(St)
    
    def modelPrice(self,baseCalibrationProduct):
        if baseCalibrationProduct.typeProduct == TypeProduct.VanillaCall:            
            #aseCalibrationProduct.__class__ = VanillaProduct

            K = baseCalibrationProduct.K
            T = baseCalibrationProduct.T
            sens = baseCalibrationProduct.sens
            
            return self.__modelVanillaCallPrice(K,T,sens)
            
        else:            
            return 1          
    
    
    def __modelVanillaCallPrice(self,K,T,sens = 1):
        
        F = self.marketObj.forwardSpot(T)
        D = self.marketObj.discount(T)        
        sigma = self.sigma()
        
        if sens == 1:            
            return BS_CALL(D,F, K, sigma,T)
        else:            
            return BS_PUT(D,F, K, sigma,T) 
        
    def constraints(self):        
        return ()       
   
    
    def guessinit(self):
        return np.array([self.sigma()])
    
    def update(self,params):
        self.dictParams_['sigma'].update(params[0])