import enum
from .BaseProduct import *
from .Utils import *
from .BS import *

class TypeBarrier(enum.Enum):
    DownAndIn = 1
    DownAndOut = 2
    UpAndIn = 3
    UpAndOut = 4    

class BarrierOptionProduct(BaseProduct):
    def __init__(self,spotRef,maturity,strikeOption,BarrierLevel,typeBarrier = TypeBarrier.UpAndIn, typeOption = TypeOptionVanilla.Call, hasRebate = False,rebateCpn = 0,Nominal = 100):
        
        super(BarrierOptionProduct,self).__init__(maturity)
        self.spotRef = spotRef
        self.maturity = maturity
        self.strikeOption = strikeOption
        self.BarrierLevel = BarrierLevel
        self.hasRebate = hasRebate
        self.rebateCpn = rebateCpn
        self.Nominal = Nominal
        self.typeOption = typeOption
        self.typeBarrier = typeBarrier
        
    def counponsObservationDates(self):
        return []
        