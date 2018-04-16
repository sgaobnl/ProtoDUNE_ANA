#!/bin/bash
## APA_analysis.py --> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag
#python APA_analysis.py   5   "04_12_2018" "04_12_2018" "04_12_2018" run08rms run04fpg   run03asi   Coldbox    False 
#
## apa_plot_main.py--> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder 
python apa_plot_main.py  5   "04_12_2018" "04_12_2018" "04_12_2018" run08rms   run04fpg  run03asi  Coldbox 
#
## avg_chns_fft.py --> # apano   rmsdate      fpgdate      asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag PSD_EN  PSD
#python avg_chns_fft.py   5   "04_12_2018" "04_12_2018" "04_12_2018"  run08rms  run04fpg  run03asi  Coldbox     False     False    0


#python APA_analysis.py   1   "11_11_2017" "11_10_2017" "11_10_2017" run06rms   run04fpg   run05asi  APA    False 
#python apa_plot_main.py  1   "11_11_2017" "11_10_2017" "11_10_2017" run06rms   run04fpg   run05asi  APA 
#python avg_chns_fft.py   1   "11_11_2017" "11_10_2017" "11_10_2017" run06rms   run04fpg   run05asi  APA    False     False    0






                     # apano,   rmsdate,     fpgdate,     asidate, rmsrunno, fpgarunno, asicrunno, apafolder, jumbo_flag
#python APA_analysis.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run08rms   run04fpg  run03asi  Coldbox  False

#python apa_plot_main.py 5     "04_12_2018" "04_12_2018" "04_12_2018" run01rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run01rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run04rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run05rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run06rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run07rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run08rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_12_2018" "04_12_2018" "04_12_2018" run08rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run08rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run09rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_12_2018" "04_12_2018" "04_12_2018" run09rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_12_2018" "04_12_2018" "04_12_2018" run09rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run01rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_13_2018" "04_12_2018" "04_12_2018" run01rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run01rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run02rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_13_2018" "04_12_2018" "04_12_2018" run02rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run02rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run03rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_13_2018" "04_12_2018" "04_12_2018" run03rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run03rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run04rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_13_2018" "04_12_2018" "04_12_2018" run04rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run04rms   run04fpg  run03asi  Coldbox 
#
##python APA_analysis.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run05rms   run04fpg  run03asi  Coldbox 
##python apa_plot_main.py 5     "04_13_2018" "04_12_2018" "04_12_2018" run05rms   run04fpg  run03asi  Coldbox 
#python avg_chns_fft.py  5     "04_13_2018" "04_12_2018" "04_12_2018" run05rms   run04fpg  run03asi  Coldbox 
#
