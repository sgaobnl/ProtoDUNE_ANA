# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sat Mar 24 08:03:02 2018
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
import struct
import os
from sys import exit
import os.path
import math
import statsmodels.api as sm
from raw_convertor import raw_convertor 
from raw_convertor import raw_convertor_filtered
from raw_convertor import raw_convertor_peak 
from femb_position import femb_position
from apa_mapping import APA_MAP
from fft_chn import chn_rfft_psd
from fpga_dac_fit import fpga_dac_fit
from asic_dac_fit import asic_dac_fit
from highpass_filter import hp_flt_applied
from highpass_filter import hp_FIR_applied

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

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

    runpath = rootpath + "/" + runno + "/" 
    for root, dirs, files in os.walk(runpath):
        break

    steppath = None
    for onedir in dirs:
        wibpos = onedir.find("WIB")
        if ( wibpos >= 0 ):
            if ( int(onedir[wibpos+3:wibpos+5]) == wibno ) and (onedir.find(stepno) >=0 ) :
                steppath = runpath + onedir + "/"
                break

    files_cs = []
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

    if (len(files_cs) == 0):
        print "there isn't any data related to your request, exit anyway"
        exit()
    return files_cs

#ana_mode = "CHN"
#ana_mode = "APA"
def read_rawdata(rootpath, runno = "run01rms", wibno=0,  fembno=0, chnno=0, gain="250", tp="20", jumbo_flag=False ):
    files = generate_rawpaths(rootpath, runno, wibno,  fembno, chnno, gain, tp ) 
    datas = []
    for onefile in files:
        with open(onefile, 'rb') as f:
            raw_data = f.read()
            filelength = len(raw_data )
            smps = (filelength-1024)/2/16 
            if smps > 200000:
                smps = 200000

            data, feed_loc, chn_peakp, chn_peakn = raw_convertor_peak(raw_data, smps, jumbo_flag)
            ###############0         1      2       3       4     5    6    7      8           9         10#########
            datas.append([onefile, runno, wibno,  fembno, chnno, gain, tp, data, feed_loc, chn_peakp, chn_peakn])
    return datas

def noise_a_chn(rmsdata, chnno, fft_en = True, fft_s=2000, fft_avg_cycle=50 ):
    asicchn = chnno % 16

    chnrmsdata = rmsdata[0][7][asicchn]
    feed_loc = rmsdata[0][8]
#   raw data
    len_chnrmsdata = len(chnrmsdata)
    rms =  np.std(chnrmsdata[0:100000])
    ped = np.mean(chnrmsdata[0:100000])
    data_slice = chnrmsdata[feed_loc[0]:feed_loc[1]]
    data_100us_slice = chnrmsdata[0:100000:200]
    if (fft_en):
        f,p = chn_rfft_psd(chnrmsdata,  fft_s = fft_s, avg_cycle = fft_avg_cycle)
    else:
        f = None
        p = None

#   data after highpass filter
    flt_chn_data = hp_flt_applied(chnrmsdata, fs = 2000000, passfreq = 1000, flt_order = 3)
    flt_chn_data = np.array(flt_chn_data) +  ped 
    hfped = ped
    hfrms = np.std(flt_chn_data)
    if (fft_en):
        hff,hfp = chn_rfft_psd(flt_chn_data, fft_s = fft_s, avg_cycle = fft_avg_cycle)
    else:
        hff = None
        hfp = None
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
                       rms,   ped,   data_slice,   data_100us_slice,   f,   p,
                       hfrms, hfped, hfdata_slice, hfdata_100us_slice, hff, hfp,
                       sfrms, sfped, unstk_ratio  ]
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

def fit_plot(ax, x, y, ped, fit_paras, fit_type = "peak" ):
    if (fit_paras!= None):
        slope, constant, peakinl, error_gain = fit_paras
        if error_gain == False and slope != 0 :
            ax.set_xlabel("Charge /fC")

            if fit_type == "Peak":
                label = "Gain = %d (e-/LSB)"%(6250/slope)  + "\n" + "INL = %.3f%%"%(peakinl*100)
                ax.set_ylabel("ADC code / LSB")
                y_plot = np.linspace(0,4096)
                if (min(np.abs(y) ) - ped ) > 0:  #positive pulse
                    ax.set_xlim([0,(max(x)//10+1)*10])
                    ax.plot( (y_plot-constant)/slope, y_plot, color = 'b')
                else: #negative pulse
                    ax.set_xlim([(max(x)//10+1)*10*(-1), 0])
                    x = (-1) * x
                    ax.plot( (constant-y_plot)/slope, y_plot, color = 'b')
                ax.scatter([0], [ped], marker="s", color = 'k') #pedestal
                ax.scatter(x, y, marker="o", color = 'r', label=label)
            elif fit_type == "Area":
                label = "Gain = %d (e-/(LSB)*(6$\mu$s))"%(6250/slope)  + "\n" + "INL = %.3f%%"%(peakinl*100)
                if max(np.abs(y) ) == max(y) : 
                    ax.set_xlim([0,(max(x)//10+1)*10])
                    y_plot =  np.linspace(0, (max(y)//100 + 1)*100 )
                    ax.plot( (y_plot-constant)/slope, y_plot, color = 'b')
                else:
                    ax.set_xlim([(max(x)//10+1)*10*(-1), 0])
                    y_plot =  np.linspace((min(y)//100 - 1)*100, 0 )
                    x = (-1) * x
                    ax.plot( (constant-y_plot)/slope, y_plot, color = 'b')
                ax.set_ylabel("Area / (LSB)*(6$\mu$s)")
                ax.scatter([0], [0], marker="s", color = 'k')
                ax.scatter(x, y, marker="o", color = 'r', label = label)
 
            ax.legend(loc='best')
            ax.set_title("Linear Fit (%s)"%fit_type)
            ax.grid()

def cali_linear_fitplot(apainfo, wireinfo, feset_info, chn_cali_paras, ploten=True):
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

    if (ploten):
        fig = plt.figure(figsize=(16,9))
        ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
        ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
        ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

        fit_plot(ax1, fc_dacs, ampps , ped, ampp_fit , fit_type = "Peak" )
        fit_plot(ax2, fc_dacs, ampns , ped, ampn_fit , fit_type = "Peak" )
        fit_plot(ax3, fc_dacs, areaps, ped, areap_fit, fit_type = "Area" )
        fit_plot(ax4, fc_dacs, areans, ped, arean_fit, fit_type = "Area" )

        apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
        wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
        fe_gain = int(feset_info[0])/10.0
        fe_tp = int(feset_info[1])/10.0
        feset_str = " ; Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s"%(fe_gain, fe_tp)
        fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 20)
        plt.tight_layout( rect=[0, 0.05, 1, 0.95])

        plt.show()
        plt.close()

    if (ampp_fit != None):
        encperlsb = int(6250/ampp_fit[0])
        chninl    = ampp_fit[2]
    else:
        encperlsb = None
        chninl    = None

    return  encperlsb,chninl

def cali_wf_subplot(ax, chn_cali_paras, t=100, pulse = "positive", avg_fg = False ):
    N = int(t/0.5)
    x = np.arange(N) * 0.5
    for onecp in chn_cali_paras:
        if pulse == "positive" :
            pos = onecp[8]
        else:
            pos = onecp[9]
        if pos >= (N//2):
            spos= pos-(N//2)
        else:
            spos= 0
        if (avg_fg):
            y = onecp[7][spos:spos+N]
            ax.set_title("Waveforms after averaging" )
        else:
            y = onecp[6][spos:spos+N]
            ax.set_title("Waveforms" )
        ax.scatter(x, y)
        ax.plot(x, y)
    ax.set_xlim([0,t])
    ax.set_ylim([0,4200])
    ax.grid()
    ax.set_ylabel("ADC output / LSB")
    ax.set_xlabel("t / $\mu$s")

def cali_wf_plot(apainfo, wireinfo, feset_info, chn_cali_paras):
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    t = 20
    cali_wf_subplot(ax1, chn_cali_paras, t=t, pulse="positive", avg_fg = False )
    cali_wf_subplot(ax2, chn_cali_paras, t=t, pulse="positive", avg_fg = True )
    cali_wf_subplot(ax3, chn_cali_paras, t=t, pulse="negative", avg_fg = False )
    cali_wf_subplot(ax4, chn_cali_paras, t=t, pulse="negative", avg_fg = True )

    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
    fe_gain = int(feset_info[0])/10.0
    fe_tp = int(feset_info[1])/10.0
    feset_str = " ; Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s"%(fe_gain, fe_tp)
    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 20)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
 
    plt.show()
    plt.close()

def ped_wf_subplot(ax, data_slice, ped, rms,  t_rate=0.5, title="Waveforms of raw data", label="Waveform" ):
    N = len(data_slice)
    x = np.arange(N) * t_rate
    y = data_slice
    ax.scatter(x, y, marker='.', color ='r', label=label)
    ax.plot(x, y, color ='b')
   
    ax.set_title(title )
    ax.set_xlim([0,int(N*t_rate)])
    ax.set_ylim([ped-5*(int(rms+1)),ped+5*(int(rms+1))])
    ax.grid()
    ax.set_ylabel("ADC output / LSB")
    ax.set_xlabel("t / $\mu$s")
    ax.legend(loc='best')

def ped_hg_subplot(ax, data_slice, ped, rms, title="Histogram of raw data", label="Waveform" ):
    N = len(data_slice)
    sigma3 = int(rms+1)*3
    ax.grid()
    ax.hist(data_slice, normed=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label=label, color='b', rwidth=0.9 )

    gaussian_x = np.linspace(ped - 3*rms, ped + 3*rms, 100)
    gaussian_y = mlab.normpdf(gaussian_x, ped, rms)
    ax.plot(gaussian_x, gaussian_y, color='r')

    ax.set_title(title + "(%d samples)"%N )
    ax.set_xlabel("ADC output / LSB")
    ax.set_ylabel("Normalized counts")
    ax.legend(loc='best')


def ped_wf_plot(apainfo, wireinfo, feset_info, chn_noise_paras):
    rms =  chn_noise_paras[1]
    ped =  chn_noise_paras[2]
    data_slice = chn_noise_paras[3]
    data_100us_slice = chn_noise_paras[4]

    hfrms =  chn_noise_paras[7]
    hfped =  chn_noise_paras[8]
    hfdata_slice = chn_noise_paras[9]
    hfdata_100us_slice = chn_noise_paras[10]

    sfrms =  chn_noise_paras[13]
    sfped =  chn_noise_paras[14]
    unstk_ratio  =  chn_noise_paras[15]

    label = "Rawdata: mean = %d, rms = %2.3f" % (int(ped), rms) + "\n" + \
            "Stuck Free: mean = %d, rms = %2.3f, unstuck=%%%d" % (int(sfped), sfrms, int(unstk_ratio*100) )

    hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 

#waveform
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
    ped_wf_subplot(ax1, data_slice,         ped,   rms,    t_rate=0.5, title="Waveforms of raw data", label=label )
    ped_wf_subplot(ax2, hfdata_slice,       hfped, hfrms,  t_rate=0.5, title="Waveforms of data after HPF", label=hflabel )
    ped_wf_subplot(ax3, data_100us_slice,   ped,   rms,    t_rate=100, title="Waveforms of raw data", label=label )
    ped_wf_subplot(ax4, hfdata_100us_slice, hfped, hfrms,  t_rate=100, title="Waveforms of data after HPF", label=hflabel )


    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
    fe_gain = int(feset_info[0])/10.0
    fe_tp = int(feset_info[1])/10.0
    feset_str = " ; Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s"%(fe_gain, fe_tp)
    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 20)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
 
    plt.show()
    plt.close()

#histogram
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=4)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=4)
#    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
#    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
    ped_hg_subplot(ax1, data_100us_slice, ped, rms, title="Histogram of raw data", label=label )
    ped_hg_subplot(ax2, hfdata_100us_slice, hfped, hfrms, title="Histogram of data after HPF", label=hflabel )
#    ped_hg_subplot(ax3, data_100us_slice, ped, rms, title="Histogram of raw data", label=label )
#    ped_hg_subplot(ax4, hfdata_100us_slice, hfped, hfrms, title="Histogram of data after HPF", label=hflabel )
 
    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
    fe_gain = int(feset_info[0])/10.0
    fe_tp = int(feset_info[1])/10.0
    feset_str = " ; Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s"%(fe_gain, fe_tp)
    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 20)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
 
    plt.show()
    plt.close()

def ped_fft_subplot(ax, f, p, maxx=1000000,  title="FFT specturm", label="FFT" ):
    ax.set_title(title )
    ax.plot(np.array(f)/1000.0,p,color='r', label=label)
    ax.set_xlim([0,maxx/1000])
    ax.set_xlabel("Frequency /kHz")
    ax.grid()
    psd=True
    if (psd == True):
        ax.set_ylabel("Power Spectral Desity /dB")
        ax.set_ylim([-80,20])
    else:
        ax.set_ylabel("Amplitude /dB")
        ax.set_ylim([-40,20])
    ax.legend(loc='best')

def ped_fft_plot(apainfo, wireinfo, feset_info, chn_noise_paras):
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    rms =  chn_noise_paras[1]
    ped =  chn_noise_paras[2]
    f = chn_noise_paras[5]
    p = chn_noise_paras[6]

    hfrms =  chn_noise_paras[7]
    hfped =  chn_noise_paras[8]
    hff = chn_noise_paras[11]
    hfp = chn_noise_paras[12]

    sfrms =  chn_noise_paras[13]
    sfped =  chn_noise_paras[14]
    unstk_ratio  =  chn_noise_paras[15]

    label = "Rawdata: mean = %d, rms = %2.3f" % (int(ped), rms) + "\n" + \
            "Stuck Free: mean = %d, rms = %2.3f, unstuck=%%%d" % (int(sfped), sfrms, int(unstk_ratio*100) )

    hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 
 
    ped_fft_subplot(ax1, f, p, maxx=1000000, title="Spectrum of raw data", label=label )
    ped_fft_subplot(ax2, hff, hfp, maxx=1000000, title="Spectrum of data after HPF", label=hflabel )
    ped_fft_subplot(ax3, f, p, maxx=100000, title="Spectrum of raw data", label=label )
    ped_fft_subplot(ax4, hff, hfp, maxx=100000, title="Spectrum of data after HPF", label=hflabel )
  
    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
    fe_gain = int(feset_info[0])/10.0
    fe_tp = int(feset_info[1])/10.0
    feset_str = " ; Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s"%(fe_gain, fe_tp)
    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 20)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
 
    plt.show()
    plt.close()

def cali_a_chn(calidata, chnno, cap=1.85E-13 ):
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
#        ped_data = []
#        for loci in range(avg_cycles-1):
#            ped_data = ped_data + chncalidata[ (feed_loc[loci]+feed_ivl//2) : (feed_loc[loci+1]) ]
        for loci in range(avg_cycles - 1):
            avg_data_slice = avg_data_slice +  np.array(chncalidata[feed_loc[loci+1]:feed_loc[loci+2]])
        avg_data_slice = avg_data_slice / (avg_cycles*1.0)
        dactype = sonecali[0]
        vdac = sonecali[1]
        fc_daclsb = sonecali[3]
        pp_loc = np.where (avg_data_slice == max(avg_data_slice))[0][0]
        np_loc = np.where (avg_data_slice == min(avg_data_slice))[0][0]
        ped    = np.mean (avg_data_slice[feed_ivl//2: feed_ivl])
#        rms    = np.std (ped_data)
        pp_area = np.sum (avg_data_slice[pp_loc-6:pp_loc+6]-ped)
        np_area = np.sum (avg_data_slice[np_loc-6:np_loc+6]-ped)
                               # 0   ,  1     ,  2,   3,      4,       5,           6,            7,         8,     9,     10,     11 ,    12   
        chn_cali_paras.append( [chnno, dactype, vdac, fc_daclsb, ppeak, npeak, data_slice, avg_data_slice, pp_loc, np_loc, ped, pp_area, np_area]  )
    return chn_cali_paras

def ana_a_chn(rootpath, mode="CHN", APAno = 4, \
               rmsrunno = "run01rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, chnno=0, gain="250", tp="20", \
               jumbo_flag=False, fft_s=5000 ):
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
    rmsdata = read_rawdata(rootpath, rmsrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    chn_noise_paras = noise_a_chn(rmsdata, chnno,fft_en = True, fft_s=fft_s, fft_avg_cycle=50)
    ped_wf_plot(apainfo, wireinfo, feset_info, chn_noise_paras)
    ped_fft_plot(apainfo, wireinfo, feset_info, chn_noise_paras)

    calidata = read_rawdata(rootpath, calirunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    chn_cali_paras = cali_a_chn(calidata, chnno )
    cali_linear_fitplot(apainfo, wireinfo, feset_info, chn_cali_paras)
    cali_wf_plot(apainfo, wireinfo, feset_info, chn_cali_paras)

def ana_a_asic(rootpath, APAno = 4, \
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

    rmsdata  = read_rawdata(rootpath, rmsrunno,  wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)
    calidata = read_rawdata(rootpath, calirunno, wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

    asic_gains =[]
    for chni in range(16):
        chnno = chni + 16*asicno
        wireinfo = None
        for onewire in All_sort:
            if (int(onewire[1]) == chnno):
                wireinfo = onewire
                break
        
        chn_noise_paras = noise_a_chn(rmsdata, chnno, fft_en = True)
        rms          =  chn_noise_paras[1]
        ped          =  chn_noise_paras[2]
        hfrms        =  chn_noise_paras[7]
        hfped        =  chn_noise_paras[8]
        sfrms        =  chn_noise_paras[13]
        sfped        =  chn_noise_paras[14]
        unstk_ratio  =  chn_noise_paras[15]

        chn_cali_paras = cali_a_chn(calidata, chnno )
        encperlsb, chninl = cali_linear_fitplot(apainfo, wireinfo, feset_info, chn_cali_paras, ploten=False)
        asic_gains.append([rms ,ped ,hfrms ,hfped ,sfrms ,sfped  ,unstk_ratio , encperlsb, chninl])



rootpath = "/Users/shanshangao/Documents/data/Rawdata_03_21_2018/" 
#ana_a_chn(rootpath,  APAno = 4, \
#               rmsrunno = "run02rms", calirunno = "run01fpg",
#               wibno=0,  fembno=0, chnno=15, gain="250", tp="30", \
#               jumbo_flag=False,fft_s=5000  )
from timeit import default_timer as timer
s0 = timer()
ana_a_asic(rootpath, APAno = 4, \
               rmsrunno = "run02rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, asicno=0, gain="250", tp="30", \
               jumbo_flag=False  )

print timer() - s0
s0= timer()
ana_a_asic(rootpath, APAno = 4, \
               rmsrunno = "run02rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, asicno=1, gain="250", tp="30", \
               jumbo_flag=False  )

print timer() - s0
s0= timer()
ana_a_asic(rootpath, APAno = 4, \
               rmsrunno = "run02rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, asicno=2, gain="250", tp="30", \
               jumbo_flag=False  )

print timer() - s0
s0= timer()
ana_a_asic(rootpath, APAno = 4, \
               rmsrunno = "run02rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, asicno=3, gain="250", tp="30", \
               jumbo_flag=False  )


print timer() - s0


#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=0, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=1, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=2, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=3, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=4, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=5, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=6, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#s0= timer()
#
#ana_a_asic(rootpath, APAno = 4, calirunno = "run01fpg", wibno=0,  fembno=0, asicno=7, gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#   
    
