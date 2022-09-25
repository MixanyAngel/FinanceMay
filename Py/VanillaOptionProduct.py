from .ResultSimulation import *
from .Utils import *
import numpy as np
import enum
import pandas as pd
from .Parameter import *
from .Utils import *
from .BaseProduct import *
from .BS import TypeOptionVanilla

### https://bookdown.org/maxime_debellefroid/MyBook/autocallables.html
class VanillaOptionProduct(BaseProduct):
    def __init__(self,strike,maturity,typeOption = TypeOptionVanilla.Call, Nominal = 1):        
        super(VanillaOptionProduct,self).__init__(maturity)
        
        self.strike = strike
        self.maturity = maturity
        self.Nominal = Nominal
        self.typeOption = typeOption
        
        
    def counponsSimulDates(self):
        return []
        
    