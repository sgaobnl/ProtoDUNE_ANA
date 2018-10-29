# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Mon Oct 29 16:26:09 2018
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
from femb_position import femb_position
from apa_mapping   import APA_MAP
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
from matplotlib.backends.backend_pdf import PdfPages
from chn_analysis  import read_rawdata 
from chn_analysis  import read_rawdata_coh 
from chn_analysis  import noise_a_chn 
from chn_analysis  import noise_a_coh 
from fft_chn import chn_rfft_psd
from chn_analysis  import coh_noise_ana


def wf_a_asic(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  fembno=0, asicno=0, gain="250", tp="05" ,\
               jumbo_flag=False, apa= "ProtoDUNE" ):
    femb_pos_np = femb_position (APAno)
    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 
    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    feset_info = [gain, tp]
    apa_map = APA_MAP()
    apa_map.APA = apa
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping()

    rmsdata  = read_rawdata_coh(rms_rootpath, rmsrunno,  wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

    asic_results =[]
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
        raw_data     =   chn_noise_paras[3]
        r100us_data     =   chn_noise_paras[4]
        fft_f        =   chn_noise_paras[5]
        fft_p        =   chn_noise_paras[6]
        fft_fl       =   chn_noise_paras[16]
        fft_pl       =   chn_noise_paras[17]
        print [apainfo, APAno, wibno, fembno, asicno, chni, wireinfo]
                             #0         1        2     3       4      5    6    7     8      9     10      11      12           13        14           15     16     17      18 
        asic_results.append([apainfo, APAno, wibno, fembno, asicno, chni, rms ,ped ,hfrms ,hfped ,sfrms ,sfped  ,unstk_ratio, raw_data, r100us_data, fft_f, fft_p, fft_fl, fft_pl, wireinfo])
    return asic_results


def wfcoh_a_asic(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = 4, \
               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi",\
               wibno=0,  fembno=0, asicno=0, gain="250", tp="05" ,\
               jumbo_flag=False, apa= "ProtoDUNE" ):
    femb_pos_np = femb_position (APAno)
    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 
    apainfo = None
    for femb_pos in femb_pos_np:
        if femb_pos[1] == wibfemb:
            apainfo = femb_pos
            break

    feset_info = [gain, tp]
    apa_map = APA_MAP()
    apa_map.APA = apa
    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping()

    rmsdata  = read_rawdata_coh(rms_rootpath, rmsrunno,  wibno,  fembno, 16*asicno, gain, tp, jumbo_flag)

    asic_results =[]
    for chni in range(16):
        chnno = chni + 16*asicno
        wireinfo = None
        for onewire in All_sort:
            if (int(onewire[1]) == chnno):
                wireinfo = onewire
                break
        wiretype = wireinfo[0][0]
        print [APAno, wibno, fembno, asicno, chni, wireinfo]
 
        rpath = "/nfs/home/shanshan/coh_study/"
        rpath = "./"
        t_pat = "Test035"
        pre_ana = t_pat + "_ProtoDUNE_CE_characterization_summary" + ".csv"
        ppath = rpath + pre_ana 
        ccs = []
        with open(ppath, 'r') as fp:
            for cl in fp:
                tmp = cl.split(",")
                x = []
                for i in tmp:
                    x.append(i.replace(" ", ""))
                x = x[:-1]
                ccs.append(x)
        ccs_title = ccs[0]
        ccs = ccs[1:]

        asic_ccs = []
        for ci in ccs:
            if (APAno == int(ci[0][1])) and ( int(ci[3]) == wibno )and ( int(ci[4]) == fembno )and ( int(ci[5]) == asicno ):
                asic_ccs.append(ci)

        cohdata ,cohdata_flg = coh_noise_ana(asic_ccs, rmsdata, wiretype = wiretype)

        chn_noise_paras = noise_a_coh(cohdata, cohdata_flg, rmsdata, chnno =chni, fft_en = True, fft_s=2000, fft_avg_cycle=50, wibno=wibno,  fembno=fembno )


        fig = plt.figure(figsize=(32,18))
        axu = []
        axm = []
        axd = []
        axu.append( plt.subplot2grid((3, 3), (0, 0), colspan=3, rowspan=1)) 
        axm.append( plt.subplot2grid((3, 3), (1, 0), colspan=3, rowspan=1)) 
        axd.append( plt.subplot2grid((3, 3), (2, 0), colspan=3, rowspan=1)) 
 
#        chn_noise_paras = w_results[chni]
#        wireinfo =  wireinfo[0][0]

        rms =  chn_noise_paras[1]
        ped =  chn_noise_paras[2]
        cohrms =  chn_noise_paras[14]
        cohped =  chn_noise_paras[15]
        postrms =  chn_noise_paras[7]
        postped =  chn_noise_paras[8]

        rawdata = chn_noise_paras[3]
        postdata = chn_noise_paras[9]


        label = wireinfo[0] + "_ASIC" + str(wireinfo[2]) + "_CHN" + wireinfo[3]  
        ped_wf_subplot(axu[0], rawdata[0:1000],  ped,     rms,     t_rate=0.5, title="Waveforms of raw data (2MSPS)", label=label )
        ped_wf_subplot(axm[0], cohdata[0:1000],  cohped,  cohrms , t_rate=0.5, title="Waveforms of coherent noise (2MSPS)", label=label )
        ped_wf_subplot(axd[0], postdata[0:1000], postped, postrms, t_rate=0.5, title="Waveforms of post-filter data (2MSPS)", label=label )


        fig_title = apainfo[0] + "_" + apainfo[1] + "_FE%d_%s"%(wireinfo[2], wiretype)
        plt.tight_layout( rect=[0, 0.05, 1, 0.95])
        fig.suptitle(fig_title, fontsize = 20)
        plt.savefig(out_path + fig_title + "_coh_wf_%s.png"%label, format='png')
        plt.close()
       
    return asic_results



def ped_wf_subplot(ax, data_slice, ped, rms,  t_rate=0.5, title="Waveforms of raw data", label="Waveform" ):
    N = len(data_slice)
    x = np.arange(N) * t_rate
    y = data_slice
    ax.scatter(x, y, marker='.', color ='r', label=label + "\n" + "mean = %d, rms = %2.3f" % (int(ped), rms))
    ax.plot(x, y, color ='b')
   
    ax.set_title(title )
    ax.set_xlim([0,int(N*t_rate)])
#    ax.set_ylim([ped-5*(int(rms+1)),ped+5*(int(rms+1))])
    ax.grid()
    ax.set_ylabel("ADC output / LSB")
    ax.set_xlabel("t / $\mu$s")
    ax.legend(loc=1)

def asic_wf_plot_wire(out_path, asic_results, wiretype = "U"):
    fig = plt.figure(figsize=(32,18))
    axl = []
    axr = []
    for i in range(7):
        axl.append( plt.subplot2grid((7, 2), (i, 0), colspan=1, rowspan=1)) 
        axr.append( plt.subplot2grid((7, 2), (i, 1), colspan=1, rowspan=1)) 
    wi = 0
    for chni in range(16):
        chn_noise_paras = asic_results[chni]
        wireinfo =  chn_noise_paras[19]
        APAno =  chn_noise_paras[1]
        if (wireinfo[0][0] == wiretype):
            rms =  chn_noise_paras[6]
            ped =  chn_noise_paras[7]
            data_slice = chn_noise_paras[13]
            data_100us_slice = chn_noise_paras[14]
            if ( wi == 0):
                avg_data = np.array(data_slice)
                avg_data_100us_slice = np.array(chn_noise_paras[14])
            else:
                avg_data = avg_data + np.array(data_slice)
                avg_data_100us_slice =avg_data_100us_slice +np.array( chn_noise_paras[14])
            
            apainfo =  chn_noise_paras[0]
            hfrms =  chn_noise_paras[7]
            hfped =  chn_noise_paras[8]
            hfdata_slice = chn_noise_paras[9]
            hfdata_100us_slice = chn_noise_paras[10]
            hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 
            sfrms =  chn_noise_paras[10]
            sfped =  chn_noise_paras[11]
            unstk_ratio  =  chn_noise_paras[12]
            label = wireinfo[0] + ", ASIC" + str(wireinfo[2]) + ", CHN" + wireinfo[3]  

            ped_wf_subplot(axl[wi], data_slice[0:2000],         ped,   rms,    t_rate=0.5, title="Waveforms of raw data (2MSPS)", label=label )
            ped_wf_subplot(axr[wi], data_100us_slice,   ped,   rms,    t_rate=100, title="Waveforms of raw data (10kSPS)", label=label )
            wi = wi + 1
    avg_data = avg_data*1.0/wi
    avg_data_100us_slice = avg_data_100us_slice*1.0/wi
    avgped = np.mean(avg_data)
    avgrms = np.std(avg_data)
    avgped100us = np.mean(avg_data_100us_slice)
    avgrms100us = np.std(avg_data_100us_slice)
 
    label = "mean = %d, rms = %2.3f" % (int(avgped), avgrms) 
    ped_wf_subplot(axl[6], avg_data[0:2000],         avgped,   avgrms,    t_rate=0.5, title="Averaging waveforms of %s wires of a FE ASIC(2MSPS)"%wiretype, label=label )
    ped_wf_subplot(axr[6], avg_data_100us_slice,   avgped100us,   avgrms100us,    t_rate=100, title="Averaging waveforms  %s wires of a FE ASIC(2MSPS)"%wiretype, label=label )
 
    fig_title = apainfo[0] + "_" + apainfo[1] + "_FE%d_%s"%(wireinfo[2], wiretype)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    fig.suptitle(fig_title, fontsize = 20)
    plt.savefig(out_path+ fig_title + ".png", format='png')
    plt.close()


def asic_coh_plot_wire(out_path, asic_results, wiretype = "U"):
    w_results = []
    wi = 0
    for chni in range(16):
        chn_noise_paras = asic_results[chni]
        wireinfo =  chn_noise_paras[19]
        APAno =  chn_noise_paras[1]
        unstk_ratio  =  chn_noise_paras[12]
        if (wireinfo[0][0] in  wiretype) and (unstk_ratio > 0.9) :
            data_slice = chn_noise_paras[13]
            if ( wi == 0):
                avg_data = np.array(data_slice)
            else:
                avg_data = avg_data + np.array(data_slice)
            wi = wi + 1
            w_results.append(asic_results[chni])
 
    coh_data = (avg_data*1.0/wi) 
    coh_data = coh_data - np.mean( coh_data)

    for chni in range(len(w_results)):
        fig = plt.figure(figsize=(32,18))
        axu = []
        axm = []
        axd = []
        for i in range(3):
            axu.append( plt.subplot2grid((3, 3), (0, i), colspan=1, rowspan=1)) 
            axm.append( plt.subplot2grid((3, 3), (1, i), colspan=1, rowspan=1)) 
            axd.append( plt.subplot2grid((3, 3), (2, i), colspan=1, rowspan=1)) 
 
        chn_noise_paras = w_results[chni]
        wireinfo =  chn_noise_paras[19]
        APAno =  chn_noise_paras[1]
        rms =  chn_noise_paras[6]
        ped =  chn_noise_paras[7]
        rawdata = chn_noise_paras[13]
        unstk_ratio  =  chn_noise_paras[12]
        pos_data = np.array (rawdata) - coh_data
        pos_ped = np.mean(pos_data[0:100000])
        pos_rms = np.std(pos_data[0:100000])
        apainfo =  chn_noise_paras[0]
        label = wireinfo[0] + "_ASIC" + str(wireinfo[2]) + "_CHN" + wireinfo[3]  
        ped_wf_subplot(axu[0], rawdata[0:1000],    ped,   rms,    t_rate=0.5, title="Waveforms of raw data (2MSPS)", label=label )
        ped_wf_subplot(axm[0], coh_data[0:1000],   np.mean(coh_data), np.std(coh_data)  ,    t_rate=0.5, title="Waveforms of coherent noise (2MSPS)", label=label )
        ped_wf_subplot(axd[0], pos_data[0:1000],   pos_ped,   pos_rms,    t_rate=0.5, title="Waveforms of post-filter data (2MSPS)", label=label )

        rf_l, rp_l = chn_rfft_psd(rawdata, fft_s = len(rawdata), avg_cycle = 1)
        cf_l, cp_l = chn_rfft_psd(coh_data, fft_s = len(coh_data), avg_cycle = 1)
        pf_l, pp_l = chn_rfft_psd(pos_data, fft_s = len(pos_data), avg_cycle = 1)

#        ped_wf_subplot(axu[1], rawdata[::200],    ped,   rms,    t_rate=100, title="Waveforms of raw data (10kSPS)", label=label )
#        ped_wf_subplot(axm[1], coh_data[::200],   np.mean(coh_data), np.std(coh_data)  ,    t_rate=100, title="Waveforms of coherent noise (10kSPS)", label=label )
#        ped_wf_subplot(axd[1], pos_data[::200],   pos_ped,   pos_rms,    t_rate=100, title="Waveforms of post-filter data (10kSPS)", label=label )
 
        ped_fft_subplot(axu[1], rf_l, rp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
        ped_fft_subplot(axm[1], cf_l, cp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
        ped_fft_subplot(axd[1], pf_l, pp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )

        ped_fft_subplot(axu[2], rf_l, rp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
        ped_fft_subplot(axm[2], cf_l, cp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
        ped_fft_subplot(axd[2], pf_l, pp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )

        fig_title = apainfo[0] + "_" + apainfo[1] + "_FE%d_%s"%(wireinfo[2], wiretype)
        plt.tight_layout( rect=[0, 0.05, 1, 0.95])
        fig.suptitle(fig_title, fontsize = 20)
        plt.savefig(out_path + fig_title + "_coh_%s.png"%label, format='png')
        plt.close()


def ped_fft_subplot(ax, f, p, maxx=1000000,  title="FFT specturm", label="FFT", peaks_note = False ):
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


def asic_fft_plot_wire(out_path, asic_results, wiretype = "U"):
    fig = plt.figure(figsize=(32,18))
    axl = []
    axm = []
    axr = []
    for i in range(7):
        axl.append( plt.subplot2grid((7, 3), (i, 0), colspan=1, rowspan=1)) 
        axm.append( plt.subplot2grid((7, 3), (i, 1), colspan=1, rowspan=1)) 
        axr.append( plt.subplot2grid((7, 3), (i, 2), colspan=1, rowspan=1)) 
    wi = 0
    for chni in range(16):
        chn_noise_paras = asic_results[chni]
        wireinfo =  chn_noise_paras[19]
        APAno =  chn_noise_paras[1]
        if (wireinfo[0][0] == wiretype):
            rms =  chn_noise_paras[6]
            ped =  chn_noise_paras[7]
            f = chn_noise_paras[15]
            p = chn_noise_paras[16]
            fl = chn_noise_paras[17]
            pl = chn_noise_paras[18]
            if ( wi == 0):
                avg_f = np.array(f)
                avg_p = np.array(p)
                avg_fl = np.array(fl)
                avg_pl = np.array(pl)
            else:
                avg_p  = avg_p  + np.array(p)
                avg_pl = avg_pl + np.array(pl)
 
            apainfo =  chn_noise_paras[0]
            label = wireinfo[0] + ", ASIC" + str(wireinfo[2]) + ", CHN" + wireinfo[3]  
            ped_fft_subplot(axl[wi], f, p, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
            ped_fft_subplot(axm[wi], fl, pl, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
            ped_fft_subplot(axr[wi], fl, pl, maxx=1000,  title="FFT specturm", label=label, peaks_note = False )
            wi = wi + 1

 
    label = wiretype + "_ASIC" + str(wireinfo[2])   
    ped_fft_subplot(axl[6], avg_f, avg_p*1.0/wi, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
    ped_fft_subplot(axm[6], avg_fl,avg_pl*1.0/wi, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
    ped_fft_subplot(axr[6], avg_fl,avg_pl*1.0/wi, maxx=1000,  title="FFT specturm", label=label, peaks_note = False )

    fig_title = apainfo[0] + "_" + apainfo[1] + "_FE%d_%s"%(wireinfo[2], wiretype)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    fig.suptitle(fig_title, fontsize = 20)
    plt.savefig(out_path + fig_title + "FFT.png", format='png')
    plt.close()



def asic_wf_plot(asic_results, wiretype = "U"):
    fig = plt.figure(figsize=(8,28))
    axl = []
    axr = []
    for i in range(7):
        axl.append( plt.subplot2grid((6, 2), (i, 0), colspan=1, rowspan=1)) 
        axr.append( plt.subplot2grid((6, 2), (i, 1), colspan=1, rowspan=1)) 
 
    for chni in range(16):
        chn_noise_paras = asic_results[chni]
        rms =  chn_noise_paras[6]
        ped =  chn_noise_paras[7]
        data_slice = chn_noise_paras[13]
        data_100us_slice = chn_noise_paras[14]
        wireinfo =  chn_noise_paras[19]
        apainfo =  chn_noise_paras[0]

        hfrms =  chn_noise_paras[7]
        hfped =  chn_noise_paras[8]
        hfdata_slice = chn_noise_paras[9]
        hfdata_100us_slice = chn_noise_paras[10]
        hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 

        sfrms =  chn_noise_paras[10]
        sfped =  chn_noise_paras[11]
        unstk_ratio  =  chn_noise_paras[12]

        label = "Rawdata: mean = %d, rms = %2.3f" % (int(ped), rms) + "\n" + \
                "Stuck Free: mean = %d, rms = %2.3f, unstuck=%%%d" % (int(sfped), sfrms, int(unstk_ratio*100) )

        wireinfo_str = "Wire" + wireinfo[0] + "_FEMBCHN" + wireinfo[1] 

        ped_wf_subplot(axl[chni], data_slice,          ped,   rms,    t_rate=0.5, title="Waveforms of raw data (2MSPS)", label=label )
        ped_wf_subplot(axr[chni], data_100us_slice,   ped,   rms,    t_rate=100, title="Waveforms of raw data (10kSPS)", label=label )
        break

    feset_str = "\n Gain = 14 mV/fC, Tp = 2.0 $\mu$s; "
    fig.suptitle(apainfo_str , fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig("./" + apainfo_str + ".png", format='png')
    plt.close()

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
    wibno = int(sys.argv[10] )
    fembno = int(sys.argv[11] )
    asicno = int(sys.argv[12] )

    if (apafolder == "APA40"):
        rms_rootpath =  "D:/APA40/Rawdata/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "D:/APA40/Rawdata/Rawdata_" + fpgdate + "/"
        asic_rootpath = "D:/APA40/Rawdata/Rawdata_" + asidate + "/"
        apa = "APA40"
    elif (apafolder != "APA"):
        rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + rmsdate + "/"
        fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + fpgdate + "/"
        asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + asidate + "/"
        apa = "ProtoDUNE"
    else:
        rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
        fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
        asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
        rms_rootpath =  "/nfs/sw/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
        fpga_rootpath = "/nfs/sw/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
        asic_rootpath = "/nfs/sw/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
        rms_rootpath =  "/Users/shanshangao/Google_Drive_BNL/tmp/pd_tmp/run03rms/"
        fpga_rootpath = "/Users/shanshangao/Google_Drive_BNL/tmp/pd_tmp/run03rms/"
        asic_rootpath = "/Users/shanshangao/Google_Drive_BNL/tmp/pd_tmp/run03rms/"
        apa = "ProtoDUNE"
        rms_rootpath =  "/Users/shanshangao/tmp/Rawdata_08_21_2018/run102dat"
        fpga_rootpath =  "/Users/shanshangao/tmp/Rawdata_08_21_2018/run99fpg"
        asic_rootpath =  "/Users/shanshangao/tmp/Rawdata_08_21_2018/run99asi"
        apa = "LArIAT"

    out_path = rms_rootpath + "/" + "results/" + "Chns_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+"/"
    if (os.path.exists(out_path)):
        pass
    else:
        try: 
            os.makedirs(out_path)
        except OSError:
            print "Can't create a folder, exit"
            exit()


    print "Start..., please wait..."
    print "Result saves at: "
    print out_path 
    gains = ["250", "140"] 
    gains = [ "140"] 
    tps = ["05", "10", "20", "30"]
    tps = [ "20"]

    asic_results = wf_a_asic(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = APAno, \
                  rmsrunno = rmsrunno, fpgarunno = fpgarunno, asicrunno = asicrunno,\
                  wibno=wibno,  fembno=fembno, asicno=asicno, gain=gains[0], tp=tps[0] ,\
                  jumbo_flag=False, apa= "ProtoDUNE" )
 
#    asic_coh_plot_wire(out_path, asic_results, wiretype = "U")
#    asic_coh_plot_wire(out_path, asic_results, wiretype = "V")
#    asic_coh_plot_wire(out_path, asic_results, wiretype = "X")
#    asic_coh_plot_wire(out_path, asic_results, wiretype = "UV")
#    asic_coh_plot_wire(out_path, asic_results, wiretype = "UVX")

    asic_wf_plot_wire(out_path, asic_results, wiretype = "U")
#    asic_wf_plot_wire(out_path, asic_results, wiretype = "V")
#    asic_wf_plot_wire(out_path, asic_results, wiretype = "X")

#    asic_fft_plot_wire(out_path, asic_results, wiretype = "U")
#    asic_fft_plot_wire(out_path, asic_results, wiretype = "V")
#    asic_fft_plot_wire(out_path, asic_results, wiretype = "X")
    print "Done, please punch \"Eneter\" or \"return\" if necessary! "

 



#####    asic_results = wfcoh_a_asic(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = APAno, \
#####                  rmsrunno = rmsrunno, fpgarunno = fpgarunno, asicrunno = asicrunno,\
#####                  wibno=wibno,  fembno=fembno, asicno=asicno, gain=gains[0], tp=tps[0] ,\
#####                  jumbo_flag=False, apa= "ProtoDUNE" )
#### 
####    asic_results = wf_a_asic(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno = APAno, \
####                  rmsrunno = rmsrunno, fpgarunno = fpgarunno, asicrunno = asicrunno,\
####                  wibno=wibno,  fembno=fembno, asicno=asicno, gain=gains[0], tp=tps[0] ,\
####                  jumbo_flag=False, apa= "ProtoDUNE" )
#### 
#####    asic_coh_plot_wire(out_path, asic_results, wiretype = "U")
#####    asic_coh_plot_wire(out_path, asic_results, wiretype = "V")
#####    asic_coh_plot_wire(out_path, asic_results, wiretype = "X")
#####    asic_coh_plot_wire(out_path, asic_results, wiretype = "UV")
#####    asic_coh_plot_wire(out_path, asic_results, wiretype = "UVX")
####
####    asic_wf_plot_wire(out_path, asic_results, wiretype = "U")
####    asic_wf_plot_wire(out_path, asic_results, wiretype = "V")
####    asic_wf_plot_wire(out_path, asic_results, wiretype = "X")
####
#####    asic_fft_plot_wire(out_path, asic_results, wiretype = "U")
#####    asic_fft_plot_wire(out_path, asic_results, wiretype = "V")
#####    asic_fft_plot_wire(out_path, asic_results, wiretype = "X")
####    print "Done, please punch \"Eneter\" or \"return\" if necessary! "

 

#waveform
#    ped_wf_subplot(ax2, hfdata_slice,       hfped, hfrms,  t_rate=0.5, title="Waveforms of data after HPF", label=hflabel )
#    ped_wf_subplot(ax4, hfdata_100us_slice, hfped, hfrms,  t_rate=100, title="Waveforms of data after HPF", label=hflabel )
#    fe_gain = int(rms_info[0])/10.0
#    fe_tp = int(rms_info[1])/10.0
#    feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, rms_info[2])
#    fig.suptitle(apainfo_str + wireinfo_str + ".png", fontsize = 16)

##############backup
#def asic_coh_plot(asic_results):
#    w_results = []
#    wi = 0
#    for chni in range(16):
#        chn_noise_paras = asic_results[chni]
#        wireinfo =  chn_noise_paras[19]
#        APAno =  chn_noise_paras[1]
#        unstk_ratio  =  chn_noise_paras[12]
#        if (unstk_ratio > 0.9) :
#            data_slice = chn_noise_paras[13]
#            if ( wi == 0):
#                avg_data = np.array(data_slice)
#            else:
#                avg_data = avg_data + np.array(data_slice)
#            wi = wi + 1
#            w_results.append(asic_results[chni])
# 
#    coh_data = (avg_data*1.0/wi) 
#    coh_data = coh_data - np.mean( coh_data)
#    for chni in range(len(w_results)):
#        fig = plt.figure(figsize=(32,18))
#        axu = []
#        axm = []
#        axd = []
#        for i in range(3):
#            axu.append( plt.subplot2grid((3, 3), (0, i), colspan=1, rowspan=1)) 
#            axm.append( plt.subplot2grid((3, 3), (1, i), colspan=1, rowspan=1)) 
#            axd.append( plt.subplot2grid((3, 3), (2, i), colspan=1, rowspan=1)) 
# 
#        chn_noise_paras = w_results[chni]
#        wireinfo =  chn_noise_paras[19]
#        APAno =  chn_noise_paras[1]
#        rms =  chn_noise_paras[6]
#        ped =  chn_noise_paras[7]
#        rawdata = chn_noise_paras[13]
#        unstk_ratio  =  chn_noise_paras[12]
#        pos_data = np.array (rawdata) - coh_data
#        pos_ped = np.mean(pos_data[0:100000])
#        pos_rms = np.std(pos_data[0:100000])
#        apainfo =  chn_noise_paras[0]
#        label = wireinfo[0] + "_ASIC" + str(wireinfo[2]) + "_CHN" + wireinfo[3]  
#        ped_wf_subplot(axu[0], rawdata[0:2000],    ped,   rms,    t_rate=0.5, title="Waveforms of raw data (2MSPS)", label=label )
#        ped_wf_subplot(axm[0], coh_data[0:2000],   np.mean(coh_data), np.std(coh_data)  ,    t_rate=0.5, title="Waveforms of coherent noise (2MSPS)", label=label )
#        ped_wf_subplot(axd[0], pos_data[0:2000],   pos_ped,   pos_rms,    t_rate=0.5, title="Waveforms of post-filter data (2MSPS)", label=label )
#
#        rf_l, rp_l = chn_rfft_psd(rawdata, fft_s = len(rawdata), avg_cycle = 1)
#        cf_l, cp_l = chn_rfft_psd(coh_data, fft_s = len(coh_data), avg_cycle = 1)
#        pf_l, pp_l = chn_rfft_psd(pos_data, fft_s = len(pos_data), avg_cycle = 1)
#
##        ped_wf_subplot(axu[1], rawdata[::200],    ped,   rms,    t_rate=100, title="Waveforms of raw data (10kSPS)", label=label )
##        ped_wf_subplot(axm[1], coh_data[::200],   np.mean(coh_data), np.std(coh_data)  ,    t_rate=100, title="Waveforms of coherent noise (10kSPS)", label=label )
##        ped_wf_subplot(axd[1], pos_data[::200],   pos_ped,   pos_rms,    t_rate=100, title="Waveforms of post-filter data (10kSPS)", label=label )
# 
#        ped_fft_subplot(axu[1], rf_l, rp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
#        ped_fft_subplot(axm[1], cf_l, cp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
#        ped_fft_subplot(axd[1], pf_l, pp_l, maxx=1000000,  title="FFT specturm", label=label, peaks_note = False )
#
#        ped_fft_subplot(axu[2], rf_l, rp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
#        ped_fft_subplot(axm[2], cf_l, cp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
#        ped_fft_subplot(axd[2], pf_l, pp_l, maxx=100000,  title="FFT specturm", label=label, peaks_note = False )
#
#        fig_title = apainfo[0] + "_" + apainfo[1] + "_FE%d"%(wireinfo[2])
#        plt.tight_layout( rect=[0, 0.05, 1, 0.95])
#        fig.suptitle(fig_title, fontsize = 20)
#        plt.savefig("./"+ fig_title + "_allcoh_%s.png"%label, format='png')
#        plt.close()
#


