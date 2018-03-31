# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Wed Mar 28 11:06:53 2018
"""
#import matplotlib
#matplotlib.use('Agg')
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

def load_sum (rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno ):
    sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
    rd_fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+ ".allsum"
    fp = sum_path + rd_fn

    fp = "/Users/shanshangao/Documents/data2/APA4_run02rms_run01fpg_run01asi.allsum"
    if (os.path.isfile(fp)): 
        with open(fp, "rb") as fp:
            sumtodict = pickle.load(fp)
    else:
        print fp + " doesn't exist, exit anyway"
        exit()
    return sumtodict

def enctp_sort_bywire (dicts,  wiretype="X"  ) :
    sort_apa_wires = []
    for loc in range(1, 21, 1):
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

def dict_filter (dicts, and_dnf =[["gain","250"]], or_dnf = [["gain","250"]]  ) :
    and_apa_wires = []
    for chi in dicts:
        for dn in and_dnf:
            cs = True
            if chi[dn[0]] != dn[1]:
                cs = False
                break
        if (cs):
            and_apa_wires.append(chi)

    or_apa_wires = []
    for chi in and_apa_wires:
        for dn in or_dnf:
            if chi[dn[0]] == dn[1]:
                or_apa_wires.append(chi)
                break

    return or_apa_wires

def apa_sorted_by_wire(orgdicts, g="250", tp="05") :
    dicts = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V"  ) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U"  ) 
    return xdicts, vdicts, udicts

def femb_sorted_by_wire(orgdicts, g="250", tp="05", wibno=0, fembno=0) :
    dicts = dict_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp], ["wib", wibno], ["femb", fembno] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V"  ) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U"  ) 
    print len(xdicts), len(vdicts), len(udicts)
    return xdicts, vdicts, udicts

def find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=0) :
    dicts = dict_filter(orgdicts, and_dnf =[["wib", wibno], ["femb", fembno], ["fembchn", fembchn] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    print len(dicts)
    return dicts

#def wib_enctp_plot (orgdicts, wibno=0, title="WIB ENC vs. Tp", rmstype="sfrms") :
def apa_plots (pp, orgdicts, title="APA ENC vs. Tp", rmstype="sfrms", calitype="fpg_gain" ) :
    gs=["250", "140"]
    #tps=["05", "10", "20", "30"]
    tps=["05", "10", "20", "30"]
    xenc_tps=[]
    venc_tps=[]
    uenc_tps=[]
    for g in gs:
        for tp in tps:
            xd,vd,ud=apa_sorted_by_wire(orgdicts, g=g, tp=tp) 
            rms_c_plots (pp, xd, title="RMS Compare" ) 
            rms_c_plots (pp, vd, title="RMS Compare" ) 
            rms_c_plots (pp, ud, title="RMS Compare" ) 

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
        ped.append(dicts[i]["rms"])
        hfped.append(dicts[i]["hfrms"])
        sfped.append(dicts[i]["sfrms"])
        fpg_gain.append(dicts[i]["fpg_gain"])
        asi_gain.append(dicts[i]["asi_gain"])
        unstk_ratio.append(dicts[i]["unstk_ratio"])
    return apachn, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio


def sub_rms_c_plots (ax, dicts, rms_cs="rms", cali_cs="fpg_gain" ) :
    apachn = 0
    for loc in range(1,21,1):
        subdicts = enctp_sort_byapaloc (dicts,  apaloc=loc  ) 
        ymax = 2500
        if subdicts != None:
            apaloc = subdicts[0]["apaloc"]
            wibno = subdicts[0]["wib"]
            fembno = subdicts[0]["wib"]
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

            ax.plot(apachn, enc,color="C" + str(loc%10))
            ax.scatter(apachn, enc, marker='.',color="C" + str(loc%10))
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
    ax.set_xlim([0,len(apachn)*20 ])
    tp = int( dicts[0]["tp"]) / 10.0
    gain = int(dicts[0]["gain"]) / 10.0
    ax.set_ylabel("ENC /e$^-$")
    ax.set_xlabel("%s wire no."%dicts[0]["wire"][0])
    ax.set_title( "%s: ENC of each channel @ (%2.1fmV/fC, %1.1f$\mu$s)"%(t, gain, tp) )


def sub_rms_p_plots (ax, dicts, rms_cs="hfrms" ) :
    apachn = 0
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



def enctp_sort_bywire (dicts,  wiretype="X"  ) :
    sort_apa_wires = []
    for loc in range(1, 21, 1):
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


def rms_c_plots (pp, dicts, title="RMS Compare" ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=1)
    ax5 = plt.subplot2grid((4, 4), (3, 2), colspan=2, rowspan=1)

    sub_rms_c_plots (ax1, dicts , rms_cs="rms", cali_cs="fpg_gain") 
    sub_rms_c_plots (ax2, dicts , rms_cs="hfrms", cali_cs="fpg_gain") 
    sub_rms_c_plots (ax3, dicts , rms_cs="sfrms", cali_cs="fpg_gain") 
    sub_rms_p_plots (ax4, dicts, rms_cs="hfrms" ) 
    sub_rms_p_plots (ax5, dicts, rms_cs="sfrms" ) 

    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig(pp, format='pdf')
#    plt.show()
    plt.close()



rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
APAno=4
rmsrunno = "run02rms" #
fpgarunno = "run01fpg" #
asicrunno = "run01asi" #

orgdicts = load_sum (rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno )

apa_sorted_by_wire (orgdicts) 

fp = "/Users/shanshangao/Documents/data2/APA4_run02rms_run01fpg_run01asi.pdf"
pp = PdfPages(fp)

apa_plots (pp, orgdicts, title="APA ENC vs. Tp", rmstype="sfrms", calitype="fpg_gain" ) 
pp.close()
#femb_sorted_by_wire(orgdicts, g="250", tp="05", wibno=0, fembno=0) 
#find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=0) 

