# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sun Apr  1 20:49:48 2018
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
import pickle

rms_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
fpga_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
asic_rootpath = "/nfs/rscratch/bnl_ce/shanshan/Rawdata/Coldbox/Rawdata_03_21_2018/"
#rms_rootpath =  "/Users/shanshangao/Documents/data2/"
#fpga_rootpath = "/Users/shanshangao/Documents/data2/"
#asic_rootpath = "/Users/shanshangao/Documents/data2/"

APAno=4
rmsrunno = "run02rms" #
fpgarunno = "run01fpg" #
asicrunno = "run01asi" #

sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno
orgdicts = load_sum (sum_path, fn + ".allsum")

fp = sum_path + fn + ".pdf" 
pp = PdfPages(fp)
plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "sf" ) 
plot0_overall_enc (pp, orgdicts, title="APA ENC vs. Tp", calitype="fpg_gain", sfhf = "hf" ) 
plot3_overall_gain (pp, orgdicts, title="APA Gain Measurement" ) 
plot2_peds (pp, orgdicts,title="Pedestals", g="250", tp="20" ) 
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "rms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "rms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "rms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "sfrms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "X", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "V", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
plot1_chns_enc (pp, orgdicts, title="APA ENC Distribution", wiretype = "U", cali_cs="fpg_gain", rms_cs = "hfrms", g="250" )  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="X", g="250" )  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="V", g="250" )  #
plot4_chns_gain (pp, orgdicts, title="Gain Distribution", wiretype="U", g="250" )  #
pp.close()


