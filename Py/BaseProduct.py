from .ResultSimulation import *
from .Utils import *
import numpy as np
import enum
import pandas as pd
from .Parameter import *
from .Utils import *


class BaseProduct:
    def __init__(self,maturity):
        self.maturity = maturity
        
    def counponsSimulDates(self):
        return []