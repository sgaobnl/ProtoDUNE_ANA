:: APA_analysis.py --> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag
::python APA_analysis.py   9   "04_15_2018" "04_15_2018" "04_15_2018" run01rms run01fpg   run01asi   APA40      True
::
:: apa_plot_main.py--> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder 
python apa_plot_main.py 9     "04_15_2018" "04_15_2018" "04_15_2018" run01rms   run01fpg  run01asi  APA40 
::
:: avg_chns_fft.py --> # apano   rmsdate      fpgdate      asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag PSD_EN  PSD
::python avg_chns_fft.py     9   "04_15_2018" "04_15_2018" "04_15_2018"  run01rms  run01fpg  run01asi     APA40     True   False    0

