# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sat Jun  9 20:51:55 2018
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

from apa_plot_out import APA_PLOT

apaplt = APA_PLOT()
apaplt.fembs_on_apa = range(1,5,1)

APAno = int(sys.argv[1])
rmsdate = sys.argv[2]
fpgdate = sys.argv[3]
asidate = sys.argv[4]
rmsrunno = sys.argv[5]
fpgarunno = sys.argv[6]
asicrunno = sys.argv[7]
apafolder = sys.argv[8] 

if (apafolder == "APA40"):
    rms_rootpath =  "D:/APA40/Rawdata/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "D:/APA40/Rawdata/Rawdata_" + fpgdate + "/"
    asic_rootpath = "D:/APA40/Rawdata/Rawdata_" + asidate + "/"
    apaplt.apa = "APA40"
    apaplt.femb_xuv = [56,36,36] 
    apaplt.fembs_on_apa = range(1,5,1)
elif (apafolder != "APA"):
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_" + asidate + "/"
    apaplt.apa = "ProtoDUNE"
    apaplt.femb_xuv = [48,40,40] 
    apaplt.fembs_on_apa = range(1,21,1)
else:
    rms_rootpath =  "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + rmsdate + "/"
    fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + fpgdate + "/"
    asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA%d/Rawdata_"%APAno + asidate + "/"
    apaplt.apa = "ProtoDUNE"
    apaplt.femb_xuv = [48,40,40] 
    apaplt.fembs_on_apa = range(1,21,1)

 
sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno
orgdicts = apaplt.load_sum (sum_path, fn + ".allsum")

if  (apafolder == "APA40"):
    bad_wib_fembchns0 = [ [0, 1, 48],  [0, 2, 126], [0, 2, 124]]  # short together
    bad_wib_fembchns1 = [ [0, 2, 127], [0, 3, 48], [0, 3, 50]]  # open wire
    orgdicts = apaplt.del_bads(orgdicts, bad_wib_fembchns0)
    orgdicts = apaplt.del_bads(orgdicts, bad_wib_fembchns1)

femb_cs = []
for fembloc in apaplt.fembs_on_apa:
    if (fembloc <= 10):
        femb_cs.append(["apaloc", "B" + format(APAno, "1d") + format(fembloc, "02d")])
    else:
        femb_cs.append(["apaloc", "A" + format(APAno, "1d") + format(fembloc, "02d")])

if APAno == 3:
    femb_cs.remove(["apaloc","A308"])  #APA3 B308 has broken FE ASIC
#if APAno == 4: #only at RT
#    femb_cs.remove(["apaloc","B409"])  #APA3 B308 has broken FE ASIC
#    femb_cs.remove(["apaloc","A420"])  #APA3 B308 has broken FE ASIC

orgdicts = apaplt.dict_filter (orgdicts, or_dnf =femb_cs, and_flg=False  ) 
#gs =["250"]
gs =["250","140"]
tps=["05", "10", "20", "30"] 
fp = sum_path + fn + ".pdf" 
pp = PdfPages(fp)
print "start...wait a few minutes..."
apaplt.plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "hf", gs=gs, tps=tps ) 
apaplt.plot3_overall_gain (pp, orgdicts, title="APA Gain Measurement", gs=gs, tps=tps  ) 
apaplt.plot2_peds (pp, orgdicts,title="Pedestals", g="250", tp="20"   ) 
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="250" )  #
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "rms",   g="250" )  #
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="250" )  #
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
print "please wait a few minutes..."
apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
print "please wait a few minutes..."
apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="250" )  #
print "please wait a few minutes..."
apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="V", g="250" )  #
print "please wait a few minutes..."
apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="250" )  #
#
##print "please wait a few minutes..."
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms",   g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "rms",   g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms",   g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "hfrms", g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "hfrms", g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "hfrms", g="140" )  #
#print "please wait a few minutes..."
#apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="140" )  #
#apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="V", g="140" )  #
#apaplt.plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="140" )  #

#print "please wait a few minutes..."
#apaplt.plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="asi_gain", sfhf = "sf" ) 
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="140" )  #
#apaplt.plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="140" )  #

pp.close()

print fp 
print "Done"

