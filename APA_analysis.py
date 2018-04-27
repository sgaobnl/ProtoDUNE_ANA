# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/27/2018 6:36:00 PM
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
import multiprocessing as mp
import time
import pickle
from femb_position import femb_position
from apa_mapping   import APA_MAP
from chn_analysis  import read_rawdata 
from chn_analysis  import noise_a_chn 
from chn_analysis  import cali_a_chn 
from chn_analysis  import cali_linear_calc 
from chn_analysis  import generate_rawpaths
from multiprocessing import Pipe
import multiprocessing as wib_mp

def ana_a_apa(rmsdatas, fpgadatas, asicdatas, dac_type="FPGADAC" APAno = 4, gain="250", tp="05", sum_chn=512, apa="ProtoDUNE"):

    femb_pos_np = femb_position (APAno)
    apa_results = []
    for apachn in range(sum_chn):
        wibno = apachn//512
        fembno = (apachn%512)//128
        fembchn = (apachn%512)%128
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
        chn_noise_paras = noise_a_chn(rmsdata, apachn, fft_en = False)
        rms          =  chn_noise_paras[1]
        ped          =  chn_noise_paras[2]
        hfrms        =  chn_noise_paras[7]
        hfped        =  chn_noise_paras[8]
        sfrms        =  chn_noise_paras[13]
        sfped        =  chn_noise_paras[14]
        unstk_ratio  =  chn_noise_paras[15]

        fpg_cali_flg = False 
        asi_cali_flg = False 
        if (dac_type == "FPGADAC"):
            fpg_cali_flg = True
            chn_fpga_paras = cali_a_chn(fpgadatas, apachn )
            fpg_encperlsb, fpg_chninl = cali_linear_calc(chn_fpga_paras)
        elif (dac_type == "ASICDAC"):
            asi_cali_flg = True
            chn_asic_paras = cali_a_chn(asicdatas, apachn )
            asi_encperlsb, asi_chninl = cali_linear_calc(chn_asic_paras)
        elif (dac_type == "BOTHDAC"):
            fpg_cali_flg = True
            asi_cali_flg = True
            chn_fpga_paras = cali_a_chn(fpgadatas, apachn )
            fpg_encperlsb, fpg_chninl = cali_linear_calc(chn_fpga_paras)
            chn_asic_paras = cali_a_chn(asicdatas, apachn )
            asi_encperlsb, asi_chninl = cali_linear_calc(chn_asic_paras)
            

        apa_results.append([apainfo, wireinfo, feset_info, wibno, fembno, fembchn, rms ,ped ,hfrms ,hfped ,sfrms ,sfped, \
                         unstk_ratio, fpg_cali_flg, fpg_encperlsb, fpg_chninl, asi_cali_flg, asi_encperlsb, asi_chninl])



def results_save(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno, gains, tp, sum_chn=512, apa="ProtoDUNE" ):
    for gain in gains: 
        for tp in tps:
            print gain, tp
            print "Gain = %2.1f mV/fC, "% (int(gain)/10.0) +  "Tp = %1.1fus"% (int(tp)/10.0) 
            datas = felix_read_rawdata_all(rootpath, runno = runno,  gain=gain, tp=tp, sum_chn = sum_chn )
            #ana_a_apa(rms_rootpath, fpga_rootpath, asic_rootpath, APAno, rmsrunno, fpgarunno, asicrunno, gain, tp, jumbo_flag, apa)
            print "time passed %d seconds"%(timer() - s0)

    sum_path = rms_rootpath + "/" + "results/" + "APA%d_"%APAno + rmsrunno + "_" + fpgarunno + "_" + asicrunno +"/"
    print sum_path
   
    if (os.path.exists(sum_path)):
        for root, dirs, files in os.walk(sum_path):
            break

    sumfiles = []
    for afile in files:
        if afile.find(".sum") == (len(afile)-4) :
           sumfiles.append(afile)

    dict_chn = {"rmspath": None, "fpgapath": None, "calipath": None, "apaloc":None, "wib":None, "femb":None, "cebox":None, "wire":None, 
                "fembchn":None, "gain":None, "tp":None, "ped":None, "rms":None, "hfped":None, "hfrms":None, "sfped":None, "sfrms":None, 
                "unstk_ratio":None, "fpgadac_en":None, "fpg_gain":None, "fpg_inl":None, "asicdac_en":None, "asi_gain":None, "asi_inl":None }
 
    sumtodict = []
    if (len(files) > 0 ):
        for sumfile in sumfiles:
            with open (sum_path+sumfile, 'rb') as fp:
                fsum = pickle.load(fp)
                info = fsum[0]
                for femb_rec in fsum[1]:
                    for asic_rec in femb_rec :
                        for chn_rec in asic_rec:
                            newdict = dict_chn.copy()
                            newdict["rmspath"]      =  info[0]               
                            newdict["fpgapath"]     =  info[1]           
                            newdict["calipath"]     =  info[2]          
                            newdict["apaloc"]       =  chn_rec[0][0]        
                            newdict["wib"]          =  chn_rec[3]          
                            newdict["femb"]         =  chn_rec[4]            
                            newdict["cebox"]        =  chn_rec[0][2]            
                            newdict["wire"]         =  chn_rec[1][0]           
                            newdict["fembchn"]      =  chn_rec[5]             
                            newdict["gain"]         =  chn_rec[2][0]          
                            newdict["tp"]           =  chn_rec[2][1]           
                            newdict["rms"]          =  chn_rec[6]            
                            newdict["ped"]          =  chn_rec[7]           
                            newdict["hfrms"]        =  chn_rec[8]              
                            newdict["hfped"]        =  chn_rec[9]              
                            newdict["sfrms"]        =  chn_rec[10]              
                            newdict["sfped"]        =  chn_rec[11]              
                            newdict["unstk_ratio"]  =  chn_rec[12]                    
                            newdict["fpgadac_en"]   =  chn_rec[13]                   
                            newdict["fpg_gain"]     =  chn_rec[14]                 
                            newdict["fpg_inl"]      =  chn_rec[15]                
                            newdict["asicdac_en"]   =  chn_rec[16]                   
                            newdict["asi_gain"]     =  chn_rec[17]                 
                            newdict["asi_inl"]      =  chn_rec[18]                
                            sumtodict.append(newdict)
#            os.remove(sum_path+sumfile)

    out_fn = "APA%d"%APAno + "_" + rmsrunno + "_" + fpgarunno + "_" + asicrunno+ ".allsum"
    fp = sum_path + out_fn
    print fp
#    if (os.path.isfile(fp)): 
#        os.remove(fp)
    with open(fp, "wb") as fp:
        pickle.dump(sumtodict, fp)

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

    if (apafolder == "FELIX"):
        rms_rootpath =  "E:/Data_FELIX/"
        fpga_rootpath = "E:/Data_FELIX/"
        asic_rootpath = "E:/Data_FELIX/"
        #apa = "APA40"
        apa = "ProtoDUNE"
    elif (apafolder == "APA40"):
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
        apa = "ProtoDUNE"
    from timeit import default_timer as timer
    s0= timer()
    print "Start..., please wait..."
    gains = ["250"] 
    #gains = ["250", "140"] 
    tps = [ "10",]
    #tps = ["05", "10", "20", "30"]

    results_save(rms_rootpath, fpga_rootpath, asic_rootpath,  APAno, rmsrunno, fpgarunno, asicrunno, gains, tps, jumbo_flag, apa )

    print "Done, please punch \"Eneter\" or \"return\" if necessary! "

 


