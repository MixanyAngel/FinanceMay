from .BasePricer import *
import numpy as np
import pandas as pd
from .Market import *
from .ResultSimulation import *
from .BaseProduct import *
import matplotlib.pyplot as plt

#https://math.stackexchange.com/questions/3588503/proving-approximation-of-second-order-derivative-of-multiple-variables

class GenerateMCSensi:
    def __init__(self,product,pricer,model,nbSim = 5000,discretStep=Frequency.TriDaily):
        self.model = model
        self.product = product
        self.Npaths = nbSim
        self.discretStep = discretStep
        self.marketObj = model.marketObj.shockSpot(0)
        self.pricer = pricer
        
        refDif =  self.model.generatePaths(product.maturity,Npaths=self.Npaths,listT=product.counponsSimulDates(),discretStep=self.discretStep)
        productPricer = pricer(product,refDif,self.marketObj.discount)        
        self.refPrice = productPricer.price
        
        
    def runPriceAndGreeks(self,listSpots = [0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.5],epsilonShock = 0.01,epsilonVolShock = 0.1,epsilonRateShock = 0.1,withRecalib = True):
        import time
        t = time.time()
        
        spot = self.marketObj.spot
        dictSpotsMarket = self.marketObj.getMarketsSpotRange(listSpots)
        
        dictRes = dict()
        dictRes['Spot'] = []
        dictRes['Price'] = []
        dictRes['Delta'] = []
        dictRes['Gamma'] = []
        dictRes['Vega'] = []
        dictRes['Vomma'] = []
        dictRes['Vanna'] = []
        dictRes['Rho'] = []
        dictRes['RepoSensi'] = []
        
        def getPrice(market):
            self.model.marketObj = market
            
            if withRecalib:
                self.model.recalibrate()
                
            pathSpot =  self.model.generatePaths(self.product.maturity,Npaths=self.Npaths,listT=self.product.counponsSimulDates(),discretStep=self.discretStep)
            productPricer = self.pricer(self.product,pathSpot,self.model.marketObj.discount)        
            
            return productPricer.price
        
        for spotRel in dictSpotsMarket:
            print(str(spotRel)+' is being treated')
            
            dictRes['Spot'].append(spotRel)
            
            mkt = dictSpotsMarket[spotRel]            
            priceSpotRef = getPrice(mkt)
            
            #dictPrices[spotRel] = priceSpotRef
            dictRes['Price'].append(priceSpotRef)
            
            mktEpsilonPlus = mkt.shockSpot(epsilonShock)
            priceSpotShockPlus = getPrice(mktEpsilonPlus)
            
            mktEpsilonMinus = mkt.shockSpot(-epsilonShock)
            priceSpotShockMinus = getPrice(mktEpsilonMinus)
            
            delta = (priceSpotShockPlus - priceSpotShockMinus)/(2*epsilonShock)
            #dictDeltas[spotRel] = delta
            dictRes['Delta'].append(delta)
            
            gamma = (priceSpotShockPlus + priceSpotShockMinus - 2*priceSpotRef)/(epsilonShock*epsilonShock)
            #dictGammas[spotRel] = gamma
            dictRes['Gamma'].append(gamma)
            
            mktvegaShockedPlus = mkt.shockVol(epsilonVolShock)
            pricevegaShockedPlus = getPrice(mktvegaShockedPlus)
            
            mktvegaShockedMinus = mkt.shockVol(-epsilonVolShock)
            pricevegaShockedMinus = getPrice(mktvegaShockedMinus)
            
            vega = (pricevegaShockedPlus-pricevegaShockedMinus)/(2*epsilonVolShock)            
            dictRes['Vega'].append(vega)
            
            vomma = (pricevegaShockedPlus + pricevegaShockedMinus - 2*priceSpotRef)/(epsilonVolShock*epsilonVolShock)
            dictRes['Vomma'].append(vomma)
            
            mktShockSpotVolPlus = mktEpsilonPlus.shockVol(epsilonVolShock)
            #mktShockSpotVolMinus = mktEpsilonMinus.shockVol(-epsilonVolShock)
            
            pricexyplus = getPrice(mktShockSpotVolPlus)
            #pricexyminus = getPrice(mktShockSpotVolMinus)
            
            tmpgamma = gamma*(epsilonShock*epsilonShock)
            tmpvomma = vomma*(epsilonVolShock*epsilonVolShock)
            
            vanna = (pricexyplus - priceSpotShockPlus - pricevegaShockedPlus +priceSpotRef)/(epsilonVolShock*epsilonShock)
            dictRes['Vanna'].append(vanna)
            #dictVegas[spotRel] = vega
            
            mktdfshockPlus = mkt.shockDiscountCurve(epsilonRateShock)
            mktdfshockMinus = mkt.shockDiscountCurve(-epsilonRateShock)
            
            priceRhoPlus = getPrice(mktdfshockPlus)
            priceRhoMinus = getPrice(mktdfshockMinus)
            
            rho = (priceRhoPlus-priceRhoMinus)/(2*epsilonRateShock)
            dictRes['Rho'].append(rho)
            
            
            mktreposhockPlus = mkt.shockRepoCurve(epsilonRateShock)
            mktreposhockMinus = mkt.shockRepoCurve(-epsilonRateShock)
            
            priceRepoPlus = getPrice(mktreposhockPlus)
            priceRepoMinus = getPrice(mktreposhockMinus)
            
            sensiRepo = (priceRepoPlus-priceRepoMinus)/(2*epsilonRateShock)
            dictRes['RepoSensi'].append(sensiRepo)
            
        self.model.marketObj = self.marketObj
            
        if withRecalib:
            self.model.recalibrate()
                
        print(time.time() - t)
        return pd.DataFrame.from_dict(dictRes).set_index(['Spot'])

    
def mcSensiPlot(resSensi):
    
    import warnings
    warnings.filterwarnings("ignore")

    plt.rcParams["figure.figsize"] = (15,7)
    x = resSensi.Price.index

    fig, axs = plt.subplots(2, 4,constrained_layout = True)
    fig.suptitle('Price and Greeks')
    axs[0, 0].plot(x, resSensi.Price.values)
    axs[0, 0].set_title('Price')
    
    
    axs[0, 1].plot(x, resSensi.Delta.values, 'tab:orange')
    axs[0, 1].set_title('Delta')
    
    axs[0, 2].plot(x, resSensi.Vega.values, 'tab:red')
    axs[0, 2].set_title('Vega')
    
    axs[1, 0].plot(x, resSensi.Vanna.values,'tab:brown')
    axs[1, 0].set_title('Vanna')
    
    axs[1, 1].plot(x, resSensi.Gamma.values, 'tab:green')
    axs[1, 1].set_title('Gamma')    

    axs[1, 2].plot(x, resSensi.Vomma.values,'tab:purple')
    axs[1, 2].set_title('Vomma')
    
    axs[0, 3].plot(x, resSensi.Rho.values, 'tab:cyan')
    axs[0, 3].set_title('Rho')
    
    axs[1, 3].plot(x, resSensi.RepoSensi.values, 'y')
    axs[1, 3].set_title('RepoSensi')
    
    for ax in axs.flat:
        ax.set(xlabel='Spot', ylabel='Values')
        ax.grid()    