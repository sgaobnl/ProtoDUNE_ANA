# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/28/2018 4:35:29 PM
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
import struct

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
        exit ()
        
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
 
def felix_generate_rawpaths(rootpath, runno = "run01rms", gain="250", tp="30" ): #calirun="run01fpg", 
    fecfg_reg0, sg, st = fe_cfg(gain=gain, tp=tp )
    
    runpath = rootpath + runno + "/" 

    files_cs = []
    if (os.path.exists(runpath)):
        for root, dirs, files in os.walk(runpath):
            break
        for rawfile in files:
            if (rawfile.find(gain) >=0 ) and (rawfile.find(tp) >=0 ):
                files_cs.append(runpath + rawfile)
    else:
        print runpath + " doesn't exist, ignore anyway!"
        files_cs = []
    return files_cs


def felix_read_rawdata_all(rootpath, runno = "run01rms", gain="250", tp="20", sum_chn = 512, cali_freq = 500 ):
    files = felix_generate_rawpaths(rootpath, runno, gain, tp ) 
    datas = []
    for onefile in files:
        with open(onefile, 'rb') as f:
            print onefile
            raw_data = f.read()
            len_raw = (len(raw_data)//1024)*512
            dataNtuple =struct.unpack_from(">%dH"%(len_raw),raw_data)

            for chn in range(sum_chn):
                wibno = chn // 512
                fembno = (chn%512)//128
                fembchn = (chn%512)%128

                chn_tuple = dataNtuple[chn::sum_chn]
                sps_len = len(chn_tuple)

                max_1st = np.max( chn_tuple[0:cali_freq] )
                max_1st_pos = np.where(chn_tuple[0:cali_freq] == max_1st)[0][0]
                max_1st_pos = max_1st_pos + cali_freq - 150
                feed_loc = range(max_1st_pos-50,sps_len-2*cali_freq,cali_freq)

                chn_peakp = []
                chn_peakn = []
                for tmp in range(len(feed_loc)-1):
                    chn_peakp.append ( np.max(chn_tuple[feed_loc[tmp]:feed_loc[tmp]+cali_freq ]) )
                    chn_peakn.append ( np.min(chn_tuple[feed_loc[tmp]:feed_loc[tmp]+cali_freq ]) )

                apachn = chn
                datas.append([onefile, runno, apachn, wibno, fembno, fembchn, gain, tp, chn_tuple, feed_loc, chn_peakp, chn_peakn])
    return datas

def felix_cs_chn(datas, apachn=0 ):
    chndatas = []
    for chndata in datas:
        if chndata[2] == apachn:
            chndatas.append(chndata)  
    return chndatas 


def felix_read_rawdata_chn(rootpath, runno = "run01rms", apachn=0, gain="250", tp="20", sum_chn = 512, cali_freq = 500 ):
    #files = felix_generate_rawpaths(rootpath, runno, wibno,  fembno, chnno, gain, tp ) 
    files = felix_generate_rawpaths(rootpath, runno, gain, tp ) 
    datas = []
    for onefile in files:
        with open(onefile, 'rb') as f:
            raw_data = f.read()
            len_raw = (len(raw_data)//1024)*512
            dataNtuple =struct.unpack_from(">%dH"%(len_raw),raw_data)

            chn = apachn
            wibno = chn // 512
            fembno = (chn%512)//128
            fembchn = (chn%512)%128

            chn_tuple = dataNtuple[chn::sum_chn]
            sps_len = len(chn_tuple)

            max_1st = np.max( chn_tuple[0:cali_freq] )
            max_1st_pos = np.where(chn_tuple[0:cali_freq] == max_1st)[0][0]
            max_1st_pos = max_1st_pos + cali_freq - 150
            feed_loc = range(max_1st_pos-50,sps_len-2*cali_freq,cali_freq)

            chn_peakp = []
            chn_peakn = []
            for tmp in range(len(feed_loc)-1):
                chn_peakp.append ( np.max(chn_tuple[feed_loc[tmp]:feed_loc[tmp]+cali_freq ]) )
                chn_peakn.append ( np.min(chn_tuple[feed_loc[tmp]:feed_loc[tmp]+cali_freq ]) )
            datas.append([onefile, runno, apachn,  wibno, fembno, fembchn, gain, tp, chn_tuple, feed_loc, chn_peakp, chn_peakn])
    return datas

def felix_noise_a_chn(chndata, fft_en = True, fft_s=2000, fft_avg_cycle=50 ):
#    rmsdata = felix_cs_chn(datas, apachn )
    rmsdata = chndata
    apachn = rmsdata[0][2]
    wibno = rmsdata[0][3]
    fembno = rmsdata[0][4]
    chnrmsdata = rmsdata[0][8]
    feed_loc = rmsdata[0][9]
    len_chnrmsdata = len(chnrmsdata)
    rms =  np.std(chnrmsdata[0:100000])
    ped = np.mean(chnrmsdata[0:100000])
    data_slice = chnrmsdata[feed_loc[0]:feed_loc[1]]
    data_200ms_slice = chnrmsdata[0:200000:200]

    avg_cycle_l = 1
    if (len(chnrmsdata) >= 400000):
        fft_s_l = 400000//avg_cycle_l
    else:
        fft_s_l = len(chnrmsdata)

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
    sfrms =  np.std(tmp_data[0:100000])
    sfped = np.mean(tmp_data[0:100000])
    chn_noise_paras = [apachn, 
                       rms,   ped,   data_slice,   data_200ms_slice,   f,   p,
                       hfrms, hfped, hfdata_slice, hfdata_100us_slice, hff, hfp,
                       sfrms, sfped, unstk_ratio, f_l, p_l, hff_l, hfp_l,
                       wibno,  fembno ]
    return chn_noise_paras

#def felix_cali_a_chn(datas, apachn=0, cap=1.85E-13 ):
def felix_cali_a_chn(chndata,  cap=1.85E-13 ):
    fc_per_v = cap / (1.602E-19 * 6250)
#    calidata = felix_cs_chn(datas, apachn )
    calidata = chndata
    calidatasort = []
    for onecali in calidata:
        apachn = onecali[0][2]
        wibno = onecali[0][3]
        fembno = onecali[0][4]
        onefile = onecali[0]
        fpg_pos = onefile.find("_FPGAdac")
        asi_pos = onefile.find("_ASICdac")
        if (fpg_pos > 0 ):
            dac_type = "FPGADAC"
            vdac = int(onefile[fpg_pos+8: fpg_pos+10],16)
            fc_daclsb = fpga_dac_fit() * fc_per_v
            calidatasort.append([dac_type, vdac, onecali, fc_daclsb])
        elif (asi_pos > 0 ):
            dac_type = "ASICDAC"
            vdac = int(onefile[asi_pos+8: asi_pos+10],16)
            fc_daclsb = asic_dac_fit() * fc_per_v
            if (vdac > 2): # because ASIC-DAC has issue when DAC value is 0,1,2
                calidatasort.append([dac_type, vdac, onecali, fc_daclsb])
    #calidatasort = sorted(calidatasort, key= lambda onecali : onecali[1])
    calidatasort = sorted(calidatasort, key= lambda tmp : tmp[1])

    chn_cali_paras = [ ]
    for sonecali in calidatasort:
        chncalidata = sonecali[2][8]
        feed_loc = sonecali[2][9]
        feed_ivl = feed_loc[1] -  feed_loc[0] 
        ppeak = np.mean(sonecali[2][10])
        npeak = np.mean(sonecali[2][11])
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
        chn_cali_paras.append( [apachn, dactype, vdac, fc_daclsb, ppeak, npeak, data_slice, avg_data_slice, pp_loc, np_loc, ped, pp_area, np_area, wibno,  fembno]  )
    return chn_cali_paras

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

def felix_ana_a_chn(rmsdatas,  calidatas, mode="CHN", APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg", apachn=0, gain="250", tp="20", \
               fft_en= True, fft_s=5000, fft_avg_cycle=50, cap=1.85E-13, apa="ProtoDUNE" ):
    femb_pos_np = femb_position (APAno)
    wibno = apachn // 512
    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 

    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    apa_map = APA_MAP()
    apa_map.APA=apa
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping()
    wireinfo = None
    for onewire in All_sort:
        if (int(onewire[1]) == chnno):
            wireinfo = onewire
            break
    feset_info = [gain, tp]
    chn_noise_paras = felix_noise_a_chn(rmsdatas, apachn,fft_en, fft_s, fft_avg_cycle)
    chn_cali_paras  = felix_cali_a_chn (calidatas, apachn, cap )

