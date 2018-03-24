# -*- coding: utf-8 -*-
"""
File Name: read_mean.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/9/2016 7:12:33 PM
Last modified: Thu Mar 22 18:02:27 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import statsmodels.api as sm

def fpga_dac_fit():
    cacu_dac_o = [
              0.606, 0.625, 0.644, 0.663, 0.682, 0.701, 0.720, 0.739,
              0.758, 0.777, 0.796, 0.815, 0.834, 0.853, 0.872, 0.891, 
              0.909, 0.928, 0.947, 0.966, 0.985, 1.004, 1.023, 1.042, 
              1.061, 1.080, 1.099, 1.118, 1.137, 1.156, 1.175, 1.194,
              1.213, 1.232, 1.251, 1.269, 1.288, 1.307, 1.326, 1.345,
              1.364, 1.383, 1.402, 1.421, 1.440, 1.459, 1.478, 1.497,
              1.516, 1.535, 1.554, 1.573, 1.592, 1.611, 1.629, 1.648,
              1.667, 1.686, 1.705, 1.724, 1.743, 1.762, 1.781, 1.800,
             ]
    cacu = cacu_dac_o

    delta_cacu = []
    for i in cacu:
        delta_cacu.append(i - cacu[0]) 

    cacu_len = len(delta_cacu)
    cx = np.arange(cacu_len)
    delta_cacu_np = np.array(delta_cacu)
    cresults = sm.OLS(delta_cacu_np,sm.add_constant(cx)).fit()
    cslope = cresults.params[1]
    cconstant = cresults.params[0]

    return cslope

#a=  fpga_dac_fit()
#print a
