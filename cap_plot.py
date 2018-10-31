# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Wed Oct 31 16:17:55 2018
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
import sys
import os.path
import math
import pickle
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab

from apa_plot_out import load_sum
from apa_plot_out import plot0_overall_enc
from apa_plot_out import plot3_overall_gain
from apa_plot_out import plot2_peds
from apa_plot_out import plot1_chns_enc
from apa_plot_out import plot4_chns_gain
from apa_plot_out import dict_filter
from apa_plot_out import find_a_chn
import statsmodels.api as sm

APAno = int(sys.argv[1])
rmsdate = sys.argv[2]
fpgdate = sys.argv[3]
asidate = sys.argv[4]
rmsrunno = sys.argv[5]
fpgarunno = sys.argv[6]
asicrunno = sys.argv[7]
apafolder = sys.argv[8]

if (apafolder == "SBND"):
    rms_rootpath =  "D:/Ledge_Study/Rawdata/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "D:/Ledge_Study/Rawdata/Rawdata_" + fpgdate + "/"
    asic_rootpath = "D:/Ledge_Study/Rawdata/Rawdata_" + asidate + "/"
elif (apafolder == "APA40"):
    rms_rootpath =  "D:/Rawdata/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "D:/Rawdata/Rawdata_" + fpgdate + "/"
    asic_rootpath = "D:/Rawdata/Rawdata_" + asidate + "/"
elif (apafolder != "APA"):
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + asidate + "/"
else:
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
 
#fembs_on_apa = range(1,21, 1) 
fembs_on_apa = range(1,2, 1) 

#sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
sum_path = "/Users/shanshangao/Google_Drive_BNL/tmp/caps/"+ "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/" 
fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno
orgdicts = load_sum (sum_path, fn + ".allsum")


femb_cs = []
for fembloc in fembs_on_apa:
    if (fembloc <= 10):
        femb_cs.append(["apaloc", "B" + format(APAno, "1d") + format(fembloc, "02d")])
    else:
        femb_cs.append(["apaloc", "A" + format(APAno, "1d") + format(fembloc, "02d")])
#asic5 = [151, 154, 100, 105, 51 , 51 , 35 , 37 , 25 , 25 , 53 , 55 , 5  , 5  , 105, 105]
asic5 = [150, 150, 100, 100, 47 , 47 , 33 , 33 , 22 , 22 , 50 , 50 , 0  , 0  , 100, 100]
asic5 = asic5[::-1]
#asic6 = [ 4  , 4  , 4  , 5  , 155, 155, 5  , 5  , 31 , 30 , 4  , 5  , 5  , 5  , 5  , 5]
asic6 = [ 0  , 0  , 0  , 0  , 150, 150, 0  , 0  , 27 , 27 , 0  , 0  , 0  , 0  , 0  , 0]
asic6 = asic6[::-1]
#asic7 = [ 154 , 106 , 150 , 103 , 55  , 37  , 55  , 40  , 30  , 105 , 30  , 56  , 5   , 105 , 5   , 107 ]
asic7 = [ 150 , 100 , 150 , 100 , 47  , 33  , 47  , 33  , 22  , 50 , 22  , 50  , 0   , 100 , 0   , 100 ]
#asic8 = [ 6   , 5   , 6   , 6   , 5   , 157 , 157 , 7   , 5   , 32  , 35  , 7   , 6   , 5   , 6   , 5   ]
asic8 = [ 0   , 0   , 0   , 0   , 0   , 150 , 150 , 0   , 0   , 27  , 27  , 0   , 0   , 0   , 0   , 0   ]

col_chncaps = asic5 + asic6 
#col_chncaps = col_chncaps[0:2] + col_chncaps[16:] 
col_chnnos= np.array(range(len(col_chncaps))) + 64 
#col_chnnos = [64,65] + range(80,96,1)

ind_chncaps = asic7 + asic8 
ind_chnnos= np.array(range(len(ind_chncaps))) + 96 
col_chncaps = ind_chncaps 
col_chnnos = ind_chnnos

col_dicts = []
for chn in range(len(col_chnnos)):
    ads = find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=col_chnnos[chn]) 
    for ad in ads:
        ad["Cd"] = col_chncaps[chn]
        col_dicts.append(ad) 

tp_dicts = dict_filter(col_dicts, and_dnf =[ ["tp", "30"],  ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 

gs = ["250","140","078","047"]
gs_cds = []
gs_encs = []
for g in gs:
    g_dicts = dict_filter(tp_dicts, and_dnf =[ ["gain", g],  ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
    cds = []
    encs = []
    for chndict in g_dicts:
        print chndict["wib"], chndict["femb"],chndict["fembchn"], chndict["gain"], chndict["tp"], int(chndict["rms"]* chndict["fpg_gain"]), chndict["fpg_inl"], chndict["Cd"]
        cds.append(chndict["Cd"]) 
        encs.append(int(chndict["rms"]* chndict["fpg_gain"])) 
    gs_cds.append(cds)
    gs_encs.append(encs)

####cds = gs_cds[3]
####encs = gs_encs[3]
####
####fig = plt.figure(figsize=(16,9))
####cresults = sm.OLS(encs,sm.add_constant(cds)).fit()
####
####cslope = cresults.params[1]
####cconstant = cresults.params[0]
####print cslope, cconstant
####
####plt.scatter(cds, encs)
####plt.plot(cds, np.array(cds)*1.0*cslope+cconstant)
####plt.show()
####plt.close()
#
gstr = ["25.0mV/fC", "14.0mV/fC", " 7.8mV/fC", " 4.7mV/fC"] 
fig = plt.figure(figsize=(12,8))
clor = ['g','b','r','m']
for i in range(4):
    cds = gs_cds[i]
    encs = gs_encs[i]
    x= np.array([0, 22, 27, 33, 47, 50, 100, 150])
    yl= [[], [],[], [], [], [], [], []]
    #x= np.array([0, 27,  50, 100, 150])
    #yl= [[], [], [], [], []]
    for j in range(len(cds)):
        if (cds[j] in x):
            pos = np.where( np.array(x) == cds[j] )[0][0]
            yl[pos].append(encs[j])
    ym = []
    yr = []
    for yt in yl:
        ym.append(np.mean(yt))
        yr.append(np.std(yt))
    
    cresults = sm.OLS(ym,sm.add_constant(x)).fit()
    
    cslope = cresults.params[1]
    cconstant = cresults.params[0]
    print cslope, cconstant
    #plt.scatter(cds, encs)
    label = gstr[i] +  ", Y = (%.2f) * X + (%d)"%(cslope, cconstant)
    plt.errorbar(x, ym, yr, color=clor[i], fmt = "o")
    plt.plot(x, np.array(x)*1.0*cslope+cconstant, c=clor[i], label=label)
    plt.text(x[0], 350+50*i, "%d e$^-$"%(x[0]*1.0*cslope+cconstant),color=clor[i], fontsize = 20 )
    plt.text(80, 50+50*i, "%d e$^-$"%(80*1.0*cslope+cconstant),color=clor[i], fontsize = 20 )
    plt.text(120, 50+50*i, "%d e$^-$"%(120*1.0*cslope+cconstant),color=clor[i], fontsize = 20 )

plt.text(x[0], 350+50*4, "Cd = 0pF", fontsize = 20 )
plt.text(80, 50+50*4, "Cd = 80pF", fontsize = 20 )
plt.text(120, 50+50*4, "Cd = 120pF", fontsize = 20 )

plt.title( "ENC vs. Cd @ (tp =3.0us) ", fontsize = 16 )
plt.ylabel("ENC / e$^-$", fontsize = 16 )
plt.ylim([0,1000])
plt.xlabel("Cd / fC", fontsize = 16 )
plt.xlim([-25, 175])
plt.legend(loc='best', fontsize = 16)
plt.tick_params(labelsize=16)
plt.grid()
plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#plt.show()
plt.savefig("/Users/shanshangao/Google_Drive_BNL/tmp/caps/" + fn + "_LN_ind_30us_.png",format='png')
plt.close()
#
#ind_chncaps = asic7 + asic8 
#ind_chnnos= np.array(range(len(ind_chncaps))) + 96 







#orgdicts = dict_filter (orgdicts, or_dnf =femb_cs, and_flg=False  ) 
#
fp = sum_path + fn + ".pdf" 
pp = PdfPages(fp)
print "start...wait a few minutes..."
#chndicts = find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=78) 
#print len(chndicts)
#dicts = dict_filter(chndicts, and_dnf =[["gain", "250"], ["tp", "20"],  ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 
#dicts = dict_filter(chndicts, and_dnf =[ ["tp", "20"],  ], or_dnf = [["fpgadac_en", True], ["asicdac_en", True]] ) 

#for chndict in dicts:
#    print chndict["wib"], chndict["femb"],chndict["fembchn"], chndict["gain"], chndict["tp"], int(chndict["rms"]* chndict["fpg_gain"]), chndict["fpg_inl"]

#for chn in chnnos:
#    chndicts = find_a_chn(orgdicts, wibno=0, fembno=0, fembchn=78) 








#plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "hf" ) 
#plot3_overall_gain (pp, orgdicts, title="APA Gain Measurement" ) 
#
#plot2_peds (pp, orgdicts,title="Pedestals", g="250", tp="20"  , fembs_on_apa = fembs_on_apa) 
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution",  cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution",  cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution",  cali_cs="fpg_gain", rms_cs = "rms",   g="078", fembs_on_apa = fembs_on_apa )  #
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution",  cali_cs="fpg_gain", rms_cs = "rms",   g="047", fembs_on_apa = fembs_on_apa )  #
#plot4_chns_gain (pp, orgdicts, title="Gain Distribution",  g="250" , fembs_on_apa = fembs_on_apa)  #
#plot4_chns_gain (pp, orgdicts, title="Gain Distribution",  g="140" , fembs_on_apa = fembs_on_apa)  #
#plot4_chns_gain (pp, orgdicts, title="Gain Distribution",  g="078" , fembs_on_apa = fembs_on_apa)  #
#plot4_chns_gain (pp, orgdicts, title="Gain Distribution",  g="047" , fembs_on_apa = fembs_on_apa)  #
##plot2_peds (pp, orgdicts,title="Pedestals", g="250", tp="20"  , fembs_on_apa = fembs_on_apa) 
##print "please wait a few minutes..."
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
#plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="250" , fembs_on_apa = fembs_on_apa)  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="250" , fembs_on_apa = fembs_on_apa)  #
##
##print "please wait a few minutes..."
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="140" , fembs_on_apa = fembs_on_apa)  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="140" , fembs_on_apa = fembs_on_apa)  #
##
##print "please wait a few minutes..."
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="078", fembs_on_apa = fembs_on_apa )  #
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="078", fembs_on_apa = fembs_on_apa )  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="078" , fembs_on_apa = fembs_on_apa)  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="078" , fembs_on_apa = fembs_on_apa)  #
##
##print "please wait a few minutes..."
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="047", fembs_on_apa = fembs_on_apa )  #
##plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="047", fembs_on_apa = fembs_on_apa )  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="047" , fembs_on_apa = fembs_on_apa)  #
##plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="047" , fembs_on_apa = fembs_on_apa)  #

#print "please wait a few minutes..."
#plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="asi_gain", sfhf = "sf" ) 
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #

pp.close()

print "Done"

