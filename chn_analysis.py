# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sun Apr  8 15:05:34 2018
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
import statsmodels.api as sm
from raw_convertor import raw_convertor_peak 
from femb_position import femb_position
from apa_mapping import APA_MAP
from fft_chn import chn_rfft_psd
from fpga_dac_fit import fpga_dac_fit
from asic_dac_fit import asic_dac_fit
from highpass_filter import hp_flt_applied
from highpass_filter import hp_FIR_applied
import multiprocessing as mp
import copy

def fe_cfg(gain="250", tp="30" ):
    if (gain=="250"):
        sg = 3
    elif (gain=="140"):
        sg = 2
    elif (gain=="078"):
        sg = 1
    elif (gain=="047"):
        sg = 0
    else:
        print "Wrong gain input, exit anyway"
        eixt ()
        
    if (tp=="30"):
        st = 2
    elif (tp=="20"):
        st = 3
    elif (tp=="10"):
        st = 0
    elif (tp=="05"):
        st = 1
    else:
        print "Wrong Tp input, exit anyway"
        eixt ()
    fecfg_reg0 = st*16 + sg*4
    return fecfg_reg0, sg, st
 
def generate_rawpaths(rootpath, runno = "run01rms", wibno=0,  fembno=0, chnno=0, gain="250", tp="30" ): #calirun="run01fpg", 
    fecfg_reg0, sg, st = fe_cfg(gain=gain, tp=tp )
    
    if runno[5:8] == "rms" :
        runcode = "1"
    elif runno[5:8] == "fpg" :
        runcode = "2"
    elif runno[5:8] == "asi" :
        runcode = "4"

    if sg == 3:
        stepno = "step" + "3" + runcode 
    elif sg == 2:
        stepno = "step" + "1" + runcode 
    elif sg == 1:
        stepno = "step" + "2" + runcode 
    elif sg == 0:
        stepno = "step" + "0" + runcode 

    runpath = rootpath + runno + "/" 
    files_cs = []
    if (os.path.exists(runpath)):
        for root, dirs, files in os.walk(runpath):
            break
        steppath = None
        for onedir in dirs:
            wibpos = onedir.find("WIB")
            if ( wibpos >= 0 ):
                if ( int(onedir[wibpos+3:wibpos+5]) == wibno ) and (onedir.find(stepno) >=0 ) :
                    steppath = runpath + onedir + "/"
                    break
        if (steppath != None):
            for root2, dirs2, files2 in os.walk(steppath):
                break
            for rawfile in files2:
                chipno = chnno // 16
                chinchn = chnno  % 16
                fembasic = "FEMB" + format(fembno, "1d") + "CHIP" + format(chipno, "1d")
                fa_pos = rawfile.find(fembasic)
                if (fa_pos >= 0):
                    fe_set_rd = int(rawfile[fa_pos+11:fa_pos+13], 16) & 0x3C
                    if (fe_set_rd == fecfg_reg0) and (rawfile.find(".bin") >=0 ):
                        files_cs.append(steppath + rawfile)
    else:
        print runpath + " doesn't exist, ignore anyway!"
        files_cs = []

    return files_cs

def read_rawdata(rootpath, runno = "run01rms", wibno=0,  fembno=0, chnno=0, gain="250", tp="20", jumbo_flag=False ):
    files = generate_rawpaths(rootpath, runno, wibno,  fembno, chnno, gain, tp ) 
    datas = []
    for onefile in files:
        with open(onefile, 'rb') as f:
            raw_data = f.read()
            filelength = len(raw_data )
            smps = (filelength-1024)/2/16 
#            if smps > 200000:
#                smps = 200000

            data, feed_loc, chn_peakp, chn_peakn = raw_convertor_peak(raw_data, smps, jumbo_flag)
            ###############0         1      2       3       4     5    6    7      8           9         10#########
            datas.append([onefile, runno, wibno,  fembno, chnno, gain, tp, data, feed_loc, chn_peakp, chn_peakn])
    return datas

def noise_a_chn(rmsdata, chnno, fft_en = True, fft_s=2000, fft_avg_cycle=50, wibno=0,  fembno=0 ):
    asicchn = chnno % 16

    chnrmsdata = rmsdata[0][7][asicchn]
    feed_loc = rmsdata[0][8]
#   raw data
    len_chnrmsdata = len(chnrmsdata)
    rms =  np.std(chnrmsdata[0:100000])
    ped = np.mean(chnrmsdata[0:100000])
    data_slice = chnrmsdata[feed_loc[0]:feed_loc[1]]
    data_200ms_slice = chnrmsdata[0:200000:200]

    avg_cycle_l = 1
    if (len(chnrmsdata) >= 400000):
        fft_s_l = 400000//avg_cycle_l

    if (fft_en):
        f,p = chn_rfft_psd(chnrmsdata,  fft_s = fft_s, avg_cycle = fft_avg_cycle)
        f_l, p_l = chn_rfft_psd(chnrmsdata, fft_s = fft_s_l, avg_cycle = avg_cycle_l)
    else:
        f = None
        p = None
        f_l = None
        p_l = None


#   data after highpass filter
    flt_chn_data = hp_flt_applied(chnrmsdata, fs = 2000000, passfreq = 1000, flt_order = 3)
    flt_chn_data = np.array(flt_chn_data) +  ped 
    hfped = ped
    hfrms = np.std(flt_chn_data)
    if (fft_en):
        hff,hfp = chn_rfft_psd(flt_chn_data, fft_s = fft_s, avg_cycle = fft_avg_cycle)
        hff_l,hfp_l = chn_rfft_psd(flt_chn_data, fft_s = fft_s_l, avg_cycle = avg_cycle_l)
    else:
        hff = None
        hfp = None
        hff_l = None
        hfp_l = None
        
    hfdata_slice = flt_chn_data[feed_loc[0]:feed_loc[1]]
    hfdata_100us_slice = flt_chn_data[0:100000:200]

#   data after stuck code filter
    tmp_data = []
    lenonechn_data = len(chnrmsdata)
    for tmp in chnrmsdata:
        if ( tmp % 64  == 63 ) or ( tmp % 64  == 0 ) or ( tmp % 64  == 1 ) or ( tmp % 64  == 62 )  or ( tmp % 64  == 2 ):
            pass
        else:
            tmp_data.append(tmp)
    len_tmp_data = len(tmp_data)
    unstk_ratio =1.0 * len_tmp_data / lenonechn_data
#    if ( unstk_ratio > 0.95 ):
#        stuck_type = "Small"
#    elif ( unstk_ratio > 0.8 ):
#        stuck_type = "Middle"
#    else:
#        stuck_type = "Large"
    sfrms =  np.std(tmp_data[0:100000])
    sfped = np.mean(tmp_data[0:100000])

    chn_noise_paras = [chnno, 
                       rms,   ped,   data_slice,   data_200ms_slice,   f,   p,
                       hfrms, hfped, hfdata_slice, hfdata_100us_slice, hff, hfp,
                       sfrms, sfped, unstk_ratio, f_l, p_l, hff_l, hfp_l,
                       wibno,  fembno ]
    return chn_noise_paras

def linear_fit(x, y):
    error_fit = False 
    try:
        results = sm.OLS(y,sm.add_constant(x)).fit()
    except ValueError:
        print "Gain Error " 
        error_fit = True 
    if ( error_fit == False ):
        error_gain = False 
        try:
            slope = results.params[1]
            #print results.summary()
            #exit()
        except IndexError:
            slope = 0
            error_gain = True
        try:
            constant = results.params[0]
        except IndexError:
            constant = 0
    else:
        slope = 0
        constant = 0
        error_gain = True

    y_fit = np.array(x)*slope + constant
    delta_y = abs(y - y_fit)
    inl = delta_y / (max(y)-min(y))
    peakinl = max(inl)

    return slope, constant, peakinl, error_gain

def cali_linear_calc(chn_cali_paras):
    vdacs = []
    ampps  = []
    ampns  = []
    areaps = []
    areans = []
    fc_daclsb = chn_cali_paras[0][3]
    ped = chn_cali_paras[0][10]

    for onecp in chn_cali_paras:
        if (ped >1000): #induction plane
            if onecp[4] < 3800 : #region inside linearity
                vdacs.append(onecp[2])
                ampps.append(onecp[4])
                ampns.append(onecp[5])
                areaps.append(onecp[11])
                areans.append(onecp[12])
        elif (ped <1000): #induction plane
            if onecp[4] < 3000 : #region inside linearity
                vdacs.append(onecp[2])
                ampps.append(onecp[4])
                ampns.append(onecp[5])
                areaps.append(onecp[11])
                areans.append(onecp[12])
    fc_dacs = np.array(vdacs) * fc_daclsb
    
    if (ped >1000): #induction plane
        #amplitude, positive pulse
        ampp_fit = linear_fit(fc_dacs,  ampps )
        ampn_fit = linear_fit(fc_dacs,  ampns )
        areap_fit = linear_fit(fc_dacs, areaps)
        arean_fit = linear_fit(fc_dacs, areans)
    else:
        ampp_fit = linear_fit(fc_dacs, ampps)
        areap_fit = linear_fit(fc_dacs,areaps)
        ampn_fit =  None
        arean_fit = None

    if (ampp_fit != None):
        encperlsb = int(6250/ampp_fit[0])
        chninl    = ampp_fit[2]
    else:
        encperlsb = None
        chninl    = None

    return  encperlsb, chninl

def cali_a_chn(calidata, chnno, cap=1.85E-13, wibno=0,  fembno=0 ):
    asicchn = chnno % 16
    fc_per_v = cap / (1.602E-19 * 6250)

    calidatasort = []
    for onecali in calidata:
        onefile = onecali[0]
        fpg_pos = onefile.find("FPGADAC")
        asi_pos = onefile.find("ASICDAC")
        if (fpg_pos > 0 ):
            dac_type = "FPGADAC"
            vdac = int(onefile[fpg_pos+7: fpg_pos+9],16)
            fc_daclsb = fpga_dac_fit() * fc_per_v
            calidatasort.append([dac_type, vdac, onecali, fc_daclsb])
        elif (asi_pos > 0 ):
            dac_type = "ASICDAC"
            vdac = int(onefile[asi_pos+7: asi_pos+9],16)
            fc_daclsb = asic_dac_fit() * fc_per_v
            if (vdac > 2): # because ASIC-DAC has issue when DAC value is 0,1,2
                calidatasort.append([dac_type, vdac, onecali, fc_daclsb])
    calidatasort = sorted(calidatasort, key= lambda onecali : onecali[1])

    chn_cali_paras = [ ]
    for sonecali in calidatasort:
        chncalidata = sonecali[2][7][asicchn]
        feed_loc = sonecali[2][8]
        feed_ivl = feed_loc[1] -  feed_loc[0] 
        ppeak = np.mean(sonecali[2][9][asicchn])
        npeak = np.mean(sonecali[2][10][asicchn])
        data_slice = chncalidata[feed_loc[0]:feed_loc[1]]
        avg_data_slice = np.array(chncalidata[feed_loc[0]:feed_loc[1]])
        avg_cycles = len(feed_loc) - 2
        for loci in range(avg_cycles - 1):
            avg_data_slice = avg_data_slice +  np.array(chncalidata[feed_loc[loci+1]:feed_loc[loci+2]])
        avg_data_slice = avg_data_slice / (avg_cycles*1.0)
        dactype = sonecali[0]
        vdac = sonecali[1]
        fc_daclsb = sonecali[3]
        pp_loc = np.where (avg_data_slice == max(avg_data_slice))[0][0]
        np_loc = np.where (avg_data_slice == min(avg_data_slice))[0][0]
        ped    = np.mean (avg_data_slice[feed_ivl//2: feed_ivl])
        pp_area = np.sum (avg_data_slice[pp_loc-6:pp_loc+6]-ped)
        np_area = np.sum (avg_data_slice[np_loc-6:np_loc+6]-ped)
                               # 0   ,  1     ,  2,   3,      4,       5,           6,            7,         8,     9,     10,     11 ,    12   
        chn_cali_paras.append( [chnno, dactype, vdac, fc_daclsb, ppeak, npeak, data_slice, avg_data_slice, pp_loc, np_loc, ped, pp_area, np_area, wibno,  fembno]  )
    return chn_cali_paras

#def chk_a_chn(chkdata, chnno, cap=1.85E-13 ):
#    asicchn = chnno % 16
#    fc_per_v = cap / (1.602E-19 * 6250)
#
#    chn_chk_paras = [ ]
#    for onechk in chkdata:
#        chnchkdata = onechk[2][7][asicchn]
#        feed_loc = onechk[2][8]
#        feed_ivl = feed_loc[1] -  feed_loc[0] 
#        ppeak = np.mean(onechk[2][9][asicchn])
#        npeak = np.mean(onechk[2][10][asicchn])
#        data_slice = chnchkdata[feed_loc[0]:feed_loc[1]]
#        avg_data_slice = np.array(chnchkdata[feed_loc[0]:feed_loc[1]])
#        avg_cycles = len(feed_loc) - 2
#        for loci in range(avg_cycles - 1):
#            avg_data_slice = avg_data_slice +  np.array(chnchkdata[feed_loc[loci+1]:feed_loc[loci+2]])
#        avg_data_slice = avg_data_slice / (avg_cycles*1.0)
#        dactype = onechk[0]
#        vdac = onechk[1]
#        fc_daclsb = onechk[3]
#        pp_loc = np.where (avg_data_slice == max(avg_data_slice))[0][0]
#        np_loc = np.where (avg_data_slice == min(avg_data_slice))[0][0]
#        ped    = np.mean (avg_data_slice[feed_ivl//2: feed_ivl])
#        pp_area = np.sum (avg_data_slice[pp_loc-6:pp_loc+6]-ped)
#        np_area = np.sum (avg_data_slice[np_loc-6:np_loc+6]-ped)
#                               # 0   ,  1     ,  2,   3,      4,       5,           6,            7,         8,     9,     10,     11 ,    12   
#        chn_cali_paras.append( [chnno, dactype, vdac, fc_daclsb, ppeak, npeak, data_slice, avg_data_slice, pp_loc, np_loc, ped, pp_area, np_area]  )
#    return chn_cali_paras


def ana_a_chn(rms_rootpath,  cali_rootpath, mode="CHN", APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, chnno=0, gain="250", tp="20", \
               jumbo_flag=False, fft_en= True, fft_s=5000, fft_avg_cycle=50, cap=1.85E-13 ):
    femb_pos_np = femb_position (APAno)
    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 

    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    apa_map = APA_MAP()
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping_pd()
    wireinfo = None
    for onewire in All_sort:
        if (int(onewire[1]) == chnno):
            wireinfo = onewire
            break
    feset_info = [gain, tp]
    rmsdata = read_rawdata(rms_rootpath, rmsrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    calidata = read_rawdata(cali_rootpath, calirunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    
    chn_noise_paras = noise_a_chn(rmsdata, chnno,fft_en, fft_s, fft_avg_cycle, wibno, fembno)
    chn_cali_paras  = cali_a_chn (calidata, chnno, cap, wibno, fembno )
#    for j in range(10):
#    for i in range(16):
#        chn_noise_paras = noise_a_chn(rmsdata, i,fft_en, fft_s, fft_avg_cycle, wibno, fembno)
#    for j in range(100):
#    for i in range(16):
#        chn_cali_paras  = cali_a_chn (calidata, i, cap, wibno, fembno )
#    a = chn_noise_paras
#    b = chn_cali_paras 

####multiprocessing, 
def mp_noise_a_chn(cc, rmsdata, chnno, fft_en = True, fft_s=2000, fft_avg_cycle=50, wibno=0, fembno=0):
    chn_noise_paras = noise_a_chn(rmsdata, chnno,fft_en, fft_s, fft_avg_cycle, wibno, fembno)
#    for j in range(10):
#    for i in range(16):
#        chn_noise_paras = noise_a_chn(rmsdata, i,fft_en, fft_s, fft_avg_cycle, wibno, fembno)
    cc.send([1, chn_noise_paras])
    cc.close()

def mp_cali_a_chn(cc, calidata, chnno, cap=1.85E-13 , wibno=0, fembno=0):
    chn_cali_paras = cali_a_chn(calidata, chnno, cap, wibno, fembno )
#    for j in range(200):
#    for i in range(16):
#        chn_cali_paras = cali_a_chn(calidata, i, cap, wibno, fembno )
    cc.send([1, chn_cali_paras])
    cc.close()

def mp_ana_a_chn(rms_rootpath,  cali_rootpath, mode="CHN", APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, chnno=0, gain="250", tp="20", \
               jumbo_flag=False, fft_en= True, fft_s=5000, fft_avg_cycle=50, cap=1.85E-13 ):
    femb_pos_np = femb_position (APAno)

    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 

    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    apa_map = APA_MAP()
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping_pd()
    wireinfo = None
    for onewire in All_sort:
        if (int(onewire[1]) == chnno):
            wireinfo = onewire
            break
    feset_info = [gain, tp]
    rmsdata = read_rawdata(rms_rootpath, rmsrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    calidata = read_rawdata(cali_rootpath, calirunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    
    from multiprocessing import Pipe
    pc1, cc1 = Pipe()
    pc2, cc2 = Pipe()
    noise_a_chn_argvs = (cc1, rmsdata, chnno,fft_en, fft_s, fft_avg_cycle, wibno, fembno)
    cali_a_chn_argvs  = (cc2, calidata, chnno, cap )
    p1 = mp.Process(target=mp_noise_a_chn, args=noise_a_chn_argvs)
    p2 = mp.Process(target=mp_cali_a_chn,  args=cali_a_chn_argvs)
    p1.start()
    p2.start()
    chn_noise_paras = pc1.recv()
    chn_cali_paras  = pc2.recv()
    p1.join()
    p2.join()
 
#    a = chn_noise_paras
#    b = chn_cali_paras 

