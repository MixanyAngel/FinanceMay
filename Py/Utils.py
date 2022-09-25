import numpy as np
import enum
import pandas as pd

class Frequency(enum.Enum):
    Daily = 1
    Weekly = 2
    BiMonthly = 3
    Monthly = 4
    Quaterly = 5
    BiAnnualy = 6
    Annualy = 7
    BiDaily = 8
    TriDaily = 9
    QuaterDaily = 10
    Refined = 11 ## 4 times a day
    AtMaturity = 12
    

def getNbStepInAyear(frequency = Frequency.Weekly):
    
    tmp = 365
    
    if frequency == Frequency.Daily:
        tmp = 365
    elif frequency == Frequency.Weekly:
        tmp = 52
    elif frequency == Frequency.BiMonthly:
        tmp = 2*12
    elif frequency == Frequency.Monthly:
        tmp = 12
    elif frequency == Frequency.Quaterly:
        tmp = 4
    elif frequency == Frequency.BiAnnualy:
        tmp = 2
    elif frequency == Frequency.Annualy:
        tmp = 1
    elif frequency == Frequency.BiDaily:   
        tmp = 2*365    
    elif frequency == Frequency.TriDaily:   
        tmp = 3*365
        
    elif frequency == Frequency.QuaterDaily:   
        tmp = 4*365
        
    elif frequency == Frequency.Refined:   
        tmp = 5*365
    else:
        tmp = 1
        
    return tmp
        
    