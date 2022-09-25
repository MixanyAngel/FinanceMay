import pandas as pd
from .Market import *
from .ResultSimulation import *
from .BasePricer import *
import numpy as np

import enum
from .BS import TypeOptionVanilla
from .VanillaOptionProduct import *


class VanillaOptionPricer(BasePricer):
    def __init__(self,product,simulationRes,discountCurve):
        super(VanillaOptionPricer,self).__init__(product,simulationRes,discountCurve)
        
        ST = simulationRes.getSimulVector([product.maturity])
        #print(ST)
        sens = 1 if product.typeOption == TypeOptionVanilla.Call else -1
        
        self.optionPayoffCoupon = np.maximum(sens*(ST-product.strike),0) 
        self.price = (float(discountCurve(product.maturity)* product.Nominal* np.mean(self.optionPayoffCoupon)))
        