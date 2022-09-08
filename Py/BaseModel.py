import scipy.optimize
from scipy.optimize import Bounds
from scipy.optimize import minimize
from scipy.optimize import NonlinearConstraint
from .Parameter import *
from .Utils import *

class BaseModel:
    def __init__(self,marketObj):        
        self.dictParams_ = dict()
        self._listCalibratedProduct = []
        self.marketObj = marketObj
        
    def printParams(self):
        dictres = dict()
        
        for key in self.dictParams_.keys():
            dictres[key] = self.dictParams_[key].value
            
        return dictres
    
    def recalibrate(self):
        return None
    
    def generatePaths(self,T,discretStep =  Frequency.Monthly, listT = [], Npaths = 50000,isAntithetic = False):
        raise NotImplementedError()
        
    def objectiveFunctionError(self,params):
        self.update(params)        
        return self.squaredErrorSum()
    
    def calibrate(self,listProduct,listParamToFix = [],maxIter = 1000,verbose = 1):
        
        self._listCalibratedProduct = listProduct
        
        if len(listParamToFix)>0:            
            for name in listParamToFix:
                if name in self.dictParams_.keys():
                    self.dictParams_[name].freezeParam()            
        
        self.__runOptimize(self.objectiveFunctionError,maxIter,verbose)  
        
        if len(listParamToFix)>0:            
            for name in listParamToFix:
                if name in self.dictParams_.keys():
                    self.dictParams_[name].UnfreezeParam()
        
        #self._listCalibratedProduct = []
        
        
    def modelPrice(self,baseCalibrationProduct):
        raise NotImplementedError()
    
    def errorDiff(self):        
        listgap= []
        
        for el in self._listCalibratedProduct:
            #rint(el.value())
            modelVal = self.modelPrice(el)
            #rint(el)
            mktval = el.value
            
            listgap.append(modelVal-mktval)
            
        return np.array(listgap)
        
    def squaredErrorSum(self):
        return 0.5*(np.power(self.errorDiff(),2)).sum()
    
    def getBounds(self):
        ld = []
        lup = []
        
        for key in self.dictParams_.keys():
            param = self.dictParams_[key]
            borne = param.getbound()
            
            ld.append(borne[0])
            lup.append(borne[1])
            
        return Bounds(ld,lup)
    
    def update(self,params):
        raise NotImplementedError()
    
    def guessinit(self):
        raise NotImplementedError()
        
    def constraints(self):
        return ()
    
    def __runOptimize(self,func,maxIter = 1000,verbose = 1):
        constraints = self.constraints()
        
        if constraints is not ():
            if not isinstance(constraints,list):
                constraints = [constraints]
        
        bounds = self.getBounds()
        x0 = self.guessinit()
        
        res = minimize(func,x0,method = 'trust-constr',
                       constraints = constraints,
                       options = {'verbose' : verbose,'maxiter': maxIter},bounds = bounds)
        
        params = res.x
        self.update(params)   