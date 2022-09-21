import time

import numpy as np
#import pytest
from consts import *
#from ddd.efficiency.rcwa import Rcwa
#from tests.fixtures.ddd.rcwa import *
from dfmod_test import *
import matplotlib.pyplot as plt
from decimal import *
from dataclass import RefractiveIndices

#setups the range of test, incluting the last value
#from rcwa_excel_comparer import S4_inputs
from ast import literal_eval
import inspect

class S4_inputs:
    def __init__(self, color, column_names, line_data):
        self._init_names_()
        self.color = color
        self.assign(color, column_names, line_data)
        self.save_s4('s4_values.txt')

    def _init_names_(self):
        self.__name_color_header = 'ray_color'
        self.__name_element_color_header = 'element_color'
        self.__name_groove_width = 'groove_width'
        self.__name_etching_depth = 'etching_depth'
        self.__name_period = 'period'
        self.__name_refractive_index = 'refractive_index'
        self.__name_polarization = 'polarization'
        self.__name_incident_angles_theta = 'incident_angle_theta'
        self.__name_incident_angles_phi = 'incident_angle_phi'
        self.__name_polarization_out = 'polarization_out'
        self.__name_efficiency = 'efficiency'
        self.__name_tolerance_efficiency = 'tolerance_efficiency'

        self.__name_groove_step_interval = 'groove_step_interval'
        self.__name_groove_tolerance = 'groove_tolerance'

        self.__name_etching_step_interval = 'etching_step_interval'
        self.__name_etching_tolerance_percent = 'etching_tolerance_percent'


    def assign(self,  color, column_names, line_data):
        index_of_color = colors.index(color)
        self.refractive_index = self.get_value_by_key(self.__name_refractive_index, column_names, line_data)
        self.groove_width = self.get_value_by_key(self.__name_groove_width, column_names, line_data)
        self.etching_depth = self.get_value_by_key(self.__name_etching_depth, column_names, line_data)
        self.period = self.get_value_by_key(self.__name_period, column_names, line_data)
        self.color_struct = self.get_color(color)

        polarization_str = self.get_value_by_key(self.__name_polarization, column_names, line_data)
        polarization = literal_eval(polarization_str)
        self.polarization_s = polarization[0]
        self.polarization_p = polarization[1]

        self.incident_angle_theta = (self.get_value_by_key(self.__name_incident_angles_theta, column_names, line_data))

        self.incident_angle_phi = (self.get_value_by_key(self.__name_incident_angles_phi, column_names, line_data))
        incident_angles = (self.incident_angle_theta, self.incident_angle_phi)

        self.s4_efficiency = self.get_value_by_key(self.__name_efficiency, column_names, line_data)
        self.s4_tolerance_efficiency = self.get_value_by_key(self.__name_tolerance_efficiency, column_names, line_data)

        self.current_color = self.get_value_by_key(self.__name_element_color_header, column_names, line_data)

        # fixing incosistent separators issue in vector of complex numbers
        polarization_out_str = self.get_value_by_key(self.__name_polarization_out, column_names, line_data)
        polarization_out_str = ''.join(polarization_out_str.splitlines())
        polarization_out_str = polarization_out_str.strip()
        polarization_out_str = polarization_out_str.replace('j', 'j,')
        self.polarization_out = np.array(literal_eval(polarization_out_str)).T  # [..., np.newaxis]

        self.groove_step_interval = self.get_value_by_key(self.__name_groove_step_interval, column_names, line_data)
        self.groove_tolerance = self.get_value_by_key(self.__name_groove_tolerance, column_names, line_data)

        self.etching_step_interval = self.get_value_by_key(self.__name_etching_step_interval, column_names, line_data)
        self.etching_tolerance_percent = self.get_value_by_key(self.__name_etching_tolerance_percent, column_names, line_data)

        return

    def save_s4(self, file_name):
        f = open(file_name, "w")
        for i in inspect.getmembers(self):
            # to remove private and protected
            # functions
            if not i[0].startswith('_'):
                # To remove other methods that
                # doesnot start with a underscore
                if not inspect.ismethod(i[1]):
                    f.write(str(i[0])+'='+str(i[1])+'\n')
        f.close()

        #self.groove_width = 0.00023;
        #self.etching_depth = 0.00014;
        #self.period = 0.0003438029949536198;
        #self.refractive_index = 1.4613;
        #self.polarization_s=(0.6262529277655595+0.733677045471162j);
        #self.polarization_p=(0.1622149087808452+0.20770052522254576j);
        #self.incident_angle_theta = np.deg2rad(47.49019073364811);
        #self.incident_angle_phi = np.deg2rad(-12.240125456111668);
        #polarization_out; = {str} ;[[0.44541021+0.74619376j]\n [0.31558368+0.38105626j]];
        #efficiency; = {str} ;0.0606501561686958;
        #rs_efficiency; = {str} ;0.06043082981;
        #rs_efficiency_tolerance; = {str} ;0;
        #rs_field; = {str} ;[[-0.03404255+0.9616731j ]\n [ 0.04644813+0.26808306j]];


    def get_order_sign(self):
        order = int(self.current_color == self.color)
        sign = 2 * int(np.rad2deg(np.abs(self.incident_angle_phi)) > 90.0) - 1
        return (order*sign)

    def get_value_by_key(self, key, column_names, line_data):
        inds = np.argwhere(column_names.values == key)
        if(inds.shape[0] == 0):
            return None
        index = int(inds[0])
        value = line_data[index]

        if(type(value) is float or type(value) is int):
            return value
        try:
            c = complex(value)
            if(np.iscomplex(c)):
                value = c
        except ValueError:
            bad_comlex=0
        return value

    def get_color(self, color):
        if(color == 'green'):
            return Color.green()
        if(color == 'blue'):
            return Color.blue()
        if(color == 'red'):
            return Color.red()
        raise KeyError(f'{color} is not red, green or blue.')




