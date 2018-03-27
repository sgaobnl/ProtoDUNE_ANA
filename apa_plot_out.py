# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Tue Mar 27 09:45:50 2018
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

    fp = "/Users/shanshangao/Documents/data2/APA4_run01rms_run01fpg_run01asi.allsum"
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

def enctp_sort_byfemb (femb_dicts ) :
    sdicts = sorted(femb_dicts, key=lambda x:x["fembchn"])
    return sdicts

def enctp_filter (dicts, and_dnf =[["gain","250"]], or_dnf = [["gain","250"]]  ) :
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


def chn_enctp (orgdicts, wibno=0, fembno=0, fembchn=0, gain="250", rmstype="rms", gaintype="fpg_gain") :
    xwires = {"X":"X","05":[],"10":[],"20":[],"30":[]} 
    vwires = {"V":"V","05":[],"10":[],"20":[],"30":[]} 
    uwires = {"U":"U","05":[],"10":[],"20":[],"30":[]} 

    for chi in orgdicts:
        if (chi["wib"] == wibno) and (chi["femb"] == fembno) and (chi["fembchn"] == fembchn) :
            if (chi["gain"] == gain) and (chi["wire"][0] == "X") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        xwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "V") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        vwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "U") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        uwires[tp].append(chi[rmstype] * chi[gaintype])
    for tp in ["05", "10", "20", "30"]:
        if len(xwires[tp]) > 0:
            xwires[tp] =[int(np.mean(xwires[tp])), int(np.std(xwires[tp])) ]  
        else:
            xwires[tp]  = None
        if len(vwires[tp]) > 0:
            vwires[tp] =[int(np.mean(vwires[tp])), int(np.std(vwires[tp])) ]  
        else:
            vwires[tp]  = None
        if len(uwires[tp]) > 0:
            uwires[tp] =[int(np.mean(uwires[tp])), int(np.std(uwires[tp])) ]  
        else:
            uwires[tp]  = None
 
    return [xwires, vwires, uwires]

def femb_enctp (orgdicts, wibno=0, fembno=0, gain="250", rmstype="rms", gaintype="fpg_gain") :
    xwires = {"X":"X","05":[],"10":[],"20":[],"30":[]} 
    vwires = {"V":"V","05":[],"10":[],"20":[],"30":[]} 
    uwires = {"U":"U","05":[],"10":[],"20":[],"30":[]} 

    for chi in orgdicts:
        if (chi["wib"] == wibno) and (chi["femb"] == fembno) :
            if (chi["gain"] == gain) and (chi["wire"][0] == "X") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        xwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "V") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        vwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "U") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        uwires[tp].append(chi[rmstype] * chi[gaintype])
    for tp in ["05", "10", "20", "30"]:
        if len(xwires[tp]) > 0:
            xwires[tp] =[int(np.mean(xwires[tp])), int(np.std(xwires[tp])) ]  
        else:
            xwires[tp]  = None
        if len(vwires[tp]) > 0:
            vwires[tp] =[int(np.mean(vwires[tp])), int(np.std(vwires[tp])) ]  
        else:
            vwires[tp]  = None
        if len(uwires[tp]) > 0:
            uwires[tp] =[int(np.mean(uwires[tp])), int(np.std(uwires[tp])) ]  
        else:
            uwires[tp]  = None
 
    return [xwires, vwires, uwires]

def wib_enctp (orgdicts, wibno=0, gain="250", rmstype="rms", gaintype="fpg_gain") :
    xwires = {"X":"X","05":[],"10":[],"20":[],"30":[]} 
    vwires = {"V":"V","05":[],"10":[],"20":[],"30":[]} 
    uwires = {"U":"U","05":[],"10":[],"20":[],"30":[]} 

    for chi in orgdicts:
        if (chi["wib"] == wibno):
            if (chi["gain"] == gain) and (chi["wire"][0] == "X") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        xwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "V") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        vwires[tp].append(chi[rmstype] * chi[gaintype])

            if (chi["gain"] == gain) and (chi["wire"][0] == "U") :
                for tp in ["05", "10", "20", "30"]:
                    if (chi["tp"] == tp) :
                        uwires[tp].append(chi[rmstype] * chi[gaintype])
    for tp in ["05", "10", "20", "30"]:
        if len(xwires[tp]) > 0:
            xwires[tp] =[int(np.mean(xwires[tp])), int(np.std(xwires[tp])) ]  
        else:
            xwires[tp]  = None
        if len(vwires[tp]) > 0:
            vwires[tp] =[int(np.mean(vwires[tp])), int(np.std(vwires[tp])) ]  
        else:
            vwires[tp]  = None
        if len(uwires[tp]) > 0:
            uwires[tp] =[int(np.mean(uwires[tp])), int(np.std(uwires[tp])) ]  
        else:
            uwires[tp]  = None
 
    return [xwires, vwires, uwires]


def apa_enctp (orgdicts, gain="250", rmstype="rms", gaintype="fpg_gain") :
    xwires = {"X":"X","05":[],"10":[],"20":[],"30":[]} 
    vwires = {"V":"V","05":[],"10":[],"20":[],"30":[]} 
    uwires = {"U":"U","05":[],"10":[],"20":[],"30":[]} 

    for chi in orgdicts:
        if (chi["gain"] == gain) and (chi["wire"][0] == "X") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    xwires[tp].append(chi[rmstype] * chi[gaintype])
        if (chi["gain"] == gain) and (chi["wire"][0] == "V") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    vwires[tp].append(chi[rmstype] * chi[gaintype])

        if (chi["gain"] == gain) and (chi["wire"][0] == "U") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    uwires[tp].append(chi[rmstype] * chi[gaintype])
    for tp in ["05", "10", "20", "30"]:
        if len(xwires[tp]) > 0:
            xwires[tp] =[int(np.mean(xwires[tp])), int(np.std(xwires[tp])) ]  
        else:
            xwires[tp]  = None
        if len(vwires[tp]) > 0:
            vwires[tp] =[int(np.mean(vwires[tp])), int(np.std(vwires[tp])) ]  
        else:
            vwires[tp]  = None
        if len(uwires[tp]) > 0:
            uwires[tp] =[int(np.mean(uwires[tp])), int(np.std(uwires[tp])) ]  
        else:
            uwires[tp]  = None
    return [xwires, vwires, uwires]

def apa_enctp (orgdicts, gain="250", rmstype="rms", gaintype="fpg_gain") :
    xwires = {"X":"X","05":[],"10":[],"20":[],"30":[]} 
    vwires = {"V":"V","05":[],"10":[],"20":[],"30":[]} 
    uwires = {"U":"U","05":[],"10":[],"20":[],"30":[]} 

    for chi in orgdicts:
        if (chi["gain"] == gain) and (chi["wire"][0] == "X") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    xwires[tp].append(chi[rmstype] * chi[gaintype])
        if (chi["gain"] == gain) and (chi["wire"][0] == "V") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    vwires[tp].append(chi[rmstype] * chi[gaintype])

        if (chi["gain"] == gain) and (chi["wire"][0] == "U") :
            for tp in ["05", "10", "20", "30"]:
                if (chi["tp"] == tp) :
                    uwires[tp].append(chi[rmstype] * chi[gaintype])
    for tp in ["05", "10", "20", "30"]:
        if len(xwires[tp]) > 0:
            xwires[tp] =[int(np.mean(xwires[tp])), int(np.std(xwires[tp])) ]  
        else:
            xwires[tp]  = None
        if len(vwires[tp]) > 0:
            vwires[tp] =[int(np.mean(vwires[tp])), int(np.std(vwires[tp])) ]  
        else:
            vwires[tp]  = None
        if len(uwires[tp]) > 0:
            uwires[tp] =[int(np.mean(uwires[tp])), int(np.std(uwires[tp])) ]  
        else:
            uwires[tp]  = None
    return [xwires, vwires, uwires]


def sub_enctp_plot (ax, encs, title="APA ENC vs. Tp",  label="Gain = 25mV/fC and FPGA-DAC") :
    x = [0.5, 1.0, 2.0, 3.0]
    y = [None, None, None, None]
    e = [None, None, None, None]
    wt = ["X", "V", "U"]
    colors = ['g', 'b', 'r']
    for i in range(len(encs)):
        y[0] = encs[i]["05"][0]
        y[1] = encs[i]["10"][0]
        y[2] = encs[i]["20"][0]
        y[3] = encs[i]["30"][0]
        e[0] = encs[i]["05"][1]
        e[1] = encs[i]["10"][1]
        e[2] = encs[i]["20"][1]
        e[3] = encs[i]["30"][1]

        if (None in y ) and (None in e):
            pass
        else:
            local_label = wt[i] + "wires: "  + label 
            ax.errorbar(x, y, e, label=local_label, color=colors[i])
            for xye in zip(x, y, e):                                   
                #ax.annotate('(%d, %d)' % xye[1:3], xy=xye[0:2], textcoords='data') 
                ax.annotate('(%d, %d)' % xye[1:3], xy=[xye[0], xye[1]+(i+2)*150], textcoords='data', color=colors[i]) 

    ax.legend(loc='best')
    ax.set_xlim([0,4])
    ax.set_xlabel("Peaking time / ($\mu$s)")
    ax.set_ylim([0,2000])
    ax.set_ylabel("ENC /e-")
    ax.set_title(title )
    ax.grid()


def apa_enctp_plot (orgdicts, title="APA ENC vs. Tp", rmstype="sfrms") :
    gs=["250", "140"]
    dacs=["FPGA-DAC", "ASIC-DAC"]
    enc_fpg_25 = apa_enctp (orgdicts, gain=gs[0], rmstype=rmstype, gaintype="fpg_gain") 
    enc_fpg_14 = apa_enctp (orgdicts, gain=gs[1], rmstype=rmstype, gaintype="fpg_gain") 
    enc_asi_25 = apa_enctp (orgdicts, gain=gs[0], rmstype=rmstype, gaintype="asi_gain") 
    enc_asi_14 = apa_enctp (orgdicts, gain=gs[1], rmstype=rmstype, gaintype="asi_gain") 

    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    sub_enctp_plot (ax1, enc_fpg_25, title=title, label="Gain = %smV/fC and"%gs[0] + dacs[0]) 
    sub_enctp_plot (ax2, enc_fpg_14, title=title, label="Gain = %smV/fC and"%gs[1] + dacs[0]) 
    sub_enctp_plot (ax3, enc_asi_25, title=title, label="Gain = %smV/fC and"%gs[0] + dacs[1]) 
    sub_enctp_plot (ax4, enc_asi_14, title=title, label="Gain = %smV/fC and"%gs[1] + dacs[1]) 

    plttitle = "APA noise measurement"    
    fig.suptitle(plttitle)
    
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
#    plt.savefig(pp, format='pdf')
    plt.show()
    plt.close()

def wib_enctp_plot (orgdicts, wibno=0, title="WIB ENC vs. Tp", rmstype="sfrms") :
    gs=["250", "140"]
    dacs=["FPGA-DAC", "ASIC-DAC"]
    enc_fpg_25 = wib_enctp (orgdicts, wibno=wibno, gain=gs[0], rmstype=rmstype, gaintype="fpg_gain") 
    enc_fpg_14 = wib_enctp (orgdicts, wibno=wibno, gain=gs[1], rmstype=rmstype, gaintype="fpg_gain") 
    enc_asi_25 = wib_enctp (orgdicts, wibno=wibno, gain=gs[0], rmstype=rmstype, gaintype="asi_gain") 
    enc_asi_14 = wib_enctp (orgdicts, wibno=wibno, gain=gs[1], rmstype=rmstype, gaintype="asi_gain") 

    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    sub_enctp_plot (ax1, enc_fpg_25, title=title, label="Gain = %smV/fC and"%gs[0] + dacs[0]) 
    sub_enctp_plot (ax2, enc_fpg_14, title=title, label="Gain = %smV/fC and"%gs[1] + dacs[0]) 
    sub_enctp_plot (ax3, enc_asi_25, title=title, label="Gain = %smV/fC and"%gs[0] + dacs[1]) 
    sub_enctp_plot (ax4, enc_asi_14, title=title, label="Gain = %smV/fC and"%gs[1] + dacs[1]) 

    plttitle = "WIB#%d noise measurement"%wibno    
    fig.suptitle(plttitle)
    
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
#    plt.savefig(pp, format='pdf')
    plt.show()
    plt.close()


####    #def apa_sorted_by_wire(orgdicts,title="WIB ENC vs. Tp", rmstype="sfrms") :
####    def apa_sorted_by_wire(orgdicts) :
####        gs=["250", "140"]
####        tps=["05","10","20","30"]
####        #dacs=["FPGA-DAC", "ASIC-DAC"]
####        dacs=["fpgadac_en", "asicdac_en"]
####        for g in gs:
####            for dac in dacs:
####                for tp in tps:
####                    dicts = enctp_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
####                    xdicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
####                    vdicts = enctp_sort_bywire (dicts,  wiretype="V"  ) 
####                    udicts = enctp_sort_bywire (dicts,  wiretype="U"  ) 
####    #                xrms = [chn[rmstype] for chn in xdicts]
####    #                vrms = [chn[rmstype] for chn in vdicts]
####    #                urms = [chn[rmstype] for chn in udicts]
####     
####    #                print np.mean(xrms)
####                    print len(xdicts), len(vdicts), len(udicts)

def apa_sorted_by_wire(orgdicts, g="250", tp="05") :
    dicts = enctp_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V"  ) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U"  ) 
    return xdicts, vdicts, udicts

def femb_sorted_by_wire(orgdicts, g="250", tp="05", wibno=0, fembno=0) :
    dicts = enctp_filter(orgdicts, and_dnf =[["gain",g],  ["tp",tp], ["wib", wibno], ["femb", fembno] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    xdicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
    vdicts = enctp_sort_bywire (dicts,  wiretype="V"  ) 
    udicts = enctp_sort_bywire (dicts,  wiretype="U"  ) 
    print len(xdicts), len(vdicts), len(udicts)
    return xdicts, vdicts, udicts

def find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=0) :
    dicts = enctp_filter(orgdicts, and_dnf =[["wib", wibno], ["femb", fembno], ["fembchn", fembchn] ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    print len(dicts)
    return dicts

#def wib_enctp_plot (orgdicts, wibno=0, title="WIB ENC vs. Tp", rmstype="sfrms") :
def apa_plots (orgdicts, title="APA ENC vs. Tp", rmstype="sfrms", calitype="fpg_gain" ) :
    gs=["250", "140"]
    tps=["05", "10", "20", "30"]
    xenc_tps=[]
    venc_tps=[]
    uenc_tps=[]
    for g in gs:
        for tp in tps:
            xd,vd,ud=apa_sorted_by_wire(orgdicts, g=g, tp=tp) 
            rms_c_plots (xd, title="RMS Compare" ) 
            rms_c_plots (vd, title="RMS Compare" ) 
            rms_c_plots (ud, title="RMS Compare" ) 
            exit()


def draw_results (ax, dicts) :
    wire=[]
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
        wire.append(i)
        rms.append(dicts[i]["rms"])
        hfrms.append(dicts[i]["hfrms"])
        sfrms.append(dicts[i]["sfrms"])
        ped.append(dicts[i]["rms"])
        hfped.append(dicts[i]["hfrms"])
        sfped.append(dicts[i]["sfrms"])
        fpg_gain.append(dicts[i]["fpg_gain"])
        asi_gain.append(dicts[i]["asi_gain"])
        unstk_ratio.append(dicts[i]["unstk_ratio"])
    return wire, rms, hfrms, sfrms, ped, hfped, sfped, fpg_gain, asi_gain, unstk_ratio


def sub_rms_c_plots (ax, dicts ) :
    wire=[]
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
        wire.append(i)
        rms.append(dicts[i]["rms"])
        hfrms.append(dicts[i]["hfrms"])
        sfrms.append(dicts[i]["sfrms"])
        ped.append(dicts[i]["rms"])
        hfped.append(dicts[i]["hfrms"])
        sfped.append(dicts[i]["sfrms"])
        fpg_gain.append(dicts[i]["fpg_gain"])
        asi_gain.append(dicts[i]["asi_gain"])
        unstk_ratio.append(dicts[i]["unstk_ratio"])
    ax.plot(wire, rms)
    ax.scatter(wire, rms)
    ax.plot(wire, hfrms)
    ax.scatter(wire, hfrms)
    ax.plot(wire, sfrms)
    ax.scatter(wire, sfrms)
    ax.grid()

def rms_c_plots (dicts, title="RMS Compare" ) :
    fig = plt.figure(figsize=(16,9))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)

    sub_rms_c_plots (ax1, dicts ) 

#    plttitle = "APA noise measurement"    
#    fig.suptitle(plttitle)
 
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
#    plt.savefig(pp, format='pdf')
    plt.show()
    plt.close()





rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
APAno=4
rmsrunno = "run01rms" #
fpgarunno = "run01fpg" #
asicrunno = "run01asi" #

orgdicts = load_sum (rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno )

apa_sorted_by_wire (orgdicts) 
apa_plots (orgdicts, title="APA ENC vs. Tp", rmstype="sfrms", calitype="fpg_gain" ) 
#femb_sorted_by_wire(orgdicts, g="250", tp="05", wibno=0, fembno=0) 
#find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=0) 

#apa_enctp_plot (orgdicts, title="APA ENC vs. Tp", rmstype="rms") 
#apa_enctp_plot (orgdicts, title="APA ENC vs. Tp", rmstype="sfrms") 
#apa_enctp_plot (orgdicts, title="APA ENC vs. Tp", rmstype="hfrms") 
#
#wib_enctp_plot (orgdicts, wibno=1, title="WIB ENC vs. Tp", rmstype="rms") 
#wib_enctp_plot (orgdicts, wibno=1, title="WIB ENC vs. Tp", rmstype="sfrms") 
#wib_enctp_plot (orgdicts, wibno=1, title="WIB ENC vs. Tp", rmstype="hfrms") 
#dicts = enctp_filter (orgdicts, dnf =[["gain","250"], ["tp","05"], ["femb",0], ["wib",0]] ) 
#dicts = enctp_sort_byfemb (dicts ) 
#for i in dicts:
#    print i["fembchn"]
#
#dicts = enctp_filter (orgdicts, dnf =[["gain","250"], ["tp","05"]] ) 
#dicts = enctp_sort_bywire (dicts,  wiretype="X"  ) 
#print len(dicts)
#print apa_enctp (sumtodict, gain="250", rmstype="rms", gaintype="fpg_gain") 
#print wib_enctp (sumtodict, wibno=0, gain="250", rmstype="rms", gaintype="fpg_gain") 
#print femb_enctp (sumtodict, wibno=0, fembno=0, gain="250", rmstype="rms", gaintype="fpg_gain") 
#print chn_enctp (sumtodict, wibno=0, fembno=0, fembchn=0, gain="250", rmstype="rms", gaintype="fpg_gain") 

#a= sort_enctp_byxuv (sumtodict, APAno="4", wiretype="X"  ) 
#print apa_enctp (a, gain="250", rmstype="rms", gaintype="fpg_gain") 
#sort_enctp_byxuv (sumtodict, APAno="4", wiretype="U"  ) 
#sort_enctp_byxuv (sumtodict, APAno="4", wiretype="V"  ) 

#def enctp_sort_bywib (dicts, wib=["wib", 0] ) :
#    cs_apa_wires = []
#    for loc in range(1, 21, 1):
#        cs_wib_wires = []
#        if (loc <= 10):
#            apaloc = "B" + APAno + format(loc, "02d")
#        else:
#            apaloc = "A" + APAno + format(loc, "02d")
#
#        for chi in dicts:
#            if (chi[wib[0]] == wib[1]) and (chi[femb[0]] == femb[0]):
#                cs_wib_wires.append(chi) 
#        sorted(cs_wib_wires, key=lambda x:x["fembchn"])
#        cs_apa_wires = cs_apa_wires + cs_wib_wires
#    return cs_apa_wires


#def enctp_cs_bygain (dicts, gain="250" ) :
#    cs_apa_wires = []
#    for chi in dicts:
#        if (chi["gain"] == gain) :
#            cs_apa_wires.append(chi)
#    return cs_apa_wires
#
#def enctp_cs_bygain (dicts, tp="05" ) :
#    cs_apa_wires = []
#    for chi in dicts:
#        if (chi["tp"] == gain) :
#            cs_apa_wires.append(chi)
#    return cs_apa_wires
#
#def enctp_filter (dicts, dn = "gain", dv="250" ) :
#    cs_apa_wires = []
#    for chi in dicts:
#        if (chi[dn] == dv) :
#            cs_apa_wires.append(chi)
#    return cs_apa_wires





#def sort_enctp (sumtodict, APAno="4", wiretype="X",  gain="250", tp ="05", rmstype="rms", gaintype="fpg_gain") :
#    APAno="4"
#
#    sort_apa_wires = []
#    for loc in range(1, 21, 1):
#        sort_wib_wires = []
#        if (loc <= 10):
#            apaloc = "B" + APAno + format(loc, "02d")
#        else:
#            apaloc = "A" + APAno + format(loc, "02d")
#
#        for chi in sumtodict:
#            if (chi["gain"] == gain) and (chi["tp"] == tp) and (chi["wire"][0] == wiretype) and (chi["apaloc"] == apaloc):
#                sort_wib_wires.append(chi) 
#        sorted(sort_wib_wires, key=lambda x:x["wire"])
#        sort_apa_wires = sort_apa_wires + sort_wib_wires
#    print len(sort_apa_wires)


#sort_enctp (sumtodict, APAno="4", wiretype="X",  gain="250", tp ="05", rmstype="rms", gaintype="fpg_gain") 
#sort_enctp (sumtodict, APAno="4", wiretype="U",  gain="250", tp ="05", rmstype="rms", gaintype="fpg_gain") 
#sort_enctp (sumtodict, APAno="4", wiretype="V",  gain="250", tp ="05", rmstype="rms", gaintype="fpg_gain") 
#    rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    #rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
#    #ali_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
#    from timeit import default_timer as timer
#    s0= timer()
#    print "Start..., please wait..."
#    APAno=4
#    rmsrunno = "run01rms" #
#    fpgarunno = "run01fpg" #
#    asicrunno = "run01asi" #
#    wibno = 0 #0~4
#    gains = ["250", "140"] 
#    tps = ["05", "10", "20", "30"]
#    jumbo_flag = False
#
#    results_save(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno, gains, tps, jumbo_flag )
#
#
#sshpass -p "Proto_DUNE"  scp -r -P 1145 shanshan@localhost:/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018//results/APA4_run01rms_run01fpg_run01asi/APA4_run01rms_run01fpg_run01asi.allsum Documents/data2
#
#
#def fit_plot(ax, x, y, ped, fit_paras, fit_type = "peak" ):
#    if (fit_paras!= None):
#        slope, constant, peakinl, error_gain = fit_paras
#        if error_gain == False and slope != 0 :
#            ax.set_xlabel("Charge /fC")
#
#            if fit_type == "Peak":
#                label = "Gain = %d (e-/LSB)"%(6250/slope)  + "\n" + "INL = %.3f%%"%(peakinl*100)
#                ax.set_ylabel("ADC code / LSB")
#                y_plot = np.linspace(0,4096)
#                if (min(np.abs(y) ) - ped ) > 0:  #positive pulse
#                    ax.set_xlim([0,(max(x)//10+1)*10])
#                    ax.plot( (y_plot-constant)/slope, y_plot, color = 'b')
#                else: #negative pulse
#                    ax.set_xlim([(max(x)//10+1)*10*(-1), 0])
#                    x = (-1) * x
#                    ax.plot( (constant-y_plot)/slope, y_plot, color = 'b')
#                ax.scatter([0], [ped], marker="s", color = 'k') #pedestal
#                ax.scatter(x, y, marker="o", color = 'r', label=label)
#            elif fit_type == "Area":
#                label = "Gain = %d (e-/(LSB)*(6$\mu$s))"%(6250/slope)  + "\n" + "INL = %.3f%%"%(peakinl*100)
#                if max(np.abs(y) ) == max(y) : 
#                    ax.set_xlim([0,(max(x)//10+1)*10])
#                    y_plot =  np.linspace(0, (max(y)//100 + 1)*100 )
#                    ax.plot( (y_plot-constant)/slope, y_plot, color = 'b')
#                else:
#                    ax.set_xlim([(max(x)//10+1)*10*(-1), 0])
#                    y_plot =  np.linspace((min(y)//100 - 1)*100, 0 )
#                    x = (-1) * x
#                    ax.plot( (constant-y_plot)/slope, y_plot, color = 'b')
#                ax.set_ylabel("Area / (LSB)*(6$\mu$s)")
#                ax.scatter([0], [0], marker="s", color = 'k')
#                ax.scatter(x, y, marker="o", color = 'r', label = label)
# 
#            ax.legend(loc='best')
#            ax.set_title("Linear Fit (%s)"%fit_type)
#            ax.grid()
#
#def cali_linear_fitplot(pp, apainfo, wireinfo, cali_info, chn_cali_paras, ploten=True):
#    vdacs = []
#    ampps  = []
#    ampns  = []
#    areaps = []
#    areans = []
#    fc_daclsb = chn_cali_paras[0][3]
#    ped = chn_cali_paras[0][10]
#
#    for onecp in chn_cali_paras:
#        if (ped >1000): #induction plane
#            if onecp[4] < 3800 : #region inside linearity
#                vdacs.append(onecp[2])
#                ampps.append(onecp[4])
#                ampns.append(onecp[5])
#                areaps.append(onecp[11])
#                areans.append(onecp[12])
#        elif (ped <1000): #induction plane
#            if onecp[4] < 3000 : #region inside linearity
#                vdacs.append(onecp[2])
#                ampps.append(onecp[4])
#                ampns.append(onecp[5])
#                areaps.append(onecp[11])
#                areans.append(onecp[12])
#    fc_dacs = np.array(vdacs) * fc_daclsb
#    
#    if (ped >1000): #induction plane
#        #amplitude, positive pulse
#        ampp_fit = linear_fit(fc_dacs,  ampps )
#        ampn_fit = linear_fit(fc_dacs,  ampns )
#        areap_fit = linear_fit(fc_dacs, areaps)
#        arean_fit = linear_fit(fc_dacs, areans)
#    else:
#        ampp_fit = linear_fit(fc_dacs, ampps)
#        areap_fit = linear_fit(fc_dacs,areaps)
#        ampn_fit =  None
#        arean_fit = None
#
#    if (ploten):
#        fig = plt.figure(figsize=(16,9))
#        ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
#        ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
#        ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
#        ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
#
#        fit_plot(ax1, fc_dacs, ampps , ped, ampp_fit , fit_type = "Peak" )
#        fit_plot(ax2, fc_dacs, ampns , ped, ampn_fit , fit_type = "Peak" )
#        fit_plot(ax3, fc_dacs, areaps, ped, areap_fit, fit_type = "Area" )
#        fit_plot(ax4, fc_dacs, areans, ped, arean_fit, fit_type = "Area" )
#
#        apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
#        wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
#        fe_gain = int(cali_info[0])/10.0
#        fe_tp = int(cali_info[1])/10.0
#        feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, cali_info[2])
#        fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
#        plt.tight_layout( rect=[0, 0.05, 1, 0.95])
#
#        plt.savefig(pp, format='pdf')
#        #plt.show()
#        plt.close()
#
#    if (ampp_fit != None):
#        encperlsb = int(6250/ampp_fit[0])
#        chninl    = ampp_fit[2]
#    else:
#        encperlsb = None
#        chninl    = None
#
#    return  encperlsb,chninl
#
#def cali_wf_subplot(ax, chn_cali_paras, t=100, pulse = "positive", avg_fg = False ):
#    N = int(t/0.5)
#    x = np.arange(N) * 0.5
#    for onecp in chn_cali_paras:
#        if pulse == "positive" :
#            pos = onecp[8]
#        else:
#            pos = onecp[9]
#        if pos >= (N//2):
#            spos= pos-(N//2)
#        else:
#            spos= 0
#        if (avg_fg):
#            y = onecp[7][spos:spos+N]
#            ax.set_title("Waveforms after averaging" )
#        else:
#            y = onecp[6][spos:spos+N]
#            ax.set_title("Waveforms" )
#        ax.scatter(x, y)
#        ax.plot(x, y)
#    ax.set_xlim([0,t])
#    ax.set_ylim([0,4200])
#    ax.grid()
#    ax.set_ylabel("ADC output / LSB")
#    ax.set_xlabel("t / $\mu$s")
#
#def cali_wf_plot(pp, apainfo, wireinfo, cali_info, chn_cali_paras):
#    fig = plt.figure(figsize=(16,9))
#    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
#    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
#    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
#    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
#
#    t = 20
#    cali_wf_subplot(ax1, chn_cali_paras, t=t, pulse="positive", avg_fg = False )
#    cali_wf_subplot(ax2, chn_cali_paras, t=t, pulse="positive", avg_fg = True )
#    cali_wf_subplot(ax3, chn_cali_paras, t=t, pulse="negative", avg_fg = False )
#    cali_wf_subplot(ax4, chn_cali_paras, t=t, pulse="negative", avg_fg = True )
#
#    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
#    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
#    fe_gain = int(cali_info[0])/10.0
#    fe_tp = int(cali_info[1])/10.0
#    feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, cali_info[2])
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
#    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
# 
#    plt.savefig(pp, format='pdf')
#    #plt.show()
#    plt.close()
#
#def ped_wf_subplot(ax, data_slice, ped, rms,  t_rate=0.5, title="Waveforms of raw data", label="Waveform" ):
#    N = len(data_slice)
#    x = np.arange(N) * t_rate
#    y = data_slice
#    ax.scatter(x, y, marker='.', color ='r', label=label)
#    ax.plot(x, y, color ='b')
#   
#    ax.set_title(title )
#    ax.set_xlim([0,int(N*t_rate)])
#    ax.set_ylim([ped-5*(int(rms+1)),ped+5*(int(rms+1))])
#    ax.grid()
#    ax.set_ylabel("ADC output / LSB")
#    ax.set_xlabel("t / $\mu$s")
#    ax.legend(loc='best')
#
#def ped_hg_subplot(ax, data_slice, ped, rms, title="Histogram of raw data", label="Waveform" ):
#    N = len(data_slice)
#    sigma3 = int(rms+1)*3
#    ax.grid()
#    ax.hist(data_slice, normed=1, bins=sigma3*2, range=(ped-sigma3, ped+sigma3),  histtype='bar', label=label, color='b', rwidth=0.9 )
#
#    gaussian_x = np.linspace(ped - 3*rms, ped + 3*rms, 100)
#    gaussian_y = mlab.normpdf(gaussian_x, ped, rms)
#    ax.plot(gaussian_x, gaussian_y, color='r')
#
#    ax.set_title(title + "(%d samples)"%N )
#    ax.set_xlabel("ADC output / LSB")
#    ax.set_ylabel("Normalized counts")
#    ax.legend(loc='best')
#
#
#def ped_wf_plot(pp, apainfo, wireinfo, rms_info, chn_noise_paras):
#    rms =  chn_noise_paras[1]
#    ped =  chn_noise_paras[2]
#    data_slice = chn_noise_paras[3]
#    data_100us_slice = chn_noise_paras[4]
#
#    hfrms =  chn_noise_paras[7]
#    hfped =  chn_noise_paras[8]
#    hfdata_slice = chn_noise_paras[9]
#    hfdata_100us_slice = chn_noise_paras[10]
#
#    sfrms =  chn_noise_paras[13]
#    sfped =  chn_noise_paras[14]
#    unstk_ratio  =  chn_noise_paras[15]
#
#    label = "Rawdata: mean = %d, rms = %2.3f" % (int(ped), rms) + "\n" + \
#            "Stuck Free: mean = %d, rms = %2.3f, unstuck=%%%d" % (int(sfped), sfrms, int(unstk_ratio*100) )
#
#    hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 
#
##waveform
#    fig = plt.figure(figsize=(16,9))
#    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
#    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
#    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
#    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
#    ped_wf_subplot(ax1, data_slice,         ped,   rms,    t_rate=0.5, title="Waveforms of raw data", label=label )
#    ped_wf_subplot(ax2, hfdata_slice,       hfped, hfrms,  t_rate=0.5, title="Waveforms of data after HPF", label=hflabel )
#    ped_wf_subplot(ax3, data_100us_slice,   ped,   rms,    t_rate=100, title="Waveforms of raw data", label=label )
#    ped_wf_subplot(ax4, hfdata_100us_slice, hfped, hfrms,  t_rate=100, title="Waveforms of data after HPF", label=hflabel )
#
#    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
#    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
#    fe_gain = int(rms_info[0])/10.0
#    fe_tp = int(rms_info[1])/10.0
#    feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, rms_info[2])
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
#    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
# 
#    plt.savefig(pp, format='pdf')
#    #plt.show()
#    plt.close()
#
##histogram
#    fig = plt.figure(figsize=(16,9))
#    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=4)
#    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=4)
##    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
##    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
#    ped_hg_subplot(ax1, data_100us_slice, ped, rms, title="Histogram of raw data", label=label )
#    ped_hg_subplot(ax2, hfdata_100us_slice, hfped, hfrms, title="Histogram of data after HPF", label=hflabel )
##    ped_hg_subplot(ax3, data_100us_slice, ped, rms, title="Histogram of raw data", label=label )
##    ped_hg_subplot(ax4, hfdata_100us_slice, hfped, hfrms, title="Histogram of data after HPF", label=hflabel )
# 
#    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
#    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
#    fe_gain = int(rms_info[0])/10.0
#    fe_tp = int(rms_info[1])/10.0
#    feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, rms_info[2])
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
#    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
# 
#    plt.savefig(pp, format='pdf')
#    #plt.show()
#    plt.close()
#
#def ped_fft_subplot(ax, f, p, maxx=1000000,  title="FFT specturm", label="FFT" ):
#    ax.set_title(title )
#    ax.plot(np.array(f)/1000.0,p,color='r', label=label)
#    ax.set_xlim([0,maxx/1000])
#    ax.set_xlabel("Frequency /kHz")
#    ax.grid()
#    psd=True
#    if (psd == True):
#        ax.set_ylabel("Power Spectral Desity /dB")
#        ax.set_ylim([-80,20])
#    else:
#        ax.set_ylabel("Amplitude /dB")
#        ax.set_ylim([-40,20])
#    ax.legend(loc='best')
#
#def ped_fft_plot(pp, apainfo, wireinfo, rms_info, chn_noise_paras):
#    fig = plt.figure(figsize=(16,9))
#    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=2, rowspan=2)
#    ax2 = plt.subplot2grid((4, 4), (0, 2), colspan=2, rowspan=2)
#    ax3 = plt.subplot2grid((4, 4), (2, 0), colspan=2, rowspan=2)
#    ax4 = plt.subplot2grid((4, 4), (2, 2), colspan=2, rowspan=2)
#
#    rms =  chn_noise_paras[1]
#    ped =  chn_noise_paras[2]
#    f = chn_noise_paras[5]
#    p = chn_noise_paras[6]
#
#    hfrms =  chn_noise_paras[7]
#    hfped =  chn_noise_paras[8]
#    hff = chn_noise_paras[11]
#    hfp = chn_noise_paras[12]
#
#    sfrms =  chn_noise_paras[13]
#    sfped =  chn_noise_paras[14]
#    unstk_ratio  =  chn_noise_paras[15]
#
#    label = "Rawdata: mean = %d, rms = %2.3f" % (int(ped), rms) + "\n" + \
#            "Stuck Free: mean = %d, rms = %2.3f, unstuck=%%%d" % (int(sfped), sfrms, int(unstk_ratio*100) )
#
#    hflabel = "After HPF:  mean = %d, rms = %2.3f" % (int(hfped), hfrms) 
# 
#    ped_fft_subplot(ax1, f, p, maxx=1000000, title="Spectrum of raw data", label=label )
#    ped_fft_subplot(ax2, hff, hfp, maxx=1000000, title="Spectrum of data after HPF", label=hflabel )
#    ped_fft_subplot(ax3, f, p, maxx=100000, title="Spectrum of raw data", label=label )
#    ped_fft_subplot(ax4, hff, hfp, maxx=100000, title="Spectrum of data after HPF", label=hflabel )
#  
#    apainfo_str = apainfo[0] + ", " + apainfo[1] + ", " + apainfo[2]  + "  ;  "
#    wireinfo_str = "Wire = " + wireinfo[0] + ", FEMB CHN =" + wireinfo[1] 
#    fe_gain = int(rms_info[0])/10.0
#    fe_tp = int(rms_info[1])/10.0
#    feset_str = "\n Gain = %2.1fmV/fC, Tp = %1.1f$\mu$s; %s"%(fe_gain, fe_tp, rms_info[2])
#    fig.suptitle(apainfo_str + wireinfo_str + feset_str, fontsize = 16)
#    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
# 
#    plt.savefig(pp, format='pdf')
#    #plt.show()
#    plt.close()
#
#def ana_a_chn(out_path, rms_rootpath,  fpga_rootpath, asic_rootpath, APAno = 4, \
#               rmsrunno = "run01rms", fpgarunno = "run01fpg", asicrunno = "run01asi", 
#               wibno=0,  fembno=0, chnno=0, gain="250", tp="20", \
#               jumbo_flag=False, fft_s=5000 ):
#
#    input_info = ["RMS Raw data Path = %s"%rms_rootpath + rmsrunno, 
#                  "Cali(FPGA DAC) Raw data Path = %s"%fpga_rootpath + fpgarunno, 
#                  "Cali(ASIC DAC) Raw data Path = %s"%asic_rootpath + asicrunno, 
#                  "APA#%d"%APAno , 
#                  "WIB#%d"%wibno , 
#                  "Gain = %2.1f mV/fC"% (int(gain)/10.0) , 
#                  "Tp = %1.1f$\mu$s"% (int(tp)/10.0)  ]
#    out_fn = "APA%d"%APAno + "_WIB%d"%wibno + "_FEMB%d"%fembno + "_CHN%d"%chnno + "_Gain%s"%gain + "_Tp%s"%tp+  "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno + ".pdf"
#
#    fp = out_path + out_fn
#    pp = PdfPages(fp)
#    femb_pos_np = femb_position (APAno)
#
#    wibfemb= "WIB"+format(wibno,'02d') + "_" + "FEMB" + format(fembno,'1d') 
#
#    apainfo = None
#    for femb_pos in femb_pos_np:
#        if femb_pos[1] == wibfemb:
#            apainfo = femb_pos
#            break
#
#    apa_map = APA_MAP()
#    All_sort, X_sort, V_sort, U_sort =  apa_map.apa_femb_mapping_pd()
#    wireinfo = None
#    for onewire in All_sort:
#        if (int(onewire[1]) == chnno):
#            wireinfo = onewire
#            break
#
#    feset_info = [gain, tp]
#    rms_info = feset_info + ["RMS"]
#    if (os.path.exists(rms_rootpath + rmsrunno)):
#        rmsdata = read_rawdata(rms_rootpath, rmsrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
#        chn_noise_paras = noise_a_chn(rmsdata, chnno,fft_en = True, fft_s=fft_s, fft_avg_cycle=50)
#        ped_wf_plot(pp, apainfo, wireinfo, rms_info, chn_noise_paras)
#        ped_fft_plot(pp, apainfo, wireinfo, rms_info, chn_noise_paras)
#    else:
#        print "Path: %s%s doesnt' exist, ignore anyway"%(rms_rootpath, rmsrunno)
#
#    fpga_info = feset_info + ["FPGA-DAC Cali"]
#    if (os.path.exists(fpga_rootpath + fpgarunno)):
#        fpgadata = read_rawdata(fpga_rootpath, fpgarunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
#        chn_cali_paras = cali_a_chn(fpgadata, chnno )
#        cali_wf_plot(pp, apainfo, wireinfo, fpga_info, chn_cali_paras)
#        cali_linear_fitplot(pp, apainfo, wireinfo, fpga_info, chn_cali_paras)
#    else:
#        print "Path: %s%s doesnt' exist, ignore anyway"%(fpga_rootpath, fpgarunno)
#
#    asic_info = feset_info + ["ASIC-DAC Cali"]
#    if (os.path.exists(asic_rootpath + asicrunno)):
#        asicdata = read_rawdata(asic_rootpath, asicrunno, wibno,  fembno, chnno, gain, tp, jumbo_flag)
#        chn_cali_paras = cali_a_chn(asicdata, chnno )
#        cali_wf_plot(pp, apainfo, wireinfo, asic_info, chn_cali_paras)
#        cali_linear_fitplot(pp, apainfo, wireinfo, asic_info, chn_cali_paras)
#    else:
#        print "Path: %s%s doesnt' exist, ignore anyway"%(asic_rootpath, asicrunno)
#
#    print "results path: " + fp
#
#
#if __name__ == '__main__':
#    rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#    #rms_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
#    #cali_rootpath = "/Users/shanshangao/Documents/data2/Rawdata_03_21_2018/" 
#    from timeit import default_timer as timer
#    s0= timer()
#    print "Start...please wait..."
#    
#    APAno=4
#    rmsrunno = "run02rms" #
#    fpgarunno = "run01fpg" #
#    asicrunno = "run01asi" #
#    wibno = 0 #0~4
#    fembno = 0 #0~3
#    chnno  = 0 #0~127
#    gains = ["250", "140"] 
#    tps = ["05", "10", "20", "30"]
#    jumbo_flag = False
#    
#    
#    out_path = rms_rootpath + "/" + "results/" + "Chns_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+"/"
#    if (os.path.exists(out_path)):
#        pass
#    else:
#        try: 
#            os.makedirs(out_path)
#        except OSError:
#            print "Can't create a folder, exit"
#            sys.exit()
#    mps = []
#    for gain in gains: 
#        for tp in tps:
#             ana_a_chn_args = (out_path, rms_rootpath, asic_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, wibno, fembno, chnno, gain, tp, jumbo_flag)
#             p = mp.Process(target=ana_a_chn, args=ana_a_chn_args)
#             mps.append(p)
#    for p in mps:
#        p.start()
#    for p in mps:
#        p.join()
#    #        ana_a_chn(rms_rootpath, asic_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, wibno, fembno, chnno, gain, tp, jumbo_flag)
#    print "time passed %d seconds"%(timer() - s0)
#    print "DONE"
#
