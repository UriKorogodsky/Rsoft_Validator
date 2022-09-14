import time

import numpy as np
#import pytest
from consts import *
#from ddd.efficiency.rcwa import Rcwa
#from tests.fixtures.ddd.rcwa import *
from dfmod_test import *
import matplotlib.pyplot as plt
import inspect
from decimal import *
from dataclass import RefractiveIndices

#setups the range of test, incluting the last value
#from rcwa_excel_comparer import S4_inputs
from ast import literal_eval

class S4_inputs:
    def __init__(self, color, column_names, line_data):
        self._init_names_()
        self.color = color
        self.assign(color, column_names, line_data)

    def _init_names_(self):
        self.__name_color_header = 'color'
        self.__name_element_color_header = 'element_color'
        self.__name_groove_width = 'groove_width'
        self.__name_etching_depth = 'etching_depth'
        self.__name_period = 'period'
        self.__name_refractive_index = 'refractive_index'
        self.__name_polarization = 'polarization'
        self.__name_incident_angles_theta = 'incident_angle_theta'
        self.__name_incident_angles_phi = 'incident_angle_phi'
        self.__name_polarization_out = 'polarization_out'
        self.__name_efficiency = 'tolerance_efficiency'


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

        self.s4_efficiency_in_table = self.get_value_by_key(self.__name_efficiency, column_names, line_data)
        self.current_color = self.get_value_by_key(self.__name_element_color_header, column_names, line_data)

        # fixing incosistent separators issue in vector of complex numbers
        polarization_out_str = self.get_value_by_key(self.__name_polarization_out, column_names, line_data)
        polarization_out_str = ''.join(polarization_out_str.splitlines())
        polarization_out_str = polarization_out_str.strip()
        polarization_out_str = polarization_out_str.replace('j', 'j,')
        self.polarization_out = np.array(literal_eval(polarization_out_str))  # [..., np.newaxis]

        return

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


        #self.refractive_index = (2.378428+4e-06j)
        #self.etching_depth = 0.00026
        #self.period = 0.000333892879477772
        #self.groove_width = 0.000199
        #self.color = 'green'
        #self.polarization_s = (-0.7778957480364084 + 0j)
        #self.polarization_p = (0.6283933522777567 + 0j)
        #self.incident_angle_theta = 1.0215418
        #self.incident_angle_phi =   -0.1586670382
        #self.sidewall_angle = 0
        #self.order = 1

    def get_order(self):
        return int(self.current_color == self.color)

    #not sure, that it belongs to this class
    def get_test_string(self):
        if (self.current_color == self.color):
            test_string = '10T'
        else:
            test_string = '00T'
        return  test_string


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



class config_range:
    #set only min_or_single, for single value,
    #set min_or_single and max for just two values
    #set min_or_single, max and step for range with given step,
    #including the last element
    def __init__(self, min_or_single, max=None, step=None):
        self.min = min_or_single
        self.max = max #cover the last element too, to be consistent with Rsoft
        self.step = step

    def value(self):
        if(self.max == None):
            return [self.min]
        elif self.step is None:
            self.step = float(Decimal(str(self.max)) - Decimal(str(self.min)))
        max_incl_last = self.max + self.step#cover the last element
        return np.arange(self.min, max_incl_last, self.step)

class test_range_config:
    refractive_index = config_range( 1.4569)
    etching_depth = config_range(0.002375)#,0.004375)#,step=0.001)
    groove_width = config_range(10.0e-05)#, 30.0e-05, step=5.0e-05)
    period = config_range(0.0003501518225175648)
    color = config_range(Color.green())
    polarization = config_range(((-0.06968886435224264+0j), (-0.9975687756667683+0j)))
    launch_angle_step = 0.5
    incident_angle_launch = config_range(min_or_single=10, max=60, step=launch_angle_step)
    incident_angle_theta = config_range(5,25,10)
    sidewall_angle = config_range(0)
    expected = config_range(0.9946828114461291)

def name_and_args():
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    return [(i, values[i]) for i in args]

mm_2_micron=1000.0


def s4_rsoft_test(method, refractive_index, etching_depth, groove_width, period, color, polarization, incident_angle_launch, incident_angle_theta, sidewall_angle, column_name):
    angles_s4, results_s4 = rcwa_compute(method, refractive_index, etching_depth, groove_width, period, color,   polarization, incident_angle_launch, incident_angle_theta, sidewall_angle)
    angles_rsoft, result_rsoft = rsoft_compute(refractive_index, etching_depth, groove_width, period, color, polarization, incident_angle_launch, incident_angle_theta, sidewall_angle, column_name)
    plt.plot(angles_s4, results_s4, 'r')
    plt.plot(angles_rsoft, result_rsoft, 'c')

    delta = np.abs(results_s4-np.array(result_rsoft))

    std = np.std(delta)
    var = np.var(delta)
    med = np.median(delta)
    mean = np.mean(delta)


def rcwa_compute(method, refractive_index, etching_depth, groove_width, period, color, polarization, incident_angle_launch, incident_angle_theta, sidewall_angle):
    angles_s4 = []
    results_s4 = []
    for launch_angle in incident_angle_launch.value():
        angles_as_list = (launch_angle * deg , incident_angle_theta*deg)
        s4_result = rcwa_compute_single_angle(method, refractive_index, etching_depth, groove_width, period, color, polarization,
                           angles_as_list, sidewall_angle)
        angles_s4.append(launch_angle)
        results_s4.append(s4_result)
    return angles_s4, results_s4

def rcwa_compute_single_angle(method, refractive_index, etching_depth, groove_width, period, color, polarization, angles_as_list, sidewall_angle):
    input = name_and_args()
    s4_result = method(refractive_index, etching_depth, groove_width, period, color, polarization, angles_as_list,
                       sidewall_angle)
    input.append(('output', s4_result))
    return s4_result

def rsoft_compute(s4_data:S4_inputs, column_name):
    dfmod_params = translate_rsoft_params(s4_data)
    columns, values, field0, field1 = dxfmod(dfmod_params)
    out_index = values.index(column_name)
    #angles_index = values.index('phi')
    angles_index = values.index('none')
    result_rsoft = columns[out_index]
    angles = columns[angles_index]
    return angles, result_rsoft, field0, field1

def rsoft_compute_old(refractive_index, etching_depth, groove_width, period, color, polarization, incident_angle_launch, incident_angle_theta, sidewall_angle, column_name):
    dfmod_params = translate_rsoft_params(refractive_index, etching_depth, groove_width, period, color,
                                                 polarization, incident_angle_launch, incident_angle_theta, sidewall_angle)
    columns, values, field0, field1 = dxfmod(dfmod_params)
    out_index = values.index(column_name)
    #angles_index = values.index('phi')
    angles_index = values.index('none')
    result_rsoft = columns[out_index]
    angles = columns[angles_index]
    return angles, result_rsoft, field0, field1


#                         ', etching_depth, groove_width, period, color, polarization, incident_angles, sidewall_angle, expected', [
#    [1.4569, 0.002375, 8.499999999999999e-05, 0.0004501518225175648, Color.red(), ((-0.06968886435224264+0j), (-0.9975687756667683+0j)), (0.7876505009301327, -0.02626090545231785), 0, 0.9946828114461291]
#])
def do_not_test_calculate_first_order_transmission(initializedRcwa, refractive_index, etching_depth, groove_width, period, color,
                                      polarization: tuple, incident_angles: tuple, sidewall_angle: float, expected):
    print(refractive_index)
    nv = name_and_args()
    loc = locals()

    angles_s4 = []
    orders = []
    for launch_angle in incident_angles[0]:#np.arange(10,60.1, 0.2):
        angles_as_list = list(incident_angles)
        angles_as_list[0] = launch_angle*deg
        angles_as_list[1] = 10*deg
        first_order = initializedRcwa.calculate_first_order_transmission(refractive_index, etching_depth, groove_width, period, color,
                                          polarization, angles_as_list, sidewall_angle)
        angles_s4.append(launch_angle)
        orders.append(first_order)

    dfmod_params = translate_rsoft_params(refractive_index, etching_depth, groove_width, period, color,
                                         polarization, angles_as_list, sidewall_angle)
    columns, values = dxfmod(dfmod_params)
    out_index = values.index('10T')
    angles_index = values.index('phi')
    T1_rsoft = columns[out_index]
    angles = columns[angles_index]

    plt.plot(angles,T1_rsoft,'r')
    plt.plot(angles_s4,orders,'c')

    delta = np.abs(T1_rsoft-np.array(orders))
    med = np.median(delta)
    mean = np.mean(delta)
    plt.show()
    return

    #assert np.allclose(first_order, expected)

def rsoft_polarisation(polarization):
    s_polarization, p_polarization = polarization
    s_norm = np.real(np.sqrt(s_polarization * np.conj(s_polarization) + p_polarization * np.conj(p_polarization)))
    s_n = s_polarization / s_norm
    p_n = p_polarization / s_norm
    pol = np.rad2deg(np.arcsin(np.abs(s_n)))
    arg_p = np.angle(p_n)
    arg_s = np.angle(s_n)
    return pol, arg_s, arg_p

#def translate_rsoft_params(refractive_index, etching_depth, groove_width, period, color,
                                    #polarization: tuple, incident_angle_launch, incident_angle_theta, sidewall_angle: float, index=None):
def translate_rsoft_params(s4_data:S4_inputs):#refractive_index, etching_depth, groove_width, period, color,
                               #polarization: tuple, incident_angle_launch, incident_angle_theta, sidewall_angle: float,
                               #index=None):
    variable_data = dict()

    variable_data['delta1'] = np.real(complex(s4_data.refractive_index)) - 1
    variable_data['alpha'] = np.imag(complex(s4_data.refractive_index))

    #refractive index of the substrate
    variable_data['delta2'] = RefractiveIndices.sio2[s4_data.color_struct]-1 #0.4613#0.4586#refractive_index - 1

    variable_data['h1'] = s4_data.etching_depth * mm_2_micron
    variable_data['h2'] = 0.5 * mm_2_micron

    variable_data['free_space_wavelength'] = s4_data.color_struct.wavelength * mm_2_micron
    variable_data['period'] = s4_data.period * mm_2_micron
    variable_data['width1'] = (s4_data.period - s4_data.groove_width) * mm_2_micron

    pol, arg_s, arg_p = rsoft_polarisation([s4_data.polarization_s, s4_data.polarization_p ])
    variable_data['rcwa_launch_pol'] = pol
    variable_data['rcwa_launch_delta_phase'] = np.rad2deg(arg_p-arg_s)

    #incident_angle_theta = test_range_config.incident_angle_launch.min
    #incident_angle_phi = s4_data.incident_angle_theta
    variable_data['launch_angle'] = np.rad2deg(s4_data.incident_angle_theta)# incident_angle_launch
    variable_data['launch_theta'] = np.rad2deg(s4_data.incident_angle_phi)
    variable_data['rcwa_harmonics_x'] = config_harmonics  #ConfigManager.config.harmonics

    variable_data['air_in_depth'] = 0.5
    variable_data['air_out_depth'] = 0.5

    variable_data['rcwa_output_option'] = 1
    #variable_data['rcwa_variation_step'] = 0.1#incident_angle_launch.step
    #variable_data['rcwa_variation_min'] = incident_angle_launch#.min
    #variable_data['rcwa_variation_max'] = incident_angle_launch#.max

    #if(index is not None):
    #    variable_data['index'] = index

    return variable_data

def dxfmod(variable_data):
    dir_name = 'run_test'# + dict_to_prefix(variable_data)
    rsoft_runner = Rsoft_CLI(ind_file, prefix=dir_name,  variable_data = variable_data, hide = True)
    if not rsoft_runner.compute(new_file=True):
        return None
    columns, values = rsoft_runner.read()
    #field0, field1 = rsoft_runner.read_fields_sp()
    field_sp = rsoft_runner.read_fields_sp()
    field_xyz = rsoft_runner.read_fields_xyz()
    field0 = field_sp[:,0]
    field1 = field_sp[:,1]
    return columns, values, field0, field1


