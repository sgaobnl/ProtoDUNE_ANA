# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/28/2018 4:37:40 PM
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
from femb_position import femb_position
from apa_mapping import APA_MAP

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

from multiprocessing import Pipe
import multiprocessing as mp
from chn_analysis import felix_read_rawdata_all
from chn_analysis import felix_cs_chn
from chn_analysis import felix_noise_a_chn
from chn_plot_out import ped_fft_plot_avg
import pickle


if __name__ == '__main__':
    APAno = int(sys.argv[1])
    rmsdate = sys.argv[2]
    fpgdate = sys.argv[3]
    asidate = sys.argv[4]
    rmsrunno = sys.argv[5]
    fpgarunno = sys.argv[6]
    asicrunno = sys.argv[7]
    apafolder = sys.argv[8]
    jumbo_flag = (sys.argv[9] == "True")
    psd_en = (sys.argv[10] == "True")
    psd = int(sys.argv[11])
    wire_type = sys.argv[12]
    gains = [sys.argv[13]]
    tps = [sys.argv[14]]
    sum_chn = 512
    cali_freq = 500

 

    if (apafolder == "APA40"):
        rms_rootpath =  "D:/APA40/Rawdata/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "D:/APA40/Rawdata/Rawdata_" + fpgdate + "/"
        asic_rootpath = "D:/APA40/Rawdata/Rawdata_" + asidate + "/"
        apa = "APA40"
    elif (apafolder == "FELIX"):
        rms_rootpath =  "W:/"
        fpga_rootpath = "W:/"
        asic_rootpath = "W:/"
        apa = "ProtoDUNE"
    elif (apafolder != "APA"):
        rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + fpgdate + "/"
        asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + asidate + "/"
        apa = "ProtoDUNE"
    else:
        rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
        fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
        asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
        apa = "ProtoDUNE"
 
    from timeit import default_timer as timer
    s0= timer()
    print "Start...please wait..."
    
    if (apa == "APA40"):
        wibnos = [0]
        fembnos = [0,1,2,3] #0~3
    else:
        wibnos = [0,1,2,3,4]
        wibnos = [0]
        fembnos = [0,1,2,3] #0~3
    #wire_type = "V"
    #only allow one gain and one peak time run at a time, otherwise memory excess error may happen
    #gains = ["250"]  #["250", "140"]
    #tps = ["20"]#["05", "10", "20", "30"]
    
    out_path = rms_rootpath + "/" + "results/" + "Avg_fft_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+"/"
    if (os.path.exists(out_path)):
        pass
    else:
        try: 
            os.makedirs(out_path)
        except OSError:
            print "Can't create a folder, exit"
            sys.exit()
    
    apa_map = APA_MAP()
    apa_map.APA = apa
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping()

    ffts = []
    for gain in gains:
        for tp in tps:
            log_str ="" 
            chn_cnt = 0
            rmsdatas = felix_read_rawdata_all(rms_rootpath, runno = rmsrunno,  gain=gain, tp=tp, sum_chn = sum_chn, cali_freq=cali_freq )
            for wibno in wibnos:
                for fembno in fembnos:
                    if (True):
                    #if (not ((wibno == 0) and (fembno == 0) ) ) : #APA5
                    #if (not ((wibno == 2) and (fembno == 2) ) ) : #APA2
                    #if (not ((wibno == 1) and (fembno == 1) ) ) : #APA4
                    #if (not ((wibno == 0) and (fembno == 3) ) ) and \
                    #   (not ((wibno == 2) and (fembno == 0) ) ) and \
                    #   (not ((wibno == 2) and (fembno == 1) ) ) and \
                    #   (not ((wibno == 3) and (fembno == 0) ) ) : #APA3
                        chn_cnt = chn_cnt + 1
                        log_str = log_str +str(wibno)+str(fembno)+"_" 
                        #V plane
                        chns = []
                        for chn_loc in All_sort:
                            if ( chn_loc[0][0] == wire_type ):
                                chns.append(int(chn_loc[1]))
                        for chnno in chns:
                            apachn = wibno*512+128*fembno+chnno
                            print "apachn%d"%apachn
                            rmsdata = felix_cs_chn(rmsdatas, apachn )
                            chn_noise_paras = felix_noise_a_chn(rmsdata, fft_en = True, fft_s=5000, fft_avg_cycle=50 )
                            ffts.append(chn_noise_paras)
                        print "time passed %d seconds"%(timer() - s0)
        
            title = "APA" + str(APAno) + "_" + rmsrunno + "_" + log_str + wire_type + "_chns" + str(chn_cnt) + "_" + "gain" + gain + "tp" + tp
            if (psd_en):
                fp = out_path + title + "_psd%d"%psd + ".png"
            else:
                fp = out_path + title  + ".png"
            fft_pp = fp
            ped_fft_plot_avg(fft_pp, ffs=ffts, title=title, lf_flg = True, psd_en = psd_en, psd = psd)
            avgffts = ped_fft_plot_avg(fft_pp, ffs=ffts, title=title, lf_flg = False, psd_en = psd_en, psd = psd)

            ffp = out_path + title + ".fft"
            with open(ffp, "wb") as ffp:
                pickle.dump(avgffts, ffp)

    print "DONE"

