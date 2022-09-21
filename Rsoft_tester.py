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
from rcwa_test import *

#setups the range of test, incluting the last value
#from rcwa_excel_comparer import S4_inputs
from ast import literal_eval

class Rsoft_tester:
    def __init__(self, s4_data:S4_inputs, scan_tolerance = False):
        self.variable_data = self.translate_to_rsoft(s4_data)
        self.s4_data = s4_data

        self._rsoft_runner = self.create_rsoft_runner(self.variable_data, scan_tolerance)

    def run(self):
        self._success = self._rsoft_runner.compute(new_file=True)
        return self._success

    def read_efficiency(self):
        if not self._success:
            return None
        efficiency = self._rsoft_runner.read_efficiency(self.s4_data.get_order_sign())
        return efficiency


    def read_field(self):
        if not self._success:
            return None
        field_sp = self._rsoft_runner.read_fields_sp(self.get_theta_angle())
        field0 = field_sp[:, 0]
        field1 = field_sp[:, 1]
        return field1

    def create_rsoft_runner(self,variable_data, scan_tolerance):
        dir_name = 'run_test'
        if not scan_tolerance:
            runner = Rsoft_CLI(ind_file, prefix=dir_name, variable_data=variable_data, hide=True)
        else:
            tolerances = self.translate_tolerances(self.s4_data)
            runner = Rsoft_Scan_CLI(ind_file, prefix=dir_name, variable_data=variable_data, hide=True, tolerances = tolerances)
        return runner

    #range: if relative is False, is range of scan one way,
    #       if relative is True, range of scan in percents (divided by 100 inside the function)
    def compute_tolerance(self, step, range, value, relative):
        if not relative:
            abs_range = range
        else:
            abs_range = value*(range/100.0)
        amount_one_side = int(np.round(abs_range/step))
        int_range = step*amount_one_side
        _min = value-int_range
        _max = value+int_range
        _amount = 2*amount_one_side+1
        tolerence = scan_config(value*mm_2_micron,_min*mm_2_micron,_max*mm_2_micron,step*mm_2_micron,_amount)
        return tolerence


    def translate_tolerances(self, s4_data: S4_inputs):
        tolerance_data = dict()
        groove_width_tolerance = \
            self.compute_tolerance( step=self.s4_data.groove_step_interval,
                                    range = self.s4_data.groove_tolerance,
                                    value=(s4_data.period - s4_data.groove_width),
                                    relative=False)

        etching_depth_tolerance = \
            self.compute_tolerance( step=self.s4_data.etching_step_interval,
                                    range = self.s4_data.etching_tolerance_percent,
                                    value = self.s4_data.etching_depth,
                                    relative=True)

        tolerance_data['width1'] = groove_width_tolerance
        tolerance_data['h1'] = etching_depth_tolerance
        return tolerance_data


    def translate_to_rsoft(self, s4_data: S4_inputs):

        variable_data = dict()

        variable_data['delta1'] = np.real(complex(s4_data.refractive_index)) - 1
        variable_data['alpha'] = np.imag(complex(s4_data.refractive_index))

        # refractive index of the substrate
        variable_data['delta2'] = RefractiveIndices.sio2[s4_data.color_struct] - 1  # 0.4613#0.4586#refractive_index - 1

        variable_data['h1'] = s4_data.etching_depth * mm_2_micron
        variable_data['h2'] = 0.5 * mm_2_micron

        variable_data['free_space_wavelength'] = s4_data.color_struct.wavelength * mm_2_micron
        variable_data['period'] = s4_data.period * mm_2_micron
        variable_data['width1'] = (s4_data.period - s4_data.groove_width) * mm_2_micron

        pol, arg_s, arg_p = self.rsoft_polarization([s4_data.polarization_s, s4_data.polarization_p])
        variable_data['rcwa_launch_pol'] = pol
        variable_data['rcwa_launch_delta_phase'] = np.rad2deg(arg_p - arg_s)

        variable_data['launch_angle'] = np.rad2deg(s4_data.incident_angle_theta)

        phi_deg = np.rad2deg(s4_data.incident_angle_phi)
        variable_data['launch_theta'] = phi_deg
        variable_data['rcwa_tra_order_x'] = self.rsoft_output_orders(phi_deg)

        variable_data['rcwa_harmonics_x'] = config_harmonics  # ConfigManager.config.harmonics

        variable_data['air_in_depth'] = 0.5
        variable_data['air_out_depth'] = 0.5

        variable_data['rcwa_output_option'] = 1

        return variable_data

    def rsoft_polarization(self, polarization):
        s_polarization, p_polarization = polarization
        s_norm = np.real(np.sqrt(s_polarization * np.conj(s_polarization) + p_polarization * np.conj(p_polarization)))
        s_n = s_polarization / s_norm
        p_n = p_polarization / s_norm
        pol = np.rad2deg(np.arcsin(np.abs(s_n)))
        arg_p = np.angle(p_n)
        arg_s = np.angle(s_n)
        return pol, arg_s, arg_p

    # provide correct output orders for efficiency
    def rsoft_output_orders(self, phi_deg):
        order_sign = 2 * int(np.abs(phi_deg) > 90.0) - 1
        range_string = str(min(0, order_sign)) + ':' + str(max(0, order_sign))
        return range_string

    def get_theta_angle(self):
        return np.rad2deg(self.s4_data.incident_angle_phi)

    @staticmethod
    def kill_residuals():
        task_names = ['rsssmpichmpd.exe', 'dfmod.exe']
        for name in task_names:
            for p in psutil.process_iter(attrs=['pid', 'name']):
                if p.info['name'] == name:
                    os.system('taskkill /f /t /im ' + name)