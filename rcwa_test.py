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

def rsoft_compute(refractive_index, etching_depth, groove_width, period, color, polarization, incident_angle_launch, incident_angle_theta, sidewall_angle, column_name):
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



def translate_rsoft_params(refractive_index, etching_depth, groove_width, period, color,
                                    polarization: tuple, incident_angle_launch, incident_angle_theta, sidewall_angle: float, index=None):
    variable_data = dict()
    variable_data['delta1'] = refractive_index - 1

    #refractive index of the substrate
    variable_data['delta2'] = RefractiveIndices.sio2[color]-1 #0.4613#0.4586#refractive_index - 1

    variable_data['h1'] = etching_depth * mm_2_micron
    variable_data['h2'] = 0.005 * mm_2_micron

    variable_data['free_space_wavelength'] = color.wavelength * mm_2_micron
    variable_data['period'] = period * mm_2_micron
    variable_data['width1'] = (period - groove_width) * mm_2_micron

    s_polarization, p_polarization = polarization
    s_norm = np.real(np.sqrt(s_polarization * np.conj(s_polarization) + p_polarization * np.conj(p_polarization)))
    s_n = s_polarization / s_norm
    p_n = p_polarization / s_norm
    pol = np.arcsin(np.abs(s_n)) / deg
    arg_p = np.angle(p_n)
    arg_s = np.angle(s_n)
    variable_data['rcwa_launch_pol'] = pol
    variable_data['rcwa_launch_delta_phase'] = (arg_p-arg_s)/deg

    #incident_angle_theta = test_range_config.incident_angle_launch.min
    incident_angle_phi = incident_angle_theta
    variable_data['launch_angle'] = incident_angle_launch
    variable_data['launch_theta'] = incident_angle_phi
    variable_data['rcwa_harmonics_x'] = config_harmonics  #ConfigManager.config.harmonics

    variable_data['air_in_depth'] = 0.5
    variable_data['air_out_depth'] = 0.5

    variable_data['rcwa_output_option'] = 1
    #variable_data['rcwa_variation_step'] = 0.1#incident_angle_launch.step
    #variable_data['rcwa_variation_min'] = incident_angle_launch#.min
    #variable_data['rcwa_variation_max'] = incident_angle_launch#.max

    if(index is not None):
        variable_data['index'] = index

    return variable_data

def dxfmod(variable_data):
    dir_name = 'run_test'# + dict_to_prefix(variable_data)
    rsoft_runner = Rsoft_CLI(ind_file, prefix=dir_name,  variable_data = variable_data, hide = True)
    if not rsoft_runner.compute(new_file=True):
        return None
    columns, values = rsoft_runner.read()
    field0, field1 = rsoft_runner.read_fields()
    return columns, values, field0, field1


