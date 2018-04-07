# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Tue Apr  3 17:15:14 2018
"""
import matplotlib
matplotlib.use('Agg')
#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import struct
import os
from sys import exit
import os.path
import math

import multiprocessing as mp
from chn_plot_out import ana_a_chn


if __name__ == '__main__':
    APAno=3
    rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_02_07_2018/"%APAno
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_02_07_2018/"%APAno
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_02_07_2018/"%APAno
    #rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
    #fpga_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
    #asic_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
    from timeit import default_timer as timer
    s0= timer()
    print "Start...please wait..."
    
    rmsrunno = "run01rms" #
    fpgarunno = "run01fpg" #
    asicrunno = "run01asi" #
    wibno = 4 #0~4
    fembno = 0 #0~3
    chnno  = 0 #0~127
    chnnos  = [17, 18, 19, 20, 59, 60, 61, 62] #0~127
    gains = ["250"] 
    tps = ["05", "10", "20", "30"]
    jumbo_flag = False
    
    
    for chnno in chnnos:
        out_path = rms_rootpath + "/" + "results/" + "Chns_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+"/"
        if (os.path.exists(out_path)):
            pass
        else:
            try: 
                os.makedirs(out_path)
            except OSError:
                print "Can't create a folder, exit"
                exit()
        mps = []
        for gain in gains: 
            for tp in tps:
                 ana_a_chn_args = (out_path, rms_rootpath, asic_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, wibno, fembno, chnno, gain, tp, jumbo_flag)
                 p = mp.Process(target=ana_a_chn, args=ana_a_chn_args)
                 mps.append(p)
        for p in mps:
            p.start()
        for p in mps:
            p.join()
        #        ana_a_chn(rms_rootpath, asic_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, wibno, fembno, chnno, gain, tp, jumbo_flag)
        print "time passed %d seconds"%(timer() - s0)
    print "DONE"

