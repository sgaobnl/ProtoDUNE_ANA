# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sat Mar 24 22:23:40 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import os
from sys import exit
import os.path
import math
import multiprocessing as mp
import time

from femb_position import femb_position
from apa_mapping   import APA_MAP
from chn_analysis  import read_rawdata 
from chn_analysis  import noise_a_chn 
from chn_analysis  import cali_linear_fitplot 
from chn_analysis  import generate_rawpaths

def mp_ana_a_asic(mpout, rms_rootpath, cali_rootpath, APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, asicno=0, gain="250", tp="05" ,\
               jumbo_flag=False ):
    femb_pos_np = femb_position (APAno)
    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 
    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    feset_info = [gain, tp]
    apa_map = APA_MAP()
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping_pd()

    rmsdata  = read_rawdata(rms_rootpath, rmsrunno,  wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)
    calidata = read_rawdata(cali_rootpath, calirunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

    asic_results =[]
    for chni in range(16):
        chnno = chni + 16*asicno
        wireinfo = None
        for onewire in All_sort:
            if (int(onewire[1]) == chnno):
                wireinfo = onewire
                break
        
        chn_noise_paras = noise_a_chn(rmsdata, chnno, fft_en = False)
        rms          =  chn_noise_paras[1]
        ped          =  chn_noise_paras[2]
        hfrms        =  chn_noise_paras[7]
        hfped        =  chn_noise_paras[8]
        sfrms        =  chn_noise_paras[13]
        sfped        =  chn_noise_paras[14]
        unstk_ratio  =  chn_noise_paras[15]

        chn_cali_paras = cali_a_chn(calidata, chnno )
        encperlsb, chninl = cali_linear_fitplot(apainfo, wireinfo, feset_info, chn_cali_paras, ploten=False)
        asic_results.append([apainfo, wireinfo, feset_info, rms ,ped ,hfrms ,hfped ,sfrms ,sfped  ,unstk_ratio , encperlsb, chninl])
    mpout.put(asic_results)

def ana_a_femb(rms_rootpath, cali_rootpath, APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg",\
               wibno=0,  fembno=0,  gain="250", tp="05" ,\
               jumbo_flag=False ):
    #multiprocessing mp_ana_a_asic, process a FEMB at a time
    mpout = mp.Queue()
    mps = [ mp.Process(target=mp_ana_a_asic, args=(mpout, rms_rootpath, cali_rootpath, APAno , rmsrunno, calirunno, wibno, fembno, asicno, gain,\
                      tp, jumbo_flag ) ) for asicno in range(8)]
    for p in mps:
        p.start()
    for p in mps:
        p.join()

    if (not mpout.empty() ):
        femb_results = [mpout.get() for p in mps]
    else:
        femb_results = None

    return femb_results


def chk_a_wib (rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run01rms", calirunno = "run01fpg",\
               wibno=0,  gain="250", tp="05", jumbo_flag=False ):
    alive_fembs = []
    for fembno in range(4):
        for asicno in range(8):
            files_flg = False
            files_cs = generate_rawpaths(rms_rootpath, runno=rmsrunno, wibno=wibno,  fembno=fembno, chnno=asicno*16, gain=gain, tp=tp ) #calirun="run01fpg", 
            if (len(files_cs) == 1):
                files_flg = True
            files_cs = generate_rawpaths(cali_rootpath, runno=calirunno, wibno=wibno,  fembno=fembno, chnno=asicno*16, gain=gain, tp=tp ) #calirun="run01fpg", 
            if (len(files_cs) >= 1):
                files_flg = True
            if (not files_flg):
                break
        if files_flg:
            alive_fembs.append(fembno)
    return [wibno, alive_fembs]

def chk_a_apa (rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run01rms", calirunno = "run01fpg",\
               gain="250", tp="05" , jumbo_flag=False ):
    alive_wibs = []
    for wibno in range(5):
        alive_fembs = chk_a_wib(rms_rootpath, cali_rootpath, APAno = APAno, rmsrunno=rmsrunno, calirunno =calirunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
        alive_wibs.append( alive_fembs )
    return alive_wibs

def ana_a_wib(rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run01rms", calirunno = "run01fpg",\
               wibno=0,  gain="250", tp="05", jumbo_flag=False ):
    alive_fembs = chk_a_wib(rms_rootpath, cali_rootpath, APAno = APAno, rmsrunno=rmsrunno, calirunno =calirunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
    wib_results = []
    for fembno in alive_fembs[1]:
        print "WIB#%d FEMB%d is being analyzed..." %(wibno, fembno)
        tmp = ana_a_femb(rms_rootpath, cali_rootpath, APAno = APAno, rmsrunno=rmsrunno, calirunno =calirunno, wibno=wibno, fembno=fembno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
        wib_results.append(tmp)

##   don't use
#    wib_mpout = wib_mp.Queue()
#    wib_mps = [ wib_mp.Process(target=ana_a_femb, args=(wib_mpout, rootpath, APAno , rmsrunno, calirunno, wibno, \
#                               fembno,  gain, tp, jumbo_flag ) ) for fembno in [0,1] ] #alive_fembs[1]]
#    for p in wib_mps:
#        p.start()
#    for p in wib_mps:
#        p.join()
#    if (not wib_mpout.empty() ):
#        wib_results = [wib_mpout.get() for p in wib_mps]
#
    import pickle
    out_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + calirunno +"/"
    if (os.path.exists(out_path)):
        pass
    else:
        try: 
            os.makedirs(out_path)
        except OSError:
            print "Can't create a folder, exit"
            sys.exit()

    input_info = ["RMS Raw data Path = %s"%rms_rootpath + rmsrunno, 
                  "Cali Raw data Path = %s"%cali_rootpath + calirunno, 
                  "APA#%d"%APAno , 
                  "WIB#%d"%wibno , 
                  "Gain = %2.1f mV/fC"% (int(gain)/10.0) , 
                  "Tp = %1.1f$\mu$s"% (int(tp)/10.0)  ]
    out_result =[input_info,  wib_results]
    out_fn = "APA%d"%APAno + "_WIB%d"%wibno + "_Gain%s"%gain + "_Tp%s"%tp+  "_" + rmsrunno + "_" + calirunno + ".sum"
    fp = out_path + out_fn
    print fp
    if (os.path.isfile(fp)): 
        os.remove(fp)
    else:
        with open(fp, "wb") as fp:
            pickle.dump(out_result, fp)

def ana_a_apa(rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run01rms", calirunno = "run01fpg", gain="250", tp="05", jumbo_flag=False ):
    alive_wibs = chk_a_apa(rms_rootpath, cali_rootpath, APAno = APAno, rmsrunno=rmsrunno, calirunno =calirunno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
    for alive_fembs in alive_wibs:
        wibno = alive_fembs[0]
        ana_a_wib(rms_rootpath, cali_rootpath, APAno = APAno, rmsrunno=rmsrunno, calirunno =calirunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )



rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
cali_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
from timeit import default_timer as timer
s0= timer()
print s0
ana_a_apa(rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg",  gain="250", tp="05", jumbo_flag=False )
print timer() - s0




