:: APA_analysis.py --> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag
python APA_analysis.py   9   "04_15_2018" "04_15_2018" "04_15_2018" ped FPGAdac  ASICdac   FELIX      True
::
:: apa_plot_main.py--> # apano   rmsdate      fpgdate     asidate     rmsrunno fpgarunno asicrunno apafolder 
python apa_plot_main.py 9     "04_15_2018" "04_15_2018" "04_15_2018" ped  FPGAdac  ASICdac  FELIX 
::
:: avg_chns_fft.py --> # apano   rmsdate      fpgdate      asidate     rmsrunno fpgarunno asicrunno apafolder jumbo_flag PSD_EN  PSD  wire_type gains tps
python avg_chns_fft.py     9   "04_15_2018" "04_15_2018" "04_15_2018"  ped     FPGAdac   ASICdac  FELIX      True   False    0       V      250  10
python avg_chns_fft.py     9   "04_15_2018" "04_15_2018" "04_15_2018"  ped     FPGAdac   ASICdac  FELIX      True   False    0       X      250  10
python avg_chns_fft.py     9   "04_15_2018" "04_15_2018" "04_15_2018"  ped     FPGAdac   ASICdac  FELIX      True   False    0       U      250  10

