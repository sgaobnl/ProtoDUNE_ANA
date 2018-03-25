# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sun Mar 25 14:09:09 2018
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
import sys
import os.path
import math
import multiprocessing as mp
import time
import pickle
from femb_position import femb_position
from apa_mapping   import APA_MAP
from chn_analysis  import read_rawdata 
from chn_analysis  import noise_a_chn 
from chn_analysis  import cali_a_chn 
from chn_analysis  import cali_linear_calc 
from chn_analysis  import generate_rawpaths
from multiprocessing import Pipe
import multiprocessing as wib_mp

def mp_ana_a_asic(mpout, rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",
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
    fpg_cali_flg = False 
    if (os.path.exists(fpga_rootpath + fpgarunno)):
        fpg_cali_flg = True
        fpgadata = read_rawdata(fpga_rootpath, fpgarunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)
    asi_cali_flg = False
    if (os.path.exists(asic_rootpath + asicrunno)):
        asi_cali_flg = True
        asicdata = read_rawdata(asic_rootpath, asicrunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

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

        if (fpg_cali_flg):
            chn_fpga_paras = cali_a_chn(fpgadata, chnno )
            fpg_encperlsb, fpg_chninl = cali_linear_calc(chn_fpga_paras)
        else:
            fpg_encperlsb, fpg_chninl = [-1, -1]
        if (asi_cali_flg):
            chn_asic_paras = cali_a_chn(asicdata, chnno )
            asi_encperlsb, asi_chninl = cali_linear_calc(chn_asic_paras)
        else:
            asi_encperlsb, asi_chninl = [-1, -1]
        asic_results.append([rms ,ped ,hfrms ,hfped ,sfrms ,sfped  ,unstk_ratio, fpg_cali_flg, fpg_encperlsb, fpg_chninl, asi_cali_flg, asi_encperlsb, asi_chninl])

    toqueue = [apainfo, wireinfo, feset_info] + asic_results
    size_toqueue = sys.getsizeof(toqueue)
    if (size_toqueue*64 > 32768): 
        print "Since multiprocessing.queue is using, the maximum buffer size can't exceed 32768 bytes, there is potiential risk using queue function."
        print "print limit the size of to queue to less than 512bytes, or re-write mp_ana_a_asic with Pipe" 
        sys.exit()
    else:
        mpout.put(toqueue)

def pipe_ana_a_asic(cc, rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",
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
    fpg_cali_flg = False 
    if (os.path.exists(fpga_rootpath + fpgarunno)):
        fpg_cali_flg = True
        fpgadata = read_rawdata(fpga_rootpath, fpgarunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)
    asi_cali_flg = False
    if (os.path.exists(asic_rootpath + asicrunno)):
        asi_cali_flg = True
        asicdata = read_rawdata(asic_rootpath, asicrunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

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

        if (fpg_cali_flg):
            chn_fpga_paras = cali_a_chn(fpgadata, chnno )
            fpg_encperlsb, fpg_chninl = cali_linear_calc(chn_fpga_paras)
        else:
            fpg_encperlsb, fpg_chninl = [-1, -1]
        if (asi_cali_flg):
            chn_asic_paras = cali_a_chn(asicdata, chnno )
            asi_encperlsb, asi_chninl = cali_linear_calc(chn_asic_paras)
        else:
            asi_encperlsb, asi_chninl = [-1, -1]
        asic_results.append([rms ,ped ,hfrms ,hfped ,sfrms ,sfped  ,unstk_ratio, fpg_cali_flg, fpg_encperlsb, fpg_chninl, asi_cali_flg, asi_encperlsb, asi_chninl])

    toqueue = [apainfo, wireinfo, feset_info] + asic_results
    cc.send(toqueue)

def ana_a_femb(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  fembno=0,  gain="250", tp="05" ,\
               jumbo_flag=False ):
    #multiprocessing mp_ana_a_asic, process a FEMB at a time
    mpout = mp.Queue()
    mps = [ mp.Process(target=mp_ana_a_asic, args=(mpout, rms_rootpath, fpga_rootpath, asic_rootpath, APAno , rmsrunno, fpgarunno, asicrunno, wibno, fembno, asicno, gain,\
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

def pipe_ana_a_femb(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  fembno=0,  gain="250", tp="05" ,\
               jumbo_flag=False ):
    #multiprocessing mp_ana_a_asic, process a FEMB at a time
    femb_results = []
    mps = []
    for asicno in range(8):
        pc, cc = Pipe()
        p = mp.Process(target=pipe_ana_a_asic, args=(cc, rms_rootpath, fpga_rootpath, asic_rootpath, APAno , rmsrunno, fpgarunno, asicrunno, wibno, fembno, asicno, gain, tp, jumbo_flag ) ) 
        mps.append([pc, cc, p])

    for onep in mps:
        onep[2].start()

    for onep in mps:
        femb_results.append(onep[0].recv())

    for onep in mps:
        onep[2].join()
 
    return femb_results


def mp_ana_a_femb(cc, rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  fembno=0,  gain="250", tp="05" ,\
               jumbo_flag=False ):
    #multiprocessing mp_ana_a_asic, process a FEMB at a time
    print "WIB#%d FEMB%d is being analyzed..." %(wibno, fembno)
    tmp = pipe_ana_a_femb(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, wibno=wibno, fembno=fembno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
    cc.send(tmp)
    cc.close()


def chk_a_wib (rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  gain="250", tp="05", jumbo_flag=False ):
    alive_fembs = []
    for fembno in range(4):
        for asicno in range(8):
            rms_files_flg = False
            fpg_files_flg = False
            asi_files_flg = False
            files_cs = generate_rawpaths(rms_rootpath, runno=rmsrunno, wibno=wibno,  fembno=fembno, chnno=asicno*16, gain=gain, tp=tp ) 
            if (len(files_cs) == 1):
                rms_files_flg = True
            files_cs = generate_rawpaths(fpga_rootpath, runno=fpgarunno, wibno=wibno,  fembno=fembno, chnno=asicno*16, gain=gain, tp=tp ) 
            if (len(files_cs) >= 1):
                fpg_files_flg = True
            files_cs = generate_rawpaths(asic_rootpath, runno=asicrunno, wibno=wibno,  fembno=fembno, chnno=asicno*16, gain=gain, tp=tp ) 
            if (len(files_cs) >= 1):
                asi_files_flg = True
            if (not rms_files_flg):
                break
            if (not rms_files_flg):
                if (not (fpg_files_flg or asi_files_flg) ):
                    break
        if rms_files_flg and (fpg_files_flg or asi_files_flg):
            alive_fembs.append(fembno)
    return [wibno, alive_fembs]

def chk_a_apa (rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, rmsrunno = "run01rms",fpgarunno = "run01fpg", asicrunno = "run01asi",\
               gain="250", tp="05" , jumbo_flag=False ):
    alive_wibs = []
    for wibno in range(5):
        alive_fembs = chk_a_wib(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
        alive_wibs.append( alive_fembs )
    return alive_wibs

def ana_a_wib(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = 4, rmsrunno = "run01rms",fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  gain="250", tp="05", jumbo_flag=False, pipe_en = False ):
    alive_fembs = chk_a_wib(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
    wib_results = []

    if pipe_en:
        pc0, cc0 = Pipe()
        pc1, cc1 = Pipe()
        pc2, cc2 = Pipe()
        pc3, cc3 = Pipe()
        pcs = [pc0, pc1, pc2, pc3]
        ccs = [cc0, cc1, cc2, cc3]
 
        wib_wps = []
        for fembno in alive_fembs[1]:
            cc = ccs[fembno]
            ptmp =  wib_mp.Process(target=mp_ana_a_femb, args=(cc, rms_rootpath, fpga_rootpath, asic_rootpath, APAno , rmsrunno, fpgarunno, asicrunno, wibno, fembno,  gain, tp, jumbo_flag ) ) 
            wib_wps.append(ptmp)
        for p in wib_wps:
            p.start()
 
        for fembno in alive_fembs[1]:
            pc = pcs[fembno]
            wib_results.append(pc.recv())

        for p in wib_wps:
            p.join()

    else:
        for fembno in alive_fembs[1]:
            print "WIB#%d FEMB%d is being analyzed..." %(wibno, fembno)
            tmp = ana_a_femb(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, wibno=wibno, fembno=fembno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag )
            wib_results.append(tmp)

    out_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
    if (os.path.exists(out_path)):
        pass
    else:
        try: 
            os.makedirs(out_path)
        except OSError:
            print "Can't create a folder, exit"
            sys.exit()

    input_info = ["RMS Raw data Path = %s"%rms_rootpath + rmsrunno, 
                  "FPGA-DAC Cali Raw data Path = %s"%fpga_rootpath + fpgarunno, 
                  "ASIC-DAC Cali Raw data Path = %s"%asic_rootpath + asicrunno, 
                  "APA#%d"%APAno , 
                  "WIB#%d"%wibno , 
                  "Gain = %2.1f mV/fC"% (int(gain)/10.0) , 
                  "Tp = %1.1f$\mu$s"% (int(tp)/10.0)  ]
    out_result =[input_info,  wib_results]
    out_fn = "APA%d"%APAno + "_WIB%d"%wibno + "_Gain%s"%gain + "_Tp%s"%tp+  "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+ ".sum"
    fp = out_path + out_fn
    print fp
    if (os.path.isfile(fp)): 
        os.remove(fp)
        with open(fp, "wb") as fp:
            pickle.dump(out_result, fp)

def ana_a_apa(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = 4, rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asic", gain="250", tp="05", jumbo_flag=False ):
    alive_wibs = chk_a_apa(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, gain=gain, tp=tp, jumbo_flag=jumbo_flag )
    for alive_fembs in alive_wibs:
        wibno = alive_fembs[0]
        ana_a_wib(rms_rootpath, fpga_rootpath, asic_rootpath, APAno = APAno, rmsrunno=rmsrunno, fpgarunno =fpgarunno, asicrunno =asicrunno, wibno=wibno,  gain=gain, tp=tp, jumbo_flag=jumbo_flag, pipe_en = True )


if __name__ == '__main__':
    rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
    #rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
    #ali_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
    from timeit import default_timer as timer
    s0= timer()
    print "Start..., please wait..."
    APAno=4
    rmsrunno = "run01rms" #
    fpgarunno = "run01fpg" #
    asicrunno = "run01asi" #
    wibno = 0 #0~4
    gains = ["250", "140"] 
    tps = ["05", "10", "20", "30"]
    jumbo_flag = False
    
    for gain in gains: 
        for tp in tps:
            print "Gain = %2.1f mV/fC, "% (int(gain)/10.0) +  "Tp = %1.1fus"% (int(tp)/10.0) 
            ana_a_apa(rms_rootpath, fpga_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, gain, tp, jumbo_flag)
            print "time passed %d seconds"%(timer() - s0)
    print "DONE"

