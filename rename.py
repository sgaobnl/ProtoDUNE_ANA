# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sun Apr  8 17:44:29 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
#import numpy as np
#import struct
import os
#from matplotlib.colors import LogNorm
#import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
from sys import exit
import zipfile
from shutil import copyfile
from shutil import move
from shutil import rmtree

path ="/nfs/rscratch/bnl_ce/shanshan/Rawdata/APA1/" 

for root, dirs, files in os.walk(path):
    break
for onedir in dirs:
    path2 = path+onedir+"/"
    for root2, dirs2, files2 in os.walk(path2):
        break
    for onedir2 in dirs2:
        path3 = path2+onedir2+"/"
        for root3, dirs3, files3 in os.walk(path3):
            break
        for onedir3 in dirs3:
            if (onedir3.find("WIB") >= 0)  :
                pos = onedir3.find("WIB") 
                wibi = int(onedir3[pos+3]) - 1
                new= path3 + onedir3[0:pos+3] + format(wibi, "02d") + onedir3[pos+4:] 
                print new
                os.rename(path3 + onedir3 , new)
            #path3 = path3+onedir3+"/"
            #print path3
            #exit()
 
#
#
#    for onedir2 in dirs2:
#        path2 = path+onedir2+"/"
#
#        for root3, dirs3, files3 in os.walk(path2):
#            break
#        for onedir3 in dirs3:
#            path3 = path2+onedir3+"/"
#            #exit()
##            for root4, dirs4, files4 in os.walk(path3):
##                break
#
#            for onedir4 in [path3]:
##            for onedir4 in dirs4:
#                path5 = path3+onedir4+"/"
#                print path5
#                dirs5 = None
#                for root5, dirs5, files5 in os.walk(path5):
#                    break
#                if (dirs5 != None) :
#                    for onedir in dirs5:
#                        print onedir
                #for onefile in files5:
                #    if (onefile.find("WIB000") >= 0)  :
                #        pos = onefile.find("WIB000") 
                #        wibi = int(onefile[pos+6]) - 1
                #        #print path5 + onefile
                #        new= path5 + onefile[0:pos+3] + format(wibi, "02d") + onefile[pos+7:] 
                #        print new
#                        os.rename(path5 + onefile , new)
                        #exit()
                        #os.rename(path5 + onefile , path5 + onefile[0:pos+3] + format(wibi, "02d") + onefile[pos+4:] )
 

#                for onefile in files4:
#                    path4 = path3 + onefile
#                    if (onefile.find("WIB") >= 0)  :
#                        pos = onefile.find("WIB") 
#                        wibi = int(onefile[pos+3])
#                        print path4
#                        os.rename(path4 , path3 + onefile[0:pos+3] + format(wibi, "02d") + onefile[pos+4:] )
                #    path5 = path4+onedir+"/"
                #    print path5 +  onefile
                    #wibi = int(onefile[3])


 
            #if onedir[0:3] == "WIB" :
            #    for root3, dirs3, files3 in os.walk(path+onedir+"/"):
            #        break
            #    for onefile in files3:
            #        if onefile[0:3] == "WIB" :
            #            path3 = path+onedir+"/"
            #            print path3 +  onefile
            #            wibi = int(onefile[3])
            #            os.rename(path3 + onefile, path3 + onefile[0:3] + format(wibi, "02d") + onefile[4:] )


#for onefile in files:
#    if onefile[0:4] == "WIB1" :
#        path3 = path
#        print path3 +  onefile
#        os.rename(path3 + onefile, path3 + onefile[0:3] + "3" + onefile[4:] )
#        #os.rename(path3 + onefile, path3 + onefile[0:11] + "0" + onefile[12:] )

#for onedir in dirs:
#    if onedir[0:4] == "WIB2" :
#        for root3, dirs3, files3 in os.walk(path+onedir+"/"):
#            break
#        for onefile in files3:
#            if onefile[0:4] == "WIB2" :
#                path3 = path+onedir+"/"
#                print path3 +  onefile
#                os.rename(path3 + onefile, path3 + onefile[0:3] + "3" + onefile[4:] )

#for onedir in dirs:
#    for root2, dirs2, files2 in os.walk(path+onedir+"/"):
#        break
#    for onedir2 in dirs2:
#        if onedir2 == "WIB1RTstep32" :
#            for root3, dirs3, files3 in os.walk(path+onedir+"/"+onedir2+"/"):
#                break
#            for onefile in files3:
#                if onefile[0] == "\\" :
#                    path3 = path+onedir+"/"+onedir2+"/"
#                    print path3 +  onefile
#                    os.rename(path3 + onefile, path3 + onefile[1:] )




