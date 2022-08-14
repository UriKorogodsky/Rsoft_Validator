import numpy as np
from dataclasses import dataclass
#from logger import *
from color import *
from numpy import sin, cos, sqrt, abs, arccos, arctan2, arcsin


def flatten(list_of_lists):
    flat_list = []
    for lst in list_of_lists:
        flat_list.extend(lst)

    return flat_list


pi = np.pi
pi_2 = np.pi * 2
pi_div_2 = np.pi / 2
deg = pi/180

eye_resolution = deg/20
bragg_angle = 30*deg
mm = 1
mu = 1/1_000  # micrometer
nm = 1/1_000_000  # nanometer
x_sampling = 1e-3*mm




#from config_manager import ConfigManager
