# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sat Mar 24 23:23:49 2018
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
from femb_position import femb_position
from apa_mapping import APA_MAP

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

from chn_analysis  import read_rawdata 
from chn_analysis  import noise_a_chn 
from chn_analysis  import cali_a_chn 
from chn_analysis  import linear_fit 


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

def ana_a_chn(rms_rootpath,  cali_rootpath, mode="CHN", APAno = 4, \
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
    rmsdata = read_rawdata(rms_rootpath, rmsrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    chn_noise_paras = noise_a_chn(rmsdata, chnno,fft_en = True, fft_s=fft_s, fft_avg_cycle=50)
    ped_wf_plot(apainfo, wireinfo, feset_info, chn_noise_paras)
    ped_fft_plot(apainfo, wireinfo, feset_info, chn_noise_paras)

    calidata = read_rawdata(cali_rootpath, calirunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
    chn_cali_paras = cali_a_chn(calidata, chnno )
    cali_wf_plot(apainfo, wireinfo, feset_info, chn_cali_paras)
    cali_linear_fitplot(apainfo, wireinfo, feset_info, chn_cali_paras)

rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/run01fpg/"
cali_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/run01fpg/"
#rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
#cali_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
from timeit import default_timer as timer
s0= timer()
print s0
ana_a_chn(rms_rootpath, cali_rootpath, APAno = 4, \
               rmsrunno = "run02rms", calirunno = "run01fpg",
               wibno=0,  fembno=0, chnno=0, gain="250", tp="30", \
               jumbo_flag=False,fft_s=5000  )
print timer() - s0





#ana_a_apa(rms_rootpath, cali_rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg",  gain="250", tp="05", jumbo_flag=False )


#ana_a_wib(rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg", wibno=0,  gain="250", tp="05", jumbo_flag=False )
#a = chk_a_apa (rootpath, APAno = 4, \
#           rmsrunno = "run02rms", calirunno = "run01fpg",\
#           gain="250", tp="05" ,\
#           jumbo_flag=False )
#print a


#ana_a_apa(rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg",  gain="250", tp="05", jumbo_flag=False )
#print timer() - s0
#print timer() - s0
#ana_a_apa(rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg",  gain="250", tp="10", jumbo_flag=False )
#print timer() - s0
#ana_a_apa(rootpath, APAno = 4, rmsrunno = "run02rms", calirunno = "run01fpg",  gain="250", tp="20", jumbo_flag=False )
#print timer() - s0


# 
#s0= timer()
#print s0
#ana_a_femb(rootpath, APAno = 4, \
#               rmsrunno = "run02rms", calirunno = "run01fpg",
#               wibno=0,  fembno=0,  gain="250", tp="05" ,\
#               jumbo_flag=False )
#print timer() - s0
#
#def a(s0):
#    ana_a_asic(rootpath, APAno = 4, \
#                   rmsrunno = "run02rms", calirunno = "run01fpg",
#                   wibno=0,  fembno=0, asicno=0, gain="250", tp="30", \
#                   jumbo_flag=False  )
#    
#    print str(timer() - s0) + "a"
#
#def b(s0):
#    ana_a_asic(rootpath, APAno = 4, \
#                   rmsrunno = "run02rms", calirunno = "run01fpg",
#                   wibno=0,  fembno=0, asicno=1, gain="250", tp="30", \
#                   jumbo_flag=False  )
#    
#    print timer() - s0
#
#from multiprocessing import Process
#
#s0= timer()
#if __name__ == '__main__':
#    a(s0)
#    p = Process(target=b, args=(s0, ))
#    p2 = Process(target=a, args=(s0, ))
#    p.start()
#    p2.start()
#    p.join()
#    p2.join()


#s0= timer()
#ana_a_asic(rootpath, APAno = 4, \
#               rmsrunno = "run02rms", calirunno = "run01fpg",
#               wibno=0,  fembno=0, asicno=2, gain="250", tp="30", \
#               jumbo_flag=False  )
#
#print timer() - s0
#s0= timer()
#ana_a_asic(rootpath, APAno = 4, \
#               rmsrunno = "run02rms", calirunno = "run01fpg",
#               wibno=0,  fembno=0, asicno=3, gain="250", tp="30", \
#               jumbo_flag=False  )
#
#
#print timer() - s0


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
    
