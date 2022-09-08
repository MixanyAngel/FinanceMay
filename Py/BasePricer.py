from .ResultSimulation import *
from .Utils import *
import numpy as np
import enum
import pandas as pd
from .Parameter import *
from .Utils import *

class BasePricer:
    def __init__(self,product,simulationRes,discountCurve):
        self.price = 0
        self.discountCurve = discountCurve
        self.simulationRes = simulationRes
    