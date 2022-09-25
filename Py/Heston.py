import numpy as np
import scipy.integrate
import scipy.optimize
from scipy.optimize import Bounds
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint
import enum
from scipy.stats import norm

import pandas as pd
from .Parameter import *
from .Market import *
from .ResultSimulation import *
from .Utils import *
from .BaseModel import *

from .CalibrationProduct import *

       
class Heston(BaseModel):
    def __init__(self,marketObj, kappa = 4, theta = 0.2,Vo = 0.02,nu = 0.5,rho = -0.7): 
        super(Heston,self).__init__(marketObj)
        self.dictParams_ = dict()
        self.dictParams_['kappa'] = Parameter(kappa,BoundaryConstraint(0,5,strictLow = False,strictUp = False),name = 'kappa')
        self.dictParams_['theta'] = Parameter(theta,BoundaryConstraint(0,5,strictLow = False,strictUp = False),name = 'theta')
        self.dictParams_['Vo'] = Parameter(Vo,BoundaryConstraint(0,5,strictLow = False,strictUp = False),name = 'Vo')
        self.dictParams_['nu'] = Parameter(nu,BoundaryConstraint(0,2,strictLow = False,strictUp = False),name = 'nu')
        self.dictParams_['rho'] = Parameter(rho,BoundaryConstraint(-1,1,strictLow = True,strictUp = True),name = 'rho')
        
        if self.__fellerCondition(self.guessinit()) <0:
            raise Exception("Sorry, 2*kappa*theta should be greater than nu*nu !")
            
        self.marketObj = marketObj
        
    def generatePaths(self,T,discretStep =  Frequency.Monthly, listT = [], Npaths = 50000,isAntithetic = False):
        return self.generate_paths(T,discretStep, listT, Npaths,isAntithetic)
    
    def generate_paths(self,T,discretStep =  Frequency.Monthly, listT = [], Npaths = 50000,isAntithetic = False, return_vol=False):
        
        tmp = getNbStepInAyear(discretStep)
      
        refNb = int(tmp*T)
    
        if refNb == 0:
            steps = []
            steps.append(0.0)
            steps.append(T)
        else:
            dt_tmp = T/refNb        
            steps = [ i*dt_tmp for i in range(refNb+1)]
            
        steps.extend(listT)
        steps = list(sorted(list(set(steps))))  
        
        if not isAntithetic:
            size = (Npaths, len(steps))
            
        else:
            size = (2*Npaths, len(steps))
            
        St = np.zeros(size)
        sigs = np.zeros(size)
        
        # Assign first value of all Vt to sigma
        St = dict()
        sigs = dict()
        
        St[0] = [self.marketObj.spot] *size[0]
        sigs[0] = [self.Vo()] *size[0]
                
        S_t = self.marketObj.spot
        v_t = self.Vo()
        
        np.random.seed(0)
        
        rho = self.rho()
        kappa = self.kappa()
        theta = self.theta()
        nu = self.nu()
        
        for i in range(1,len(steps)):
            
            ti_prev = steps[i-1]
            ti = steps[i]
            
            dt = ti - ti_prev
            
            if dt == 0:
                continue
            
            
            r = (1/dt)*(np.log(self.marketObj.zcDriftCurve(ti))-np.log(self.marketObj.zcDriftCurve(ti_prev)))            
            
            WT = np.random.multivariate_normal(np.array([0,0]), 
                                               cov = np.array([[1,rho],
                                                              [rho,1]]), 
                                               size=Npaths) * np.sqrt(dt)
            
            #print(type(WT))
            #print(WT)
            #print(-1*WT)
            
            if isAntithetic:
                WT = np.concatenate((WT,-1*WT))

            S_t = S_t*(np.exp( (r- 0.5*v_t)*dt+ np.sqrt(v_t) *WT[:,0] ) ) 
            v_t = np.abs(v_t + kappa*(theta-v_t)*dt + nu*np.sqrt(v_t)*WT[:,1])
            St[ti] = S_t
            sigs[ti] = v_t

        if return_vol:
            return ResultSimulation(St), ResultSimulation(sigs)
    
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
    
    ## https://quant.stackexchange.com/questions/18684/heston-model-option-price-formula
    def __modelVanillaCallPrice(self,K,T,sens = 1):
        
        fwd = self.marketObj.forwardSpot(T)
        discount = self.marketObj.discount(T)        
        
        s = self.marketObj.spot                
        v = self.Vo()
        kappa = self.kappa()
        theta = self.theta()
        sigma_v = self.nu()
        rho = self.rho()
        k = K
        tau = T

        def phi(u, tau):
            alpha_hat = -0.5 * u * (u + 1j)
            beta = kappa - 1j * u * sigma_v * rho
            gamma = 0.5 * sigma_v ** 2
            d = np.sqrt(beta**2 - 4 * alpha_hat * gamma)
            g = (beta - d) / (beta + d)
            h = np.exp(-d*tau)
            A_ = (beta-d)*tau - 2*np.log((g*h-1) / (g-1))
            A = kappa * theta / (sigma_v**2) * A_
            B = (beta - d) / (sigma_v**2) * (1 - h) / (1 - g*h)
            return np.exp(A + B * v)

        def integral(k, tau):
            integrand = (lambda u: 
                np.real(np.exp((1j*u + 0.5)*k)*phi(u - 0.5j, tau))/(u**2 + 0.25))

            i, err = scipy.integrate.quad_vec(integrand, 0, np.inf)
            return i

        def call(k, tau):
            a = np.log(fwd/k)
            i = integral(a, tau)        
            return discount*(fwd - k/np.pi*i)
        
        callval = call(K,T)
        
        if sens == 1:
            return callval
        else:
            return callval - discount*(fwd-K)         
    
    def kappa(self):
        return self.dictParams_['kappa'].value
    
    def theta(self):
        return self.dictParams_['theta'].value
    
    def Vo(self):
        return self.dictParams_['Vo'].value
    
    def nu(self):
        return self.dictParams_['nu'].value
    
    def rho(self):
        return self.dictParams_['rho'].value
    
    def __fellerCondition(self,params):
        kappa = params[0]
        theta = params[1]
        Vo = params[2]
        nu = params[3]
        rho = params[4]
        
        return (2.0*kappa*theta) - (nu*nu) 
        
    def constraints(self):        
        nlc = NonlinearConstraint(self.__fellerCondition,0,np.inf)        
        return nlc
    
    
    def printParams(self):
        dictres = dict()        
        for key in self.dictParams_.keys():
            dictres[key] = self.dictParams_[key].value
            
        return dictres
    
    def guessinit(self):
        return np.array([self.kappa(),self.theta(),self.Vo(),self.nu(),self.rho()])
    
    def update(self,params):
        self.dictParams_['kappa'].update(params[0])
        self.dictParams_['theta'].update(params[1])
        self.dictParams_['Vo'].update(params[2])
        self.dictParams_['nu'].update(params[3])
        self.dictParams_['rho'].update(params[4])
        
    def recalibrate(self):
        if len(self._listCalibratedProduct)>0:
            self.calibrate(self._listCalibratedProduct,listParamToFix = [],maxIter = 100,verbose = 0)