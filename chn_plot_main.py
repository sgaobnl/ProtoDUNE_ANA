# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 10/23/2018 7:21:29 PM
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
import sys
import os.path
import math

import multiprocessing as mp
from chn_plot_out import plot_a_chn


if __name__ == '__main__':
    APAno = int(sys.argv[1])
    rmsdate = sys.argv[2]
    fpgdate = sys.argv[3]
    asidate = sys.argv[4]
    rmsrunno = sys.argv[5]
    fpgarunno = sys.argv[6]
    asicrunno = sys.argv[7]
    apafolder = sys.argv[8]
    wibno  = int(sys.argv[9])
    fembno  = int(sys.argv[10])
    chnno  = int(sys.argv[11])

    print apafolder
    if (apafolder == "APA40"):
        rms_rootpath =  "D:/APA40/Rawdata/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "D:/APA40/Rawdata/Rawdata_" + fpgdate + "/"
        asic_rootpath = "D:/APA40/Rawdata/Rawdata_" + asidate + "/"
    elif (apafolder == "SBND"):
        rms_rootpath =  "D:/Ledge_Study/Rawdata/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "D:/Ledge_Study/Rawdata/Rawdata_" + fpgdate + "/"
        asic_rootpath = "D:/Ledge_Study/Rawdata/Rawdata_" + asidate + "/"
    else:
        rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
        fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
        asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
 
    from timeit import default_timer as timer
    s0= timer()
    print "Start...please wait..."
    
    gains = ["250","140","078","047"] 
    tps = ["05", "10", "20", "30"]
    #tps = [  "20"]
    jumbo_flag = True
#    wib_femb_chns = [  
#                        #wib(0-4), femb(0-3), chn(0~127)
#                        #[0, 2, 120   ],
#                        [wibno, fembno, chnno]
#                    ]    
    wib_femb_chns = [  ]
    for i in range(64,128,1):
        wib_femb_chns.append( [0, 0, i] )
    
    for wfc in wib_femb_chns:
        wibno = wfc[0]
        fembno = wfc[1]
        chnno = wfc[2]
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
                 p = mp.Process(target=plot_a_chn, args=ana_a_chn_args)
                 mps.append(p)
        for p in mps:
            p.start()
        for p in mps:
            p.join()
        #        ana_a_chn(rms_rootpath, asic_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, wibno, fembno, chnno, gain, tp, jumbo_flag)
        print "time passed %d seconds"%(timer() - s0)
    print "DONE"

