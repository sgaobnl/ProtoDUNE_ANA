# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/10/2018 9:37:27 PM
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

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

from matplotlib.backends.backend_pdf import PdfPages

import pickle

def load_sum (sum_path, rd_fn):
    fp = sum_path + rd_fn

    if (os.path.isfile(fp)): 
        with open(fp, "rb") as fp:
            sumtodict = pickle.load(fp)
    else:
        print fp + " doesn't exist, exit anyway"
        exit()
    return sumtodict

def enctp_sort_bywire (dicts,  wiretype="X", fembs_on_apa = range(1, 21, 1) ) :
    sort_apa_wires = []
    for loc in fembs_on_apa:
        cs_wib_wires = []
        if (loc <= 10):
            apaloc = format(loc, "02d")
        else:
            apaloc = format(loc, "02d")

        for chi in dicts:
            if (chi["wire"][0] == wiretype) and (chi["apaloc"][2:] == apaloc):
                cs_wib_wires.append(chi) 
        sorted(cs_wib_wires, key=lambda x:x["wire"])
        sort_apa_wires = sort_apa_wires + cs_wib_wires
    return sort_apa_wires

def enctp_sort_byapaloc (dicts,  apaloc=0  ) :
    sort_wires = []
    apaloc_str = format(apaloc, "02d")
    for chi in dicts:
        if (chi["apaloc"][2:] == apaloc_str):
            sort_wires.append(chi) 
    if (len(sort_wires) == 0 ):
        sort_wires = None
    else:
        sort_wires = sorted(sort_wires, key=lambda x:x["wire"])
    return sort_wires

def enctp_sort_byfemb (femb_dicts ) :
    sdicts = sorted(femb_dicts, key=lambda x:x["fembchn"])
    return sdicts

def dict_filter (dicts, and_dnf =[["gain","250"]], or_dnf = [["gain","250"]], and_flg = True, or_flg = True  ) :
    if (and_flg):
        and_apa_wires = []
        for chi in dicts:
            for dn in and_dnf:
                cs = True
                if chi[dn[0]] != dn[1]:
                    cs = False
                    break
            if (cs):
                and_apa_wires.append(chi)
    else:
        and_apa_wires = dicts
    if (or_flg):
        or_apa_wires = []
        for chi in and_apa_wires:
            for dn in or_dnf:
                if chi[dn[0]] == dn[1]:
                    or_apa_wires.append(chi)
                    break
    else:
        or_apa_wires = and_apa_wires
    return or_apa_wires

def apa_sorted_by_wire(orgdicts, g="250", tp="05", fembs_on_apa = range(1, 21, 1)) :
    dicts = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X" , fembs_on_apa = fembs_on_apa ) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V" , fembs_on_apa = fembs_on_apa ) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U" , fembs_on_apa = fembs_on_apa ) 
    return xdicts, vdicts, udicts

def femb_sorted_by_wire(orgdicts, g="250", tp="05", wibno=0, fembno=0, fembs_on_apa = range(1, 21, 1)) :
    dicts = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp], ["wib", wibno], ["femb", fembno] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X" , fembs_on_apa = fembs_on_apa) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V" , fembs_on_apa = fembs_on_apa) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U" , fembs_on_apa = fembs_on_apa) 
    return xdicts, vdicts, udicts

def find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=0) :
    dicts = dict_filter(orgdicts, and_dnf =[["wib", wibno], ["femb", fembno], ["fembchn", fembchn] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    return dicts

def draw_results (dicts) :
    apachn=[]
    rms=[]
    hfrms=[]
    sfrms=[]
    ped=[]
    hfped=[]
    sfped=[]
    fpg_gain=[]
    asi_gain=[]
    unstk_ratio = []
    for i in range(len(dicts)):
        if dicts[i]["wire"][0] == "X":
            apachn.append(48*(int(dicts[i]["apaloc"][2:4])-1) + int(dicts[i]["wire"][1:3]))
        elif dicts[i]["wire"][0] == "V":
            apachn.append(40*(int(dicts[i]["apaloc"][2:4])-1) + int(dicts[i]["wire"][1:3]))
        elif dicts[i]["wire"][0] == "U":
            apachn.append(40*(int(dicts[i]["apaloc"][2:4])-1) + int(dicts[i]["wire"][1:3]))
        rms.append(dicts[i]["rms"])
        hfrms.append(dicts[i]["hfrms"])
        sfrms.append(dicts[i]["sfrms"])
        ped.append(dicts[i]["ped"])
        hfped.append(dicts[i]["hfped"])
        sfped.append(dicts[i]["sfped"])
        fpg_gain.append(dicts[i]["fpg_gain"])
        asi_gain.append(dicts[i]["asi_gain"])
        unstk_ratio.append(dicts[i]["unstk_ratio"])
    return apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio

###############################################################################################################################
###############################################################################################################################
def sub_rms_c_plot5 (ax, dicts, rms_cs="rms", cali_cs="fpg_gain", fembs_on_apa = range(1, 21, 1) ) :
    apachn = [] 
    for loc in fembs_on_apa:
        subdicts = enctp_sort_byapaloc (dicts,  apaloc=loc  ) 
        ymax = 2500
        if subdicts != None:
            apaloc = subdicts[0]["apaloc"]
            wibno = subdicts[0]["wib"]
            fembno = subdicts[0]["femb"]
            apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (subdicts) 
            if (rms_cs=="rms" ):
                plotrms = rms
                t = "Raw Data"
            elif (rms_cs=="hfrms" ):
                plotrms = hfrms
                t = "Data after HPF"
            elif (rms_cs=="sfrms" ):
                plotrms = sfrms
                t = "Stuck Free Data"
            else:
                plotrms = rms
                t = "Raw Data"

            if (cali_cs=="fpg_gain" ):
                plotgain = fpg_gain
            else:
                plotgain = asi_gain

            enc = np.array(plotrms)*np.array(plotgain)
            encmean = np.mean(enc)
            encstd = np.std(enc)

            #ax.plot(apachn, enc,color="C" + str(loc%10))
            ax.plot(apachn, enc,)
            ax.scatter(apachn, enc, marker='.')
            #ax.scatter(apachn, enc, marker='.',color="C" + str(loc%10))
            ax.text(apachn[5], ymax*0.96, apaloc, fontsize=8)
            ax.text(apachn[5], ymax*0.92, "wib%d"%wibno, fontsize=6)
            ax.text(apachn[5], ymax*0.88, "femb%d"%fembno, fontsize=6)
            ax.text(apachn[5], ymax*0.80, "%de$^-$"%encmean, fontsize=6)
            ax.text(apachn[5], ymax*0.76, "$\pm$%d"%encstd, fontsize=6)
            ax.vlines(apachn[0], 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
        else:
            if ( loc == 1):
                ax.text(5, ymax*0.96, "Dead", fontsize=8)
            else:
                ax.text(5+(loc-1)*len(apachn), ymax*0.96, "Dead", fontsize=8)
                ax.vlines((loc-1)*len(apachn), 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
 
    ax.set_ylim([0,ymax])
    ax.set_xlim([len(apachn)*(fembs_on_apa[0]-1),len(apachn)*(fembs_on_apa[-1]) ])
    tp = int( dicts[0]["tp"]) / 10.0
    gain = int(dicts[0]["gain"]) / 10.0
    ax.set_ylabel("ENC /e$^-$")
    ax.set_xlabel("%s wire no."%dicts[0]["wire"][0])
    ax.set_title( "%s: ENC of each channel @ (%2.1fmV/fC, %1.1f$\mu$s)"%(t, gain, tp) )

def sub_rms_p_plot5 (ax, dicts, rms_cs="hfrms" ) :
    apachn = []
    apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (dicts) 
    if (rms_cs=="rms" ):
        plotrms = rms
        t = "Raw Data"
    elif (rms_cs=="hfrms" ):
        plotrms = hfrms
        t = "Data after HPF"
    elif (rms_cs=="sfrms" ):
        plotrms = sfrms
        t = "Stuck Free Data"
    else:
        plotrms = rms
        t = "Raw Data"

    cmp_rms = np.array(rms) / (np.array(plotrms) *1.0 ) 
    rms110_cnt = 0
    rms90_cnt = 0
    for i in cmp_rms:
        if i > 1.1:
            rms110_cnt = rms110_cnt + 1
        elif i < 0.9:
            rms90_cnt = rms90_cnt + 1
    totalchn = len(cmp_rms)
    ratio110 = rms110_cnt*100.0/totalchn
    ratio90 = rms90_cnt*100.0/totalchn
    label = "%d channels, R > 1.1: %2.1f%%  R < 0.9: %2.1f%%"%(totalchn, ratio110, ratio90)

    weights = np.ones_like(cmp_rms)/float(len(cmp_rms))
    #ax.hist(cmp_rms, weights=weights, bins=20, range=(0.05, 2.05),  stacked = True, histtype='bar', label= label, color='b', rwidth=0.9 )
    ax.hist(cmp_rms, weights=weights, bins=20, stacked = True, histtype='bar', label= label, color='b', rwidth=0.9 )
    ax.set_xlabel("Ratio", fontsize = 8)
    tp = int( dicts[0]["tp"]) / 10.0
    gain = int(dicts[0]["gain"]) / 10.0
    ax.set_title( "ENC(Raw Data)/ENC(%s) @ (%2.1fmV/fC, %1.1f$\mu$s)"%(t, gain, tp), fontsize = 10 )
    ax.set_ylabel("Normalized channels", fontsize = 8)
    ax.set_ylim([0,1])
    ax.legend(loc='best', fontsize=9)

def apa_plot5 (pp, orgdicts, title="APA ENC vs. Tp", rmstype="sfrms", calitype="fpg_gain" , fembs_on_apa = range(1, 21, 1)) :
    gs=["250", "140"]
    tps=["05", "10", "20", "30"]
    xenc_tps=[]
    venc_tps=[]
    uenc_tps=[]
    for g in gs:
        for tp in tps:
            xd,vd,ud=apa_sorted_by_wire(orgdicts, g=g, tp=tp, fembs_on_apa=fembs_on_apa) 
            rms_c_plot5 (pp, xd, title="RMS Compare" ) 
            rms_c_plot5 (pp, vd, title="RMS Compare" ) 
            rms_c_plot5 (pp, ud, title="RMS Compare" ) 

def rms_c_plot5 (pp, dicts, title="RMS Compare" ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=1)
    ax5 = plt.subplot2grid((4, 4), (3, 2), colspan=2, rowspan=1)

    sub_rms_c_plot5 (ax1, dicts , rms_cs="rms", cali_cs="fpg_gain") 
    sub_rms_c_plot5 (ax2, dicts , rms_cs="hfrms", cali_cs="fpg_gain") 
    sub_rms_c_plot5 (ax3, dicts , rms_cs="sfrms", cali_cs="fpg_gain") 
    sub_rms_p_plot5 (ax4, dicts, rms_cs="hfrms" ) 
    sub_rms_p_plot5 (ax5, dicts, rms_cs="sfrms" ) 

    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()

###############################################################################################################################
###############################################################################################################################
def draw_enctp_plot0(wdicts, calitype = "fpg_gain"):
    dr = draw_results (wdicts) 
    drchns = len(dr[0])
    if calitype == "fpg_gain":
        plot_gains = dr[7]
    else:
        plot_gains = dr[8]
    dr_enc = np.array(dr[1]) * np.array(plot_gains)
    dr_encmean = np.mean(dr_enc)
    dr_encstd = np.std(dr_enc)
    dr_sfenc = np.array(dr[3]) * np.array(plot_gains)
    dr_sfencmean = np.mean(dr_sfenc)
    dr_sfencstd = np.std(dr_sfenc)
    dr_hfenc = np.array(dr[2]) * np.array(plot_gains)
    dr_hfencmean = np.mean(dr_hfenc)
    dr_hfencstd = np.std(dr_hfenc)
    return drchns, dr_encmean, dr_encstd, dr_sfencmean, dr_sfencstd, dr_hfencmean, dr_hfencstd

def sub_enctp_plot0 (ax, g,calitype, tp_us, xchns, xenc_tps, vchns, venc_tps, uchns, uenc_tps, title="APA ENC vs. Tp" , note="Raw data") :
    if (calitype == "fpg_gain"):
        dactype = "FPGA DAC"
    else:
        dactype = "ASIC DAC"
    title = title + "(%s, %s.%smV/fC, %s)"%(note, g[0:2],g[2], dactype)

    x = tp_us
    y = [xenc_tps[0][0], xenc_tps[1][0], xenc_tps[2][0], xenc_tps[3][0]]
    maxy = np.max(y)
    e = [xenc_tps[0][1], xenc_tps[1][1], xenc_tps[2][1], xenc_tps[3][1]]
    label = "%d"%xchns +" X " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='g', marker='o')
    #for xye in zip(x, y, e):                                   
        #ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 1500], textcoords='data', color='g') 
        #ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 1500], textcoords='data', color='g') 

    y = [venc_tps[0][0], venc_tps[1][0], venc_tps[2][0], venc_tps[3][0]]
    if (np.max(y) >  maxy):
        maxy = np.max(y) 
    e = [venc_tps[0][1], venc_tps[1][1], venc_tps[2][1], venc_tps[3][1]]
    label = "%d"%vchns +" V " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='b', marker='o')
    #for xye in zip(x, y, e):                                   
        #ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 1650], textcoords='data', color='b') 

    y = [uenc_tps[0][0], uenc_tps[1][0], uenc_tps[2][0], uenc_tps[3][0]]
    if (np.max(y) >  maxy):
        maxy = np.max(y) 
    e = [uenc_tps[0][1], uenc_tps[1][1], uenc_tps[2][1], uenc_tps[3][1]]
    label = "%d"%uchns +" U " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='r', marker='o')
    #for xye in zip(x, y, e):                                   
        #ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 1800], textcoords='data', color='r') 

    ax.legend(loc=4)
    ax.set_xlim([0,4])
    ax.set_xlabel("Peaking time / ($\mu$s)")
    if maxy > 2000:
        maxy = (maxy//1000 + 1)*1000
    else:
        maxy = 2000
    ax.set_ylim([0,maxy])
    ax.set_ylabel("ENC /e-")
    ax.set_title(title )
    ax.grid()

def plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "sf" ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    gs=["250", "140"]
    tps=["05", "10", "20", "30"]

    encgs = []
    for g in gs:
        tp_us = []
        xenc_tps=[]
        xsfenc_tps=[]
        xhfenc_tps=[]

        venc_tps=[]
        vsfenc_tps=[]
        vhfenc_tps=[]

        uenc_tps=[]
        usfenc_tps=[]
        uhfenc_tps=[]
 
        for tp in tps:
            tp_us.append(int(tp)/10.0)
            xd, vd, ud = apa_sorted_by_wire(orgdicts, g=g, tp=tp) 

            xdr = draw_enctp_plot0(xd, calitype = calitype)
            xchns = xdr[0]
            xenc_tps.append  ([xdr[1],xdr[2]])
            xsfenc_tps.append([xdr[3],xdr[4]])
            xhfenc_tps.append([xdr[5],xdr[6]])
                
            vdr = draw_enctp_plot0(vd, calitype = calitype)
            vchns = vdr[0]
            venc_tps.append  ([vdr[1],vdr[2]])
            vsfenc_tps.append([vdr[3],vdr[4]])
            vhfenc_tps.append([vdr[5],vdr[6]])

            udr = draw_enctp_plot0(ud, calitype = calitype)
            uchns = udr[0]
            uenc_tps.append  ([udr[1],udr[2]])
            usfenc_tps.append([udr[3],udr[4]])
            uhfenc_tps.append([udr[5],udr[6]])
 
        if ( g == "250" ):
            sub_enctp_plot0 (ax1, g, calitype, tp_us, xchns, xenc_tps, vchns, venc_tps, uchns, uenc_tps, note="Raw data") 
            if (sfhf == "sf"):
                sub_enctp_plot0 (ax3, g, calitype, tp_us, xchns, xsfenc_tps, vchns, vsfenc_tps, uchns, usfenc_tps, note="Stuck Free") 
            else:
                sub_enctp_plot0 (ax3, g, calitype, tp_us, xchns, xhfenc_tps, vchns, vhfenc_tps, uchns, uhfenc_tps, note="HPF data") 
        else:
            sub_enctp_plot0 (ax2, g, calitype, tp_us, xchns, xenc_tps, vchns, venc_tps, uchns, uenc_tps, note="Raw data") 
            if (sfhf == "sf"):
                sub_enctp_plot0 (ax4, g, calitype, tp_us, xchns, xsfenc_tps, vchns, vsfenc_tps, uchns, usfenc_tps, note="Stuck Free") 
            else:
                sub_enctp_plot0 (ax4, g, calitype, tp_us, xchns, xhfenc_tps, vchns, vhfenc_tps, uchns, uhfenc_tps, note="HPF data") 

    fig.suptitle("Noise Measurement", fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()

###############################################################################################################################
###############################################################################################################################
def plot1_chns_enc (pp, orgdicts, title="APA ENC s. Tp", wiretype="X",  cali_cs="fpg_gain", rms_cs = "raw", g="250" , fembs_on_apa = range(1, 21, 1)) : #enctype, raw, hf, sf
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=4, rowspan=3)
    ax2 = plt.subplot2grid((4, 4), (3, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((4, 4), (3, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((4, 4), (3, 2), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((4, 4), (3, 3), colspan=1, rowspan=1)

    tps=["05", "10", "20", "30"]
    xenc_tps=[]
    venc_tps=[]
    uenc_tps=[]
    for tp in tps:
        dicts_xvu = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
        dicts = enctp_sort_bywire (dicts_xvu,  wiretype=wiretype , fembs_on_apa = fembs_on_apa ) 
        sub_chns_plot1 (ax1, dicts, rms_cs=rms_cs, cali_cs=cali_cs, fembs_on_apa = fembs_on_apa  ) 
        if ( tp == "05" ):
            sub_chns_hist_plot1 (ax2, dicts, rms_cs=rms_cs, cali_cs=cali_cs ) 
        elif ( tp == "10" ):
            sub_chns_hist_plot1 (ax3, dicts, rms_cs=rms_cs, cali_cs=cali_cs ) 
        elif ( tp == "20" ):
            sub_chns_hist_plot1 (ax4, dicts, rms_cs=rms_cs, cali_cs=cali_cs ) 
        elif ( tp == "30" ):
            sub_chns_hist_plot1 (ax5, dicts, rms_cs=rms_cs, cali_cs=cali_cs ) 

    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()

def sub_chns_plot1 (ax, dicts, rms_cs="rms", cali_cs="fpg_gain", fembs_on_apa = range(1, 21, 1) ) :
    apachn = [] 
    for loc in fembs_on_apa:
        subdicts = enctp_sort_byapaloc (dicts,  apaloc=loc  ) 
        ymax = 2000
        tp = int( dicts[0]["tp"]) / 10.0
        if subdicts != None:
            apaloc = subdicts[0]["apaloc"]
            wibno = subdicts[0]["wib"]
            fembno = subdicts[0]["femb"]
            apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (subdicts) 
            if (rms_cs=="rms" ):
                plotrms = rms
                t = "Raw Data"
            elif (rms_cs=="hfrms" ):
                plotrms = hfrms
                t = "Data after HPF"
            elif (rms_cs=="sfrms" ):
                plotrms = sfrms
                t = "Stuck Free Data"
            else:
                plotrms = rms
                t = "Raw Data"

            if (cali_cs=="fpg_gain" ):
                plotgain = fpg_gain
            else:
                plotgain = asi_gain

            enc = np.array(plotrms)*np.array(plotgain)

            label = "%1.1f$\mu$s)"%tp 
            #ax.scatter(apachn, enc, marker='.',color="C" + str(loc%6+4))
            ax.scatter(apachn, enc, marker='.')
            if (loc == 1):
                #ax.plot(apachn, enc,color="C" + str(int(tp)), label=label)
                ax.plot(apachn, enc, label=label)
            else:
                #ax.plot(apachn, enc,color="C" + str(int(tp)))
                ax.plot(apachn, enc)
            if (tp ==2):
                ax.text(apachn[5], ymax*0.96, apaloc, fontsize=8)
                ax.text(apachn[5], ymax*0.92, "wib%d"%wibno, fontsize=8)
                ax.text(apachn[5], ymax*0.88, "femb%d"%fembno, fontsize=8)
                ax.vlines(apachn[0], 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
        else:
            if (tp ==2):
                ax.text(5+(loc-1)*len(apachn), ymax*0.96, "Dead", fontsize=8)
                if ( loc != 1):
                    ax.vlines((loc-1)*len(apachn), 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
 
    if (tp ==2):
        ax.set_ylim([0,ymax])
        ax.set_xlim([len(apachn)*(fembs_on_apa[0]-1),len(apachn)*(fembs_on_apa[-1]) ])
        gain = int(dicts[0]["gain"]) / 10.0
        ax.set_ylabel("ENC /e$^-$")
        ax.set_xlabel("%s wire no."%dicts[0]["wire"][0])
        ax.set_title( "%s: ENC of %s wires @ (%2.1fmV/fC)"%(t, dicts[0]["wire"][0], gain) )
    ax.legend(loc=7)

def sub_chns_hist_plot1 (ax, dicts, rms_cs="rms", cali_cs="fpg_gain" ) :
    apachn = []
    ymax = 2000
    tp = int( dicts[0]["tp"]) / 10.0
    gain = int(dicts[0]["gain"]) / 10.0
    apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (dicts) 
    if (rms_cs=="rms" ):
        plotrms = rms
        t = "Raw Data"
    elif (rms_cs=="hfrms" ):
        plotrms = hfrms
        t = "Data after HPF"
    elif (rms_cs=="sfrms" ):
        plotrms = sfrms
        t = "Stuck Free Data"
    else:
        plotrms = rms
        t = "Raw Data"

    if (cali_cs=="fpg_gain" ):
        plotgain = fpg_gain
    else:
        plotgain = asi_gain

    enc = np.array(plotrms)*np.array(plotgain)
    encmean = np.mean(enc)
    encstd = np.std(enc)
    N = len(enc)
    sigma5 = int(encstd+1)*5

    ax.grid()
    label = "%1.1f$\mu$s, %d$\pm$%d"%(tp, int(encmean), int(encstd)) 
    ax.hist(enc, normed=1, bins=sigma5*2, range=(encmean-sigma5, encmean+sigma5),  histtype='bar', label=label, color='b', rwidth=0.9 )

    gaussian_x = np.linspace(encmean - 3*encstd, encmean + 3*encstd, 100)
    gaussian_y = mlab.normpdf(gaussian_x, encmean, encstd)
    ax.plot(gaussian_x, gaussian_y, color='r')

    ax.set_title( "Histogram of %s"%(t) )
    ax.set_ylabel("Normalized counts")
    ax.set_xlabel("ENC /e$^-$")
    ax.legend(loc='best')


###############################################################################################################################
###############################################################################################################################
def sub_ped_plot2 (ax, dicts , fembs_on_apa = range(1, 21, 1) ) :
    apachn = []
    for loc in fembs_on_apa:
        subdicts = enctp_sort_byapaloc (dicts,  apaloc=loc  ) 
        ymax = 4100
        tp = int( dicts[0]["tp"]) / 10.0
        if subdicts != None:
            apaloc = subdicts[0]["apaloc"]
            wibno = subdicts[0]["wib"]
            fembno = subdicts[0]["femb"]
            apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (subdicts) 

            label = "%1.1f$\mu$s)"%tp 
            #ax.scatter(apachn, ped, marker='.',color="C" + str(loc%6+4))
            ax.scatter(apachn, ped, marker='.')
            if (loc == 1):
                #ax.plot(apachn, ped,color="C" + str(int(tp)), label=label)
                ax.plot(apachn, ped, label=label)
            else:
                #ax.plot(apachn, ped,color="C" + str(int(tp)))
                ax.plot(apachn, ped)
            ax.text(apachn[5], ymax*0.90, apaloc, fontsize=8)
            ax.text(apachn[5], ymax*0.80, "wib%d"%wibno, fontsize=8)
            ax.text(apachn[5], ymax*0.70, "femb%d"%fembno, fontsize=8)
            ax.vlines(apachn[0], 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
        else:
            ax.text(5+(loc-1)*len(apachn), ymax*0.90, "Dead", fontsize=8)
            if ( loc != 1):
                ax.vlines((loc-1)*len(apachn), 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
    ax.set_ylim([0,ymax])
    ax.set_xlim([len(apachn)*(fembs_on_apa[0]-1),len(apachn)*(fembs_on_apa[-1]) ])
    gain = int(dicts[0]["gain"]) / 10.0
    ax.set_ylabel("ADC output / LSB")
    ax.set_xlabel("%s wire no."%dicts[0]["wire"][0])
    ax.set_title( "Pedestals of %s wires @ (%2.1fmV/fC)"%(dicts[0]["wire"][0], gain) )
    ax.legend(loc=4)

def sub_ped_hist_plot2 (ax, dicts ) :
    apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (dicts) 
    pedmean = np.mean(ped)
    pedstd = np.std(ped)
    N = len(ped)
    sigma5 = int(pedstd+1)*5

    ax.grid()
    label = "%d$\pm$%d"%(int(pedmean), int(pedstd)) 
    ax.hist(ped, normed=1, bins=sigma5*2, range=(pedmean-sigma5, pedmean+sigma5),  histtype='bar', label=label, color='b', rwidth=0.9 )

    gaussian_x = np.linspace(pedmean - 3*pedstd, pedmean + 3*pedstd, 100)
    gaussian_y = mlab.normpdf(gaussian_x, pedmean, pedstd)
    ax.plot(gaussian_x, gaussian_y, color='r')

    ax.set_title( "Histogram of %s wires "%dicts[0]["wire"][0])
    ax.set_ylabel("Normalized counts")
    ax.set_xlabel("ADC output / LSB")
    ax.legend(loc='best')

def plot2_peds (pp, orgdicts, title="Pedestals", g="250", tp="20", fembs_on_apa = range(1, 21, 1)  ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=1)
    ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=1)
    ax3 = plt.subplot2grid((3, 3), (2, 0), colspan=2, rowspan=1)
    ax4 = plt.subplot2grid((3, 3), (0, 2), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((3, 3), (1, 2), colspan=1, rowspan=1)
    ax6 = plt.subplot2grid((3, 3), (2, 2), colspan=1, rowspan=1)

    dicts_xvu = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    dicts = enctp_sort_bywire (dicts_xvu,  wiretype = "X" , fembs_on_apa = fembs_on_apa ) 
    sub_ped_plot2 (ax1, dicts, fembs_on_apa = fembs_on_apa) 
    sub_ped_hist_plot2 (ax4, dicts ) 
    dicts = enctp_sort_bywire (dicts_xvu,  wiretype = "V" , fembs_on_apa = fembs_on_apa) 
    sub_ped_plot2 (ax2, dicts, fembs_on_apa = fembs_on_apa) 
    sub_ped_hist_plot2 (ax5, dicts ) 
    dicts = enctp_sort_bywire (dicts_xvu,  wiretype = "U" , fembs_on_apa = fembs_on_apa) 
    sub_ped_plot2 (ax3, dicts, fembs_on_apa = fembs_on_apa) 
    sub_ped_hist_plot2 (ax6, dicts ) 

    fig.suptitle("Pedestal Measurement", fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()

###############################################################################################################################
###############################################################################################################################
def sub_gain_plot3 (ax, g, tp_us, xchns, xgain, vchns, vgain, uchns, ugain, title="Gain Measurement" , note="FPGA-DAC") :
    title = title + "(%s, %s.%smV/fC)"%(note, g[0:2],g[2])
    x = tp_us
    y = [xgain[0][0], xgain[1][0], xgain[2][0], xgain[3][0]]
    e = [xgain[0][1], xgain[1][1], xgain[2][1], xgain[3][1]]
    label = "%d"%xchns + " X " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='g', marker='o')
    #for xye in zip(x, y, e):                                   
    #    ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 475], textcoords='data', color='g') 

    y = [vgain[0][0], vgain[1][0], vgain[2][0], vgain[3][0]]
    e = [vgain[0][1], vgain[1][1], vgain[2][1], vgain[3][1]]
    label = "%d"%vchns +" V " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='b', marker='o')
    #for xye in zip(x, y, e):                                   
    #    ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 450], textcoords='data', color='b') 

    y = [ugain[0][0], ugain[1][0], ugain[2][0], ugain[3][0]]
    e = [ugain[0][1], ugain[1][1], ugain[2][1], ugain[3][1]]
    label = "%d"%uchns +" U " +  "wires" 
    ax.errorbar(x, y, e, label=label, color='r', marker='o')
    #for xye in zip(x, y, e):                                   
    #    ax.annotate('%d$\pm$%d' % xye[1:3], xy=[xye[0], 425], textcoords='data', color='r') 

    ax.legend(loc=4)
    ax.set_xlim([0,4])
    ax.set_xlabel("Peaking time / ($\mu$s)")
    maxy = 500 
    ax.set_ylim([0,maxy])
    ax.set_ylabel("Gain  e$^-$/LSB")
    ax.set_title(title )
    ax.grid()

def plot3_overall_gain (pp, orgdicts, title="APA Gain Measurement" ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    gs=["250", "140"]
    tps=["05", "10", "20", "30"]

    encgs = []
    for g in gs:
        tp_us = []
        xfpg_dac=[]
        xasi_dac=[]
        vfpg_dac=[]
        vasi_dac=[]
        ufpg_dac=[]
        uasi_dac=[]
 
        for tp in tps:
            tp_us.append(int(tp)/10.0)
            xd, vd, ud = apa_sorted_by_wire(orgdicts, g=g, tp=tp) 
            dr = draw_results (xd) 
            xchns = len(dr[0])
            xfpg_dac.append([np.mean(dr[7]), np.std(dr[7])] )
            xasi_dac.append([np.mean(dr[8]), np.std(dr[8])] )

            dr = draw_results (vd) 
            vchns = len(dr[0])
            vfpg_dac.append([np.mean(dr[7]), np.std(dr[7])] )
            vasi_dac.append([np.mean(dr[8]), np.std(dr[8])] )

            dr = draw_results (ud) 
            uchns = len(dr[0])
            ufpg_dac.append([np.mean(dr[7]), np.std(dr[7])] )
            uasi_dac.append([np.mean(dr[8]), np.std(dr[8])] )
 
        if ( g == "250" ):
            sub_gain_plot3 (ax1, g, tp_us, xchns, xfpg_dac, vchns, vfpg_dac, uchns, ufpg_dac, note="FPGA-DAC") 
            sub_gain_plot3 (ax2, g, tp_us, xchns, xasi_dac, vchns, vasi_dac, uchns, uasi_dac, note="ASIC-DAC") 
        else:
            sub_gain_plot3 (ax3, g, tp_us, xchns, xfpg_dac, vchns, vfpg_dac, uchns, ufpg_dac, note="FPGA-DAC") 
            sub_gain_plot3 (ax4, g, tp_us, xchns, xasi_dac, vchns, vasi_dac, uchns, uasi_dac, note="ASIC-DAC") 
 
    fig.suptitle("Gain Measurement", fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()


###############################################################################################################################
def plot4_chns_gain (pp, orgdicts, title="Gain Measurement", wiretype="X", g="250", cali_cs="fpg_gain", fembs_on_apa = range(1, 21, 1) ): #enctype, raw, hf, sf
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=4, rowspan=3)
    ax2 = plt.subplot2grid((4, 4), (3, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((4, 4), (3, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((4, 4), (3, 2), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((4, 4), (3, 3), colspan=1, rowspan=1)

    tps=["05", "10", "20", "30"]
    xg=[]
    vg=[]
    ug=[]
    for tp in tps:
        dicts_xvu = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
        dicts = enctp_sort_bywire (dicts_xvu,  wiretype=wiretype  ) 
        sub_gain_plot4 (ax1, dicts, cali_cs=cali_cs , fembs_on_apa = fembs_on_apa) 
        if ( tp == "05" ):
            sub_hist_gain_plot4 (ax2, dicts, cali_cs=cali_cs ) 
        elif ( tp == "10" ):
            sub_hist_gain_plot4 (ax3, dicts, cali_cs=cali_cs ) 
        elif ( tp == "20" ):
            sub_hist_gain_plot4 (ax4, dicts, cali_cs=cali_cs ) 
        elif ( tp == "30" ):
            sub_hist_gain_plot4 (ax5, dicts, cali_cs=cali_cs ) 

    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()

def sub_gain_plot4 (ax, dicts, cali_cs="fpg_gain", fembs_on_apa = range(1, 21, 1)  ) :
    apachn = []
    for loc in fembs_on_apa:
        subdicts = enctp_sort_byapaloc (dicts,  apaloc=loc  ) 
        ymax = 500
        tp = int( dicts[0]["tp"]) / 10.0
        if subdicts != None:
            apaloc = subdicts[0]["apaloc"]
            wibno = subdicts[0]["wib"]
            fembno = subdicts[0]["femb"]
            apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (subdicts) 
            if (cali_cs=="fpg_gain" ):
                pgain = fpg_gain
            else:
                pgain = asi_gain
            label = "%1.1f$\mu$s)"%tp 
            #ax.scatter(apachn, pgain, marker='.',color="C" + str(loc%6+4))
            ax.scatter(apachn, pgain, marker='.')
            if (loc == 1):
                #ax.plot(apachn, pgain,color="C" + str(int(tp)), label=label)
                ax.plot(apachn, pgain, label=label)
            else:
                #ax.plot(apachn, pgain,color="C" + str(int(tp)))
                ax.plot(apachn, pgain)
            if (tp ==2):
                ax.text(apachn[5], ymax*0.96, apaloc, fontsize=8)
                ax.text(apachn[5], ymax*0.92, "wib%d"%wibno, fontsize=8)
                ax.text(apachn[5], ymax*0.88, "femb%d"%fembno, fontsize=8)
                ax.vlines(apachn[0], 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
        else:
            if (tp ==2):
                ax.text(5+(loc-1)*len(apachn), ymax*0.96, "Dead", fontsize=8)
                if ( loc != 1):
                    ax.vlines((loc-1)*len(apachn), 0, ymax, color='b',linestyles="dotted", linewidth=0.8)
    if (tp ==2):
        ax.set_ylim([0,ymax])
        #ax.set_xlim([0,len(apachn)*len(fembs_on_apa) ])
        ax.set_xlim([len(apachn)*(fembs_on_apa[0]-1),len(apachn)*(fembs_on_apa[-1]) ])
        gain = int(dicts[0]["gain"]) / 10.0
        ax.set_ylabel("Gain /e$^-$/LSB")
        ax.set_xlabel("%s wire no."%dicts[0]["wire"][0])
        ax.set_title( "Gain of %s wires @ (%2.1fmV/fC)"%(dicts[0]["wire"][0], gain) )
    ax.legend(loc=7)

def sub_hist_gain_plot4 (ax, dicts,  cali_cs="fpg_gain" ) :
    ymax = 500 
    tp = int( dicts[0]["tp"]) / 10.0
    gain = int(dicts[0]["gain"]) / 10.0
    apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio = draw_results (dicts) 
    if (cali_cs=="fpg_gain" ):
        pgain = fpg_gain
    else:
        pgain = asi_gain

    pgainmean = np.mean(pgain)
    pgainstd = np.std(pgain)
    N = len(pgain)
    sigma3 = int(pgainstd+1)*3

    ax.grid()
    label = "%1.1f$\mu$s, %d$\pm$%d"%(tp, int(pgainmean), int(pgainstd)) 
    ax.hist(pgain, normed=1, bins=sigma3*2, range=(pgainmean-sigma3, pgainmean+sigma3),  histtype='bar', label=label, color='b', rwidth=0.9 )

    gaussian_x = np.linspace(pgainmean - 3*pgainstd, pgainmean + 3*pgainstd, 100)
    gaussian_y = mlab.normpdf(gaussian_x, pgainmean, pgainstd)
    ax.plot(gaussian_x, gaussian_y, color='r')

    ax.set_title( "Histogram of Gain")
    ax.set_ylabel("Normalized counts")
    ax.set_xlabel("Gain / e$^-$/LSB")
    ax.legend(loc='best')

