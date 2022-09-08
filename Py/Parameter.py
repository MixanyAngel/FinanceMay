import numpy as np
import scipy.optimize
from scipy.optimize import Bounds
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint
import enum
import pandas as pd
from scipy.stats import norm

class SupInf(enum.Enum):
    Sup = 1
    Inf = 2
    
class Constraint:    
    def __init__(self,epsilon = 1e-8):
        self.epsilon = epsilon
        
    def bound(self):
        raise NotImplementedError()
        
class UnConstraint(Constraint):
    def bound(self):
        return [-np.inf, np.inf]
    
class PositiveNegativeConstraint(Constraint):
    def __init__(self,bound = 0,sens = SupInf.Sup,strict = False,epsilon = 1e-8):
        super(PositiveNegativeConstraint,self).__init__(epsilon)
        
        self.strict_ = strict
        self.sens_ = sens
        self.bound_ = bound
    
    def bound(self):
        epsilon = self.epsilon
        if self.strict_ is False:
            epsilon = 0
        
        if self.sens_ == SupInf.Sup:
            return [self.bound_+epsilon, np.inf]
        else:
            return [-np.inf,self.bound_-epsilon]
        

class BoundaryConstraint(Constraint):
    def __init__(self,boundinf,boundsup,strictLow = True,strictUp = True,epsilon = 1e-8):
        super(BoundaryConstraint,self).__init__(epsilon)
        
        self.boundinf = boundinf
        self.boundsup = boundsup
        self.strictLow = strictLow
        self.strictUp = strictUp
        
    def bound(self):
        epsilonUp = self.epsilon
        epsilonDown = self.epsilon
        
        if self.strictLow is False:
            epsilonDown = 0
        
        if self.strictUp is False:
            epsilonUp = 0
            
        return [self.boundinf+epsilonDown, self.boundsup - epsilonUp]
        
        
class Parameter:    
    def __init__(self,value,constraint = UnConstraint(),name=''):
        self.value = value
        self.constraint = constraint
        self.name = name
        self.__oldConstraint = None
        
    def update(self,value):        
        self.value = value
    
    def value(self):
        return self.value
    
    def getbound(self):
        return self.constraint.bound()
    
    def UnfreezeParam(self):
        if self.__oldConstraint is not None:
            self.constraint = self.__oldConstraint
            self.__oldConstraint = None  
        
    def freezeParam(self):
        self.__oldConstraint = self.constraint
        self.constraint = BoundaryConstraint(self.value,self.value,strictLow = False,strictUp = False)