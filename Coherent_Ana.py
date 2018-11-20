# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Mon Nov  5 21:25:50 2018
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
import copy
import sys


rpath = "/Users/shanshangao/tmp/Rawdata_08_22_2018/"
gcsv = "run01fpg_fpga_cali.csv"
rcsv = "run51dat_ASICrms.csv"

gs = []
with open(rpath + gcsv, 'r') as fp:
    for cl in fp:
        tmp = cl.split(",")
        x = []
        for i in tmp:
            x.append(i.replace(" ", ""))
        x = x[:-1]
        gs.append(x)
gs_title = gs[0]
gs = gs[1:]

rs = []
with open(rpath + rcsv, 'r') as fp:
    for cl in fp:
        tmp = cl.split(",")
        x = []
        for i in tmp:
            x.append(i.replace(" ", ""))
        x = x[:-1]
        rs.append(x)
rs_title = rs[0]
rs = rs[1:]
print len(rs)

grs = [] 
for r in rs:
    wibno = int(r[1])
    fembno = int(r[2])
    chnno = int(r[3])*16 + int(r[4])
    chngrs = []
    for g in gs:
        if (int(g[0]) == wibno) and (int(g[1]) == fembno) and (int(g[2]) == chnno) :
            chngrs.append( r[0] )
            chngrs.append( int(r[1]) ) #wibno
            chngrs.append( int(r[2]) ) #fembno
            chngrs.append( int(r[3]) ) #asicno
            chngrs.append( int(r[4]) ) #chnno
            chngrs.append( float(r[5]) ) #raw rms
            chngrs.append( float(r[6]) ) #coh rms
            chngrs.append( float(r[7]) ) #post rms
            if float(g[3]) > 300 or float(g[3]) < 100 :
                if r[0][0] == "X":
                    egain = 245
                else:
                    egain = 225
                einl = 0
                eflag = False
            else:
                egain =float(g[3]) 
                einl = float(g[4])
                eflag = True
            chngrs.append( egain ) #egain
            chngrs.append( einl ) #egain inl
            chngrs.append( eflag ) #egain inl
            chngrs.append( int(egain * float(r[5])) ) #raw rms
            chngrs.append( int(egain * float(r[6])) ) #coh rms
            chngrs.append( int(egain * float(r[7])) ) #post rms
            break
    grs.append(chngrs) 



open_inds = []
inds = []
open_cols = []
cols  = []
c150s = []
c100s = []
c050s = []
c027s = []
bads = []
print len(grs)
for gr in grs:
    if (gr[0][0] == "V") and (gr[1] == 1) and (gr[2] == 0) and (gr[3] in [0,1,4,5,7]) and (gr[10]==True):
        open_inds.append(gr)
    if (gr[0][0] == "U") and (gr[10]==True):
        inds.append(gr)
    if (gr[0][0] == "V") and (gr[1] == 0) and (gr[2] == 0) and (gr[3] in [0,1,4,5,7]) and (gr[10]==True):
        open_cols.append(gr)
    if (gr[0][0] == "X") and (gr[10]==True):
        cols.append(gr)
    if (gr[0] == "C150") and (gr[10]==True):
        c150s.append(gr)
    if (gr[0] == "C100") and (gr[10]==True):
        c100s.append(gr)
    if (gr[0] == "C050") and (gr[10]==True):
        c050s.append(gr)
    if (gr[0] == "C027") and (gr[10]==True):
        c027s.append(gr)
    if (gr[10]==False):
        bads.append(gr)

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import statsmodels.api as sm

inds = sorted(inds, key= lambda i : int(i[0][1:]))
cols = sorted(cols, key= lambda i : int(i[0][1:]))


#for y in c150s:
#    print y
#for y in c100s:
#    print y
#for y in c050s:
#    print y
#for y in c027s:
#    print y
#
#for y in bads:
#    print y

ss = [open_inds, inds, open_cols,cols, c150s, c100s, c050s, c027s, bads]
ts = ["Unused U", "U Plane", "Unused X", "X Plane", "150pF X", "100pF X", "50pF X", "27pF X", "Bad"] 


####    fig = plt.figure(figsize=(16,8))
####    i = 0
####    for si in range(4):
####        ccs = ss[si]
####        print len(ccs)
####        plt.vlines(i, 0, 800, color='b', linestyles="dotted", linewidth=0.8)
####        x = []
####        y1 = []
####        y2 = []
####        y3 = []
####        for cs in ccs:
####            x.append(i)
####            y1.append(cs[5])
####            y2.append(cs[6])
####            y3.append(cs[7])
####            #plt.scatter([i], [cs[11]], marker="^", color = "C" + str(cs[3]))
####            #plt.scatter([i], [cs[12]], marker="o", color = "C" + str(cs[3]))
####            #plt.scatter([i], [cs[13]], marker="*", color = "C" + str(cs[3]))
####            i = i + 1
####        plt.plot(x, y1, color = "r" )
####        plt.plot(x, y2, color = "c" )
####        plt.plot(x, y3, color = "g" )
####        plt.text((i-len(x)/2-30), 4.5, ts[si], fontsize = 20)
####        plt.text((i-len(x)/2-30), 4, format(np.mean(y1), ".3f") + "$\pm$" + format(np.std(y1), ".3f") + " bin", color = 'r', fontsize = 20)
####        plt.text((i-len(x)/2-30), 3.5, format(np.mean(y3), ".3f") + "$\pm$" + format(np.std(y3), ".3f") + " bin", color = 'g', fontsize = 20)
####    
####    plt.title("Noise Performance", fontsize = 24 )
####    plt.ylabel("RMS / bin", fontsize = 20 )
####    plt.xlabel("Channel No. ", fontsize = 20 )
####    plt.xlim([0,640])
####    plt.ylim([0,5])
####    plt.tick_params(labelsize=20)
####    plt.grid(axis="y")
####    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
####    plt.savefig(rpath + "/run51dat_rms_performance1.png")
#plt.show()
#
#fig = plt.figure(figsize=(16,8))
#i = 0
#for si in range(4):
#    ccs = ss[si]
#    print len(ccs)
#    plt.vlines(i, 0, 800, color='b', linestyles="dotted", linewidth=0.8)
#    x = []
#    y1 = []
#    y2 = []
#    y3 = []
#    for cs in ccs:
#        x.append(i)
#        y1.append(cs[11])
#        y2.append(cs[12])
#        y3.append(cs[13])
#        #plt.scatter([i], [cs[11]], marker="^", color = "C" + str(cs[3]))
#        #plt.scatter([i], [cs[12]], marker="o", color = "C" + str(cs[3]))
#        #plt.scatter([i], [cs[13]], marker="*", color = "C" + str(cs[3]))
#        i = i + 1
#    plt.plot(x, y1, color = "r" )
#    plt.plot(x, y2, color = "c" )
#    plt.plot(x, y3, color = "g" )
#    plt.text((i-len(x)/2-30), 750, ts[si], fontsize = 20)
#    plt.text((i-len(x)/2-30), 700, str(int(np.mean(y1))) + "$\pm$" + str(int(np.std(y1))) + " e$^-$", color = 'r', fontsize = 20)
#    plt.text((i-len(x)/2-30), 650, str(int(np.mean(y3))) + "$\pm$" + str(int(np.std(y3))) + " e$^-$", color = 'g', fontsize = 20)
#
#plt.title("Noise Performance", fontsize = 24 )
#plt.ylabel("ENC / e$^-$", fontsize = 20 )
#plt.xlabel("Channel No. ", fontsize = 20 )
#plt.xlim([0,640])
#plt.ylim([0,800])
#plt.tick_params(labelsize=20)
#plt.grid(axis="y")
#plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#plt.savefig(rpath + "/run51dat_noise_performance1.png")
##plt.show()
#
#fig = plt.figure(figsize=(16,8))
#i = 0
#for si in range(4,8):
#    ccs = ss[si]
#    print len(ccs)
#    plt.vlines(i, 0, 800, color='b', linestyles="dotted", linewidth=0.8)
#    x = []
#    y1 = []
#    y2 = []
#    y3 = []
#    for cs in ccs:
#        x.append(i)
#        y1.append(cs[11])
#        y2.append(cs[12])
#        y3.append(cs[13])
#        plt.scatter([i], [cs[11]], marker="^", color = "C" + str(cs[3]))
#        plt.scatter([i], [cs[12]], marker="o", color = "C" + str(cs[3]))
#        plt.scatter([i], [cs[13]], marker="*", color = "C" + str(cs[3]))
#        i = i + 1
#    plt.plot(x, y1, color = "r" )
#    plt.plot(x, y2, color = "c" )
#    plt.plot(x, y3, color = "g" )
#    plt.text((i-3), 125, ts[si], fontsize = 20)
#    plt.text((i-3), 75, str(int(np.mean(y1))) + "$\pm$" + str(int(np.std(y1))) + " e$^-$", color = 'r', fontsize = 20)
#    plt.text((i-3), 25, str(int(np.mean(y3))) + "$\pm$" + str(int(np.std(y3))) + " e$^-$", color = 'g', fontsize = 20)
#
#plt.title("Noise Performance", fontsize = 24 )
#plt.ylabel("ENC / e$^-$", fontsize = 20 )
#plt.xlabel("Channel No. ", fontsize = 20 )
#plt.xlim([-1,15])
#plt.ylim([0,800])
#plt.tick_params(labelsize=20)
#plt.grid(axis="y")
#plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#plt.savefig(rpath + "/run51dat_noise_performance2.png")
#plt.show()


#fig = plt.figure(figsize=(16,8))
#i = 0
#for si in range(4):
#    ccs = ss[si]
#    print len(ccs)
#    plt.vlines(i, 0, 800, color='b', linestyles="dotted", linewidth=0.8)
#    x = []
#    y1 = []
#    for cs in ccs:
#        x.append(i)
#        y1.append(cs[8])
#        i = i + 1
#    plt.plot(x, y1, color = "b" )
#    plt.text((i-len(x)/2-30), 750, ts[si], fontsize = 20)
#    plt.text((i-len(x)/2-30), 700, str(int(np.mean(y1))) + "$\pm$" + str(int(np.std(y1))) + " e$^-$", color = 'r', fontsize = 20)
#
#plt.title("Inverted Gain Performance", fontsize = 24 )
#plt.ylabel("Inverted Gain / e$^-$/bin", fontsize = 20 )
#plt.xlabel("Channel No. ", fontsize = 20 )
#plt.xlim([0,640])
#plt.ylim([0,800])
#plt.tick_params(labelsize=20)
#plt.grid(axis="y")
#plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#plt.savefig(rpath + "/run51dat_gain_performance1.png")
##plt.show()



fcss = ["0pF U", "0.45m U", "0pF X", "0.45m X", "150pF X", "100pF X", "50pF X", "27pF X", "Bad"] 
fcs = [0, 0.45*18.1, 0, 0.45*18.1, 150, 100, 50, 27]

fig = plt.figure(figsize=(16,8))
i = 0
yms1 = []
yss1 = []
yss3 = []
yms3 = []
for si in range(8):
    ccs = ss[si]
    x = []
    y1 = []
    y3 = []
    for cs in ccs:
        x.append(i)
        y1.append(cs[11])
        y3.append(cs[13])
        i = i + 1
    yms1.append(np.mean(y1))
    yss1.append(np.std(y1))
    yms3.append(np.mean(y3))
    yss3.append(np.std(y3))
ws = np.array(fcs)/18.1
#plt.errorbar(ws, yms1, yss1, label= "VST Raw Data", color='r', fmt='x')
#plt.errorbar(ws[0:4], yms1[0:4], yss1[0:4], label= "VST Raw Data", color='r', fmt='x')
#plt.errorbar(ws[0:4], yms3[0:4], yss3[0:4], label= "VST Filtered Data", color='g', fmt='o')
plt.errorbar([ws[1],ws[3]], [yms3[1],yms3[3]], [yss3[1],yss3[3]], label= "VST Filtered Data", color='g', fmt='o')

yt = yms1
yt = np.delete(yt, [4])
wt = ws
wt = np.delete(wt, [4])

y1r = sm.OLS(yt, sm.add_constant(wt)).fit()
y1r_a= y1r.params[1]
y1r_b = y1r.params[0]
#plt.plot(ws, ws*y1r_a+y1r_b, label= "VST Raw Data (Fit)", color='r')

#y3r = sm.OLS(yms3,sm.add_constant(ws)).fit()
#y3r_a= y3r.params[1]
#y3r_b = y3r.params[0]
#plt.plot(ws, ws*y3r_a+y3r_b, label= "VST Filtered Data (Fit)", color='g')

bnlc = [  0,  22 , 27 , 33 , 47 , 50 ,100 ,150]
bnle =[207.0, 246.0, 241.5, 269.5, 298.5, 300.0, 411.0, 515.0]
bnlstd =[8.8801544388114593, 4.0, 7.5, 5.5, 4.5, 5.0, 5.3385391260156556, 9.8994949366116654]
bnlw = np.array(bnlc)/18.1
bnlr = sm.OLS(bnle,sm.add_constant(bnlw)).fit()
bnlr_a= bnlr.params[1]
bnlr_b= bnlr.params[0]
plt.errorbar(bnlw, bnle, bnlstd, fmt='s', color ='b')
plt.plot(bnlw, bnlw*bnlr_a+bnlr_b, label= "BNL Caps Raw Data", color='b')
#ywr = sm.OLS(yms3[0:4],sm.add_constant(ws[0:4])).fit()
#ywr_a= ywr.params[1]
#ywr_b= ywr.params[0]
#plt.plot(ws, ws*ywr_a+ywr_b, label= "Filtered Wire Data (Fit)", color='b')


mbx = [2.5, 4.8, 4.8]
mbe = [350, 490, 480]
fmbe = [300, 380, 400]
#plt.fill_between(mbx, mbe, fmbe, color = 'pink', interpolate=True )
plt.scatter(mbx, mbe, marker='D', color ='c', label = "MicroBooNE Raw Data")
plt.scatter(mbx, fmbe, marker='p', color ='brown', label = "MicroBooNE Filtered Data")

apa40x = [2.8, 4, 4]
apa40e = [332, 383, 395]
apa40s = [21, 24, 19]
plt.errorbar(apa40x, apa40e, apa40s, color = "m", fmt='d', label = "40% APA Raw Data")
fapa40e = [318, 325, 352]
plt.scatter(apa40x, fapa40e, marker='X', color ='olive', label = "40% APA Filtered Data")



pdx = [6, 7.39, 7.39]
pde = [565, 662, 651]
pds = [60, 56, 54]
plt.errorbar(pdx, pde, pds, color = "orange", fmt='P', label = "ProtoDUNE Raw Data")

#rawx = np.array([ws[0],ws[2]] + mbx + apa40x + pdx)
rawx = np.array([ws[0],ws[2]] + mbx  + pdx)
#rawy = [yms1[0],yms1[2]] + mbe + apa40e + pde
rawy = [yms1[0],yms1[2]] + mbe  + pde
rraw = sm.OLS(rawy, sm.add_constant(rawx)).fit()
rraw_a= rraw.params[1]
rraw_b = rraw.params[0]
rawxx = np.append(rawx,8.2)

plt.plot(rawxx, rawxx*rraw_a+rraw_b,  color='c', label = "Fitting with MicroBooNE Raw Data\n and ProtoDUNE Raw Data")



#
#apa40x = [2.8, 4, 4]
#apa40e = [332, 351, 380]
#plt.scatter(apa40x, apa40e, marker='d', color ='m', label = "40% APA Raw Data")
#fapa40e = [318, 325, 352]
#plt.scatter(apa40x, fapa40e, marker='D', color ='m', label = "40% APA Filtered Data")

#apa40s = [21, 24, 19]
#plt.errorbar(apa40x, apa40e, apa40s, fmt='d', label = "40% APA Raw Data")

wssort = np.array(sorted(ws))
#plt.fill_between(wssort, wssort*y1r_a+y1r_b, wssort*y3r_a+y3r_b, color = 'y' )

plt.title("Noise Performance", fontsize = 24 )
plt.ylabel("ENC / e$^-$", fontsize = 20 )
plt.xlabel("Equivalent Wire Length (18.1pF/m) / m ", fontsize = 20 )
plt.xlim([-1,10])
plt.ylim([0,1000])
plt.tick_params(labelsize=20)
#plt.grid(axis="y")
plt.grid()
plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
plt.legend(loc='best', fontsize=16)
#plt.show()
plt.savefig(rpath + "/run51dat_noise_range_alls.png")
#



















##for ccs in [open_inds, inds, open_cols,cols, c150s, c100s, c050s, c027s]:
#for ccs in [open_inds, inds, open_cols,cols]:
#    print len(ccs)
#    plt.vlines(i, 0, 500, color='c', linestyles="dotted", linewidth=0.8)
#    x = []
#    y1 = []
#    y2 = []
#    y3 = []
#    for cs in ccs:
#        x.append(i)
#        y1.append(cs[11])
#        y2.append(cs[12])
#        y3.append(cs[13])
#        i = i + 1
#    #    plt.scatter([i], [cs[11]], marker="+", color = "C" + str(cs[3]))
#    #    plt.scatter([i], [cs[12]], marker="o", color = "C" + str(cs[3]))
#    #    plt.scatter([i], [cs[13]], marker=".", color = "C" + str(cs[3]))
#    plt.plot(x, y1, color = "r" )
#    plt.plot(x, y2, color = "c" )
#    plt.plot(x, y3, color = "g" )


#for ccs in [bads]:
#    print len(ccs)
#    plt.vlines(i, 0, 800, color='c', linestyles="dotted", linewidth=0.8)
#    for cs in ccs:
#        plt.scatter([i], [cs[11]], marker=".", color = "K")
#        i = i + 1


plt.close()







#print open_inds[0]
#print inds[0] 
#print open_cols[0]
#print cols[0] 
#print c150s[0]
#print c100s[0]
#print c050s[0]
#print c027s[0]
#print bads[0] 
#

#for i in range(32):
#    print ind_grs[i]





#PCE = t_pat + "_ProtoDUNE_CE_characterization_summary" + ".csv"
#ppath = rpath + PCE
#ccs = []
#with open(ppath, 'r') as fp:
#    for cl in fp:
#        tmp = cl.split(",")
#        x = []
#        for i in tmp:
#            x.append(i.replace(" ", ""))
#        x = x[:-1]
#        ccs.append(x)
#ccs_title = ccs[0]
#ccs = ccs[1:]
#
#cpath = "/Users/shanshangao/Google_Drive_BNL/tmp/pd_tmp/coh_results/"
#
#for root, dirs, files in os.walk(cpath):
#    break
#
#cohcsvfs = []
#for f in files:
#    if (".csv" in f) and ( "COH_" in f):
#        cohcsvfs.append(f)
#
#cohtitle = []
#cohapa = []
#for f in cohcsvfs:
#    li = 0
#    with open(cpath+f, 'r') as fp:
#        for cl in fp:
#            tmp = cl.split(",")
#            x = []
#            for i in tmp:
#                x.append(i.replace(" ", ""))
#            x = x[:-1]
#            if ( li != 0 ):
#                cohapa.append(x)
#            else:
#                cohtitle = x
#            li = li + 1
#
#cohccs_title = ccs_title + ["rawrms", "rawped", "postrms", "postped", "cohrms", "cohped", "coh_chns"]
#cohccs = []
#for ci in ccs:
#    for cohi in cohapa:
#        if (ci[0] == cohi[0]) and (ci[2] == cohi[4]) and (ci[3] == cohi[1]) and (ci[4] == cohi[2]) : 
#            cohccs.append(ci + cohi[8:15])
#            break
#
#COH = t_pat + "COH_ProtoDUNE_CE_characterization_summary" + ".csv"
#with open (rpath+COH, 'w') as fp:
#    fp.write(",".join(str(i) for i in cohccs_title) +  "," + "\n")
#    for x in cohccs:
#        fp.write(",".join(str(i) for i in x) +  "," + "\n")
#
#print len(cohccs)
#
