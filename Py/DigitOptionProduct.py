import enum
from .BaseProduct import *
from .Utils import *
from .BS import *

class TypeDigit(enum.Enum):
    European = 1
    American = 2  
    
class DigitOptionProduct(BaseProduct):
    def __init__(self,spotRef,maturity,strike,typeDigit = TypeDigit.European, hasRebate = False,rebateCpn = 0,Nominal = 100):
        
        super(DigitOptionProduct,self).__init__(maturity)
        self.spotRef = spotRef
        self.maturity = maturity
        self.strike = strike
        self.typeDigit = typeDigit
        self.hasRebate = hasRebate
        self.rebateCpn = rebateCpn
        self.Nominal = Nominal        
        
    def counponsObservationDates(self):
        return []
        