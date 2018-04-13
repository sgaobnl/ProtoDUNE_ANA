# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Thu Apr 12 23:53:33 2018
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
import sys
import os.path
import math
import pickle
from matplotlib.backends.backend_pdf import PdfPages

from apa_plot_out import load_sum
from apa_plot_out import plot0_overall_enc
from apa_plot_out import plot3_overall_gain
from apa_plot_out import plot2_peds
from apa_plot_out import plot1_chns_enc
from apa_plot_out import plot4_chns_gain
from apa_plot_out import dict_filter

APAno = sys.argv[1]
rmsdate = sys.argv[2]
fpgdate = sys.argv[3]
asidate = sys.argv[4]
rmsrunno = sys.argv[5]
fpgarunno = sys.argv[6]
asicrunno = sys.argv[7]
apafolder = sys.argv[8]

if (apafolder != "APA"):
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + asidate + "/"
else:
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
 
fembs_on_apa = range(1,21, 1) 

sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno
orgdicts = load_sum (sum_path, fn + ".allsum")


femb_cs = []
for fembloc in fembs_on_apa:
    if (fembloc <= 10):
        femb_cs.append(["apaloc", "B" + format(APAno, "1d") + format(fembloc, "02d")])
    else:
        femb_cs.append(["apaloc", "A" + format(APAno, "1d") + format(fembloc, "02d")])

if APAno == 3:
    femb_cs.remove(["apaloc","A308"])  #APA3 B308 has broken FE ASIC
#if APAno == 4: #only at RT
#    femb_cs.remove(["apaloc","B409"])  #APA3 B308 has broken FE ASIC
#    femb_cs.remove(["apaloc","A420"])  #APA3 B308 has broken FE ASIC

orgdicts = dict_filter (orgdicts, or_dnf =femb_cs, and_flg=False  ) 

fp = sum_path + fn + ".pdf" 
pp = PdfPages(fp)
print "start...wait a few minutes..."
plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "hf" ) 
plot3_overall_gain (pp, orgdicts, title="APA Gain Measurement" ) 
plot2_peds (pp, orgdicts,title="Pedestals", g="250", tp="20"  , fembs_on_apa = fembs_on_apa) 
print "please wait a few minutes..."
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="250", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "hfrms", g="250", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "hfrms", g="250", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "hfrms", g="250", fembs_on_apa = fembs_on_apa )  #
print "please wait a few minutes..."
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="250" , fembs_on_apa = fembs_on_apa)  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="V", g="250" , fembs_on_apa = fembs_on_apa)  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="250" , fembs_on_apa = fembs_on_apa)  #

#print "please wait a few minutes..."
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="140", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "hfrms", g="140", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "hfrms", g="140", fembs_on_apa = fembs_on_apa )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "hfrms", g="140", fembs_on_apa = fembs_on_apa )  #
print "please wait a few minutes..."
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="140" , fembs_on_apa = fembs_on_apa)  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="V", g="140" , fembs_on_apa = fembs_on_apa)  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="140" , fembs_on_apa = fembs_on_apa)  #

#print "please wait a few minutes..."
#plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="asi_gain", sfhf = "sf" ) 
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="250", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #
#plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="140", fembs_on_apa = fembs_on_apa )  #

pp.close()

print fp 
print "Done"

