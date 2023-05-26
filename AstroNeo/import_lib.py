# Import Library
import os
from psutil import cpu_count
import time, datetime, subprocess
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import csv
import sys
# import sherpa
import matplotlib.pyplot as plt
import matplotlib as mpl
import pathlib
import numpy as np
from operator import itemgetter
import operator
import random
from .import_lib import *
from .input_arg import *
from .helper import *
# from sherpa.astro.ui import load_rmf, set_analysis, notice_id, set_method, set_xsabund, \
#     set_xsxsect, set_xscosmo, set_source, get_staterror, get_stat_info, plot_fit, set_stat, subtract

# Need further testing to see if this is needed...
os.environ['HEADAS'] = '/Users/andy/projects/xspec/heasoft-6.31.1/aarch64-apple-darwin22.4.0'
os.system(f"source $HEADAS/headas-init.sh")

import xspec

sys.path.append("/Users/andy/projects/Astro_Neo/input_files/ACX2")
import acx2_xspec

xspec.xset.Xset.chatter = 0



if timeing_mode:
    # %matplotlib inline
    t1 = timecall()

# Set the number of threads
os.environ['NUMEXPR_MAX_THREADS'] = str(cpu_count())
# import larch
# import lmfit
# from larch_plugins.io import read_ascii
# from larch_plugins.xafs import autobk
# from larch_plugins.xafs import feffdat
# from larch_plugins.xafs import xftf
# from larch import Interpreter
# from scipy.integrate import simps
# from multiprocessing import Pool
# import multiprocessing as mp
# import ray
# from multiprocessing import Pool as ProcessPool
# from multiprocessing.dummy import Pool as ThreadPool  ### this uses threads

if timeing_mode:
    initial_elapsed = timecall() - t1
    print('Inital import function took %.2f second' % initial_elapsed)
