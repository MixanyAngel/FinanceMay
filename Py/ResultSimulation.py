import numpy as np
import enum
import pandas as pd


class ResultSimulation:
    def __init__(self,St):
        if not isinstance(St,dict):
            raise Exception("Sorry, St must be a dict with times as keys, and values being simulations !")
        
        self.times = np.array(list(St.keys()))
        self.maxMat = float(self.times[-1])
        self.simulDict = St
        self.simulDf = pd.DataFrame.from_dict(self.simulDict)
        
    def __getInterpBounds(self,T):
        posSup = np.flatnonzero(self.times>T)[0]
        posInf = np.flatnonzero(self.times<=T)[-1]
        
        tb = self.times[posSup]
        ta = self.times[posInf]
        
        if ta == tb:
            return self.simulDict[ta]
        else:
            ya = self.simulDict[ta]
            yb = self.simulDict[tb]
            
            return (((yb-ya)/(tb-ta))*(T-ta))+ya
            
        
    def getSimul(self,T):
        
        try:
            return self.simulDict[T]
        except:        
            return self.__getInterpBounds(T)
    
    def getSimulVector(self,vectT):
        
        res =  [self.getSimul(u) for u in vectT]
        dictRes = dict(zip(vectT,res))
        
        return pd.DataFrame.from_dict(dictRes)
    
    def getSimulUpTo(self,T):
        
        if T == self.maxMat:
            return self.simulDf
        
        vectT = list(self.times[self.times<=T])
        
        if T not in vectT:
            vectT.append(T)
            
        return self.getSimulVector(vectT)