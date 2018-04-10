# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/10/2018 4:40:22 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

def femb_position (APAno=1):
    if (APAno == 1):
        femb_pos_np = [ 
                #"B101" --> B1: APA#1 B side, 01: APA slot number, "B101" is also embeded in EPROM address 0x2000X
                #"WIB4_FEMB1": WIB4 --> WIB position in crate, FEMB1 --> FEMB slot of WIB
                #"CEbox10" : CE box number
                #"0x20000 : EPPOM ID address
                        ["B101", "WIB04_FEMB1", "CEbox010", "0x20000",], 
                        ["B102", "WIB03_FEMB1", "CEbox025", "0x20000",], 
                        ["B103", "WIB02_FEMB1", "CEbox026", "0x20000",], 
                        ["B104", "WIB01_FEMB1", "CEbox011", "0x20000",], 
                        ["B105", "WIB00_FEMB1", "CEbox003", "0x20000",], 

                        ["B106", "WIB04_FEMB0", "CEbox012", "0x20000",], 
                        ["B107", "WIB03_FEMB0", "CEbox016", "0x20000",], 
                        ["B108", "WIB02_FEMB0", "CEbox021", "0x20000",], 
                        ["B109", "WIB01_FEMB0", "CEbox007", "0x20000",], 
                        ["B110", "WIB00_FEMB0", "CEbox004", "0x20000",], 
                        
                        ["A111", "WIB04_FEMB3", "CEbox001", "0x20000",], 
                        ["A112", "WIB03_FEMB3", "CEbox017", "0x20000",], 
                        ["A113", "WIB02_FEMB3", "CEbox027", "0x20000",], 
                        ["A114", "WIB01_FEMB3", "CEbox013", "0x20000",], 
                        ["A115", "WIB00_FEMB3", "CEbox008", "0x20000",], 

                        ["A116", "WIB04_FEMB2", "CEbox002", "0x20000",], 
                        ["A117", "WIB03_FEMB2", "CEbox015", "0x20000",], 
                        ["A118", "WIB02_FEMB2", "CEbox023", "0x20000",], 
                        ["A119", "WIB01_FEMB2", "CEbox005", "0x20000",], 
                        ["A120", "WIB00_FEMB2", "CEbox014", "0x20003",], 
                    ]
    elif (APAno ==2):
        femb_pos_np = [ 
                        ["B201", "WIB04_FEMB1", "CEbox042", "0x20000",], 
                        ["B202", "WIB03_FEMB1", "CEbox048", "0x20001",], 
                        ["B203", "WIB02_FEMB1", "CEbox054", "0x20000",], 
                        ["B204", "WIB01_FEMB1", "CEbox051", "0x20000",], 
                        ["B205", "WIB00_FEMB1", "CEbox044", "0x20000",], 
    
                        ["B206", "WIB04_FEMB0", "CEbox052", "0x20000",], 
                        ["B207", "WIB03_FEMB0", "CEbox055", "0x20000",], 
                        ["B208", "WIB02_FEMB0", "CEbox006", "0x20000",], 
                        ["B209", "WIB01_FEMB0", "CEbox047", "0x20000",], 
                        ["B210", "WIB00_FEMB0", "CEbox053", "0x20000",], 
                        
                        ["A211", "WIB04_FEMB3", "CEbox036", "0x20000",], 
                        ["A212", "WIB03_FEMB3", "CEbox057", "0x20000",], 
                        ["A213", "WIB02_FEMB3", "CEbox040", "0x20000",], 
                        ["A214", "WIB01_FEMB3", "CEbox046", "0x20000",], 
                        ["A215", "WIB00_FEMB3", "CEbox045", "0x20000",], 
    
                        ["A216", "WIB04_FEMB2", "CEbox058", "0x20000",], 
                        ["A217", "WIB03_FEMB2", "CEbox043", "0x20000",], 
                        ["A218", "WIB02_FEMB2", "CEbox039", "0x20000",], 
                        ["A219", "WIB01_FEMB2", "CEbox041", "0x20000",], 
                        ["A220", "WIB00_FEMB2", "CEbox019", "0x20000",], 
                    ]

    elif (APAno ==3):
        femb_pos_np = [ 
                        ["B301", "WIB04_FEMB1", "CEbox064", "0x20000",], 
                        ["B302", "WIB03_FEMB1", "CEbox056", "0x20000",], 
                        ["B303", "WIB02_FEMB1", "CEbox018", "0x20000",], 
                        ["B304", "WIB01_FEMB1", "CEbox084", "0x20000",], 
                        ["B305", "WIB00_FEMB1", "CEbox073", "0x20000",], 
    
                        ["B306", "WIB04_FEMB0", "CEbox087", "0x20000",], 
                        ["B307", "WIB03_FEMB0", "CEbox075", "0x20000",], 
                        ["B308", "WIB02_FEMB0", "CEbox022", "0x20001",], 
                        ["B309", "WIB01_FEMB0", "CEbox088", "0x20000",], 
                        ["B310", "WIB00_FEMB0", "CEbox076", "0x20000",], 
                        
                        ["A311", "WIB04_FEMB3", "CEbox083", "0x20000",], 
                        ["A312", "WIB03_FEMB3", "CEbox050", "0x20000",], 
                        ["A313", "WIB02_FEMB3", "CEbox077", "0x20000",], 
                        ["A314", "WIB01_FEMB3", "CEbox080", "0x20000",], 
                        ["A315", "WIB00_FEMB3", "CEbox049", "0x20000",], 
    
                        ["A316", "WIB04_FEMB2", "CEbox060", "0x20000",], 
                        ["A317", "WIB03_FEMB2", "CEbox079", "0x20000",], 
                        ["A318", "WIB02_FEMB2", "CEbox066", "0x20000",], 
                        ["A319", "WIB01_FEMB2", "CEbox072", "0x20000",], 
                        ["A320", "WIB00_FEMB2", "CEbox074", "0x20000",], 
                    ]

    elif (APAno ==4):
        femb_pos_np = [ 
                        ["B401", "WIB04_FEMB1", "CEbox096", "0x20000",], 
                        ["B402", "WIB03_FEMB1", "CEbox101", "0x20000",], 
                        ["B403", "WIB02_FEMB1", "CEbox038", "0x20000",], 
                        ["B404", "WIB01_FEMB1", "CEbox085", "0x20000",], 
                        ["B405", "WIB00_FEMB1", "CEbox089", "0x20000",], 
    
                        ["B406", "WIB04_FEMB0", "CEbox082", "0x20000",], 
                        ["B407", "WIB03_FEMB0", "CEbox095", "0x20000",], 
                        ["B408", "WIB02_FEMB0", "CEbox069", "0x20000",], 
                        ["B409", "WIB01_FEMB0", "CEbox070", "0x20000",], 
                        ["B410", "WIB00_FEMB0", "CEbox065", "0x20000",], 
                        
                        ["A411", "WIB04_FEMB3", "CEbox098", "0x20000",], 
                        ["A412", "WIB03_FEMB3", "CEbox094", "0x20000",], 
                        ["A413", "WIB02_FEMB3", "CEbox092", "0x20000",], 
                        ["A414", "WIB01_FEMB3", "CEbox117", "0x20000",], 
                        ["A415", "WIB00_FEMB3", "CEbox097", "0x20000",], 
    
                        ["A416", "WIB04_FEMB2", "CEbox099", "0x20000",], 
                        ["A417", "WIB03_FEMB2", "CEbox061", "0x20000",], 
                        ["A418", "WIB02_FEMB2", "CEbox067", "0x20000",], 
                        ["A419", "WIB01_FEMB2", "CEbox037", "0x20000",], 
                        ["A420", "WIB00_FEMB2", "CEbox100", "0x20000",], 
                    ]
    elif (APAno ==9): #9 --> 40%APA
        femb_pos_np = [ 
                        ["A901", "WIB00_FEMB0", "CEbox001", "0x20000",], 
                        ["A902", "WIB00_FEMB1", "CEbox002", "0x20000",], 
                        ["A903", "WIB00_FEMB2", "CEbox003", "0x20000",], 
                        ["A904", "WIB00_FEMB3", "CEbox004", "0x20000",], 
                    ]


    return femb_pos_np

