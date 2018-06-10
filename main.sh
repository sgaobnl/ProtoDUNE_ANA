#!/bin/bash
## APA_analysis.py --> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag
python APA_analysis.py   1   "06_05_2018" "06_05_2018" "06_05_2018" run01rms run01fpg   run01asi   APA    False 
#
## apa_plot_main.py--> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder 
python apa_plot_main.py  1   "06_05_2018" "06_05_2018" "06_05_2018" run01rms   run01fpg  run01asi  APA 
#
## avg_chns_fft.py --> # apano   rmsdate      fpgdate      asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag PSD_EN  PSD wire_type gains tps
python avg_chns_fft.py   1   "06_05_2018" "06_05_2018" "06_05_2018" run01rms  run01fpg  run01asi     APA     False     False    0     V       250  20







