import csv
import pickle

import matplotlib.pyplot as plt
import pandas as pd
#from ddd.efficiency.rcwa import Rcwa
import numpy as np
from color import Color
#from ddd.efficiency.optimizer import *
from dfmod_test import *
from tests.rcwa import *
from ast import literal_eval

class Optimizer_Unitest:
    def __init__(self):
        mu = 1 / 1_000  # micrometer
        axis_spread_groove = np.linspace(-0.015, 0.015, 5) * mu
        axis_spread_etching = np.linspace(0.95, 1.05, 5)
        self.groove_offsets, self.etching_offsets = np.meshgrid(axis_spread_groove, axis_spread_etching)


        segment_per_mm = 1
        #super().__init__(segment_per_mm)

        # We sample for values in several points so we have a big enough area with these values. because manufacturers
        # have a certain precision they can provide

    def efficiency_tolerance(self,order, refractive_index, etching_depth, groove_width, period, color_struct, polarization, incident_angles ):
        groove_range = (self.groove_offsets + groove_width).flatten()
        etching_range = (self.etching_offsets * etching_depth).flatten()

        num_of_points = len(groove_range)
        cost_main = np.zeros([num_of_points])

        for i in range(num_of_points):
            current_groove = groove_range[i]
            current_etching = etching_range[i]

            cost = self.get_efficiency(refractive_index=refractive_index,
                                        etching_depth=current_etching,
                                        groove_width=current_groove,
                                        period=period,
                                        color_struct=color_struct,
                                        polarization=polarization,
                                        incident_angles=incident_angles,
                                        order=order)


            #m = method(refractive_index=refractive_index,
            #           etching_depth=current_etching,
            #           groove_width=current_groove,
            #           period=period,
            #           color=color_struct,
            #           polarization=polarization,
            #           incident_angles=incident_angles,
            #           sidewall_angle=0)
            cost_main[i] = cost
        mean_efficiency = np.mean(cost_main)
        if(np.std(cost_main)>0.1):
            iii=9
        return  mean_efficiency , np.std(cost_main)

    #def get_efficiency(self,order, refractive_index, etching_depth, groove_width, period, color_struct, polarization, incident_angles):
    #    cost = self.rcwa.calculate_flux_by_order(
    #        refractive_index=refractive_index,
    #        etching_depth=etching_depth,
    #        groove_width=groove_width,
    #        period=period,
    #        color=color_struct,
    #        polarization=polarization,
    #        incident_angles=incident_angles,
    #        sidewall_angle=0,
    #        order=order
    #    )
    #    return cost

    #def segment_area_tolerance_efficiency(self, efficiency_method, income_ray_details: RayDetails, segment):
    #    groove_range = (self.groove_offsets + segment.line_width).flatten()
    #    etching_range = (self.etching_offsets * segment.etching_depth).flatten()3

    #   num_of_points = len(groove_range)
    #    cost_main = np.zeros([num_of_points])

    #    for i in range(num_of_points):
    #        current_groove = groove_range[i]
    #        current_etching = etching_range[i]

    #        m = efficiency_method(segment, income_ray_details, current_groove, current_etching)
    #        cost_main[i] = m

    #    # logger.info(
    #    #     f"{income_ray_details.color.name} - mean: {np.mean(cost_main)}, min: {np.min(cost_main)}, "
    #    #     f"index: {segment.refractive_index}, etching: {segment.etching_depth}, "
    #    #     f"groove: {segment.groove_width}, period: {segment.period}, "
    #    #     f"theta/phi: {income_ray_details.incident_angles}, s/p:{income_ray_details.polarization}"
    #    #     f" segment: {segment.incident_point_on_element()}"
    #    # )

    #    return np.mean(cost_main), np.std(cost_main)


#TODO
colors = [ 'red', 'green', 'blue']
refractive_indices = [ 2.129,  2.1824 ,  2.2478 ]

class rcwa_excel_parser:
    def __init__(self, file_name):
        self.test_optimizer = Optimizer_Unitest()
        #self.rcwa = Rcwa()
        self.file_name = file_name
        self.xls = pd.ExcelFile(file_name)
        for sheet_name in self.xls.sheet_names:
            if(sheet_name[0] == 'f'):
                break
            print(sheet_name + ' start')
            plt.clf()
            plt.title(sheet_name)
            sheet = self.process_sheet(sheet_name)
            fig_manager = plt.get_current_fig_manager()
            fig_manager.window.showMaximized()
            plt.savefig(sheet_name+'.png', dpi = 600)
            #plt.show(block=False)
            print(sheet_name + ' end')

        plt.show(block=True)



    def process_sheet(self, sheet_name):
        sheet = pd.read_excel(self.xls, sheet_name)
        sheet_names = sheet.axes[1]
        matrix = sheet.values.tolist()

        for c in colors:
            frame,header = self.process_color(c, sheet_names, matrix)
            file_name = sheet_name+'_' + c + '.csv'
            np.savetxt(file_name, frame, fmt='%s,', header=header, comments='')
        plt.show()
        return sheet


    def process_color(self, color, sheet_names, matrix):
        results_table = list()
        rsoft_results = list()
        for line_index in range(0,len(matrix), 20):
            line_data = matrix[line_index]
            if(np.isnan(line_data[0]) or line_data[0] == 0):
                break
            result_in_table, rsoft_result = self.process_line(color, sheet_names, line_data, line_index)

            results_table.append( result_in_table)
            rsoft_results.append(rsoft_result)

        results_table = np.array(results_table)[..., np.newaxis]
        rsoft_results = np.array(rsoft_results)[..., np.newaxis]
        frame = np.concatenate([rsoft_results, results_table], axis=1)
        #the header is coupled with the structure, change accurately
        header = 'rsoft, s4, s4_mean, table'

        index_of_color = colors.index(color)
        draw = True
        if(draw):
            plt.subplot(3, 2, 2*index_of_color+1)
            #plt.plot(100.0*(np.array(results_table)-np.array(results_mean))/np.array(results_table), color[0], linewidth=1 )

            plt.subplot(3, 2, 2*index_of_color+2)
            plt.plot(results_table, 'k', linewidth=1 )
            plt.plot(rsoft_results, color[0], linewidth=1 )

        return frame, header

    def get_value_by_key(self, key, sheet_names, line_data):
        inds = np.argwhere(sheet_names.values == key)
        if(inds.shape[0] == 0):
            return None
        index = int(inds[0])
        return line_data[index]

    def get_color(self, color):
        if(color == 'green'):
            return Color.green()
        if(color == 'blue'):
            return Color.blue()
        if(color == 'red'):
            return Color.red()
        raise KeyError(f'{color} is not red, green or blue.')

    def compute_field_delta(self, rs_field0, rs_field1, table_polarization, order):
        ex_0rs = rs_field0[0]
        ey_0rs = rs_field0[1]
        ez_0rs = rs_field0[2]

        ex_1rs = rs_field1[0]
        ey_1rs = rs_field1[1]
        ez_1rs = rs_field1[2]

        ex_0S4 = table_polarization[0]
        ey_0S4 = table_polarization[1]
        ez_0S4 = table_polarization[2]

        ex_1S4 = table_polarization[0]
        ey_1S4 = table_polarization[1]
        ez_1S4 = table_polarization[2]

        dxy0 = np.abs(ex_0rs * ey_0S4 - ey_0rs * ex_0S4)
        dxz0 = np.abs(ex_0rs * ez_0S4 - ez_0rs * ex_0S4)
        dyz0 = np.abs(ey_0rs * ez_0S4 - ez_0rs * ey_0S4)

        dxy1 = np.abs(ex_1rs * ey_1S4 - ey_1rs * ex_1S4)
        dxz1 = np.abs(ex_1rs * ez_1S4 - ez_1rs * ex_1S4)
        dyz1 = np.abs(ey_1rs * ez_1S4 - ez_1rs * ey_1S4)

        dxp0 = np.angle(ex_0rs) - np.angle(ex_0S4)
        dyp0 = np.angle(ey_0rs) - np.angle(ey_0S4)
        dzp0 = np.angle(ez_0rs) - np.angle(ez_0S4)

        dxp1 = np.angle(ex_1rs) - np.angle(ex_1S4)
        dyp1 = np.angle(ey_1rs) - np.angle(ey_1S4)
        dzp1 = np.angle(ez_1rs) - np.angle(ez_1S4)
        iii=9

    def process_line(self, color, sheet_names, line_data, line_num):

        #names = np.array(sheet_names.values)[..., np.newaxis]
        #values = np.array(line_data)[..., np.newaxis]
        #frame = np.concatenate([names, values], axis=1).T
        #file_name = 'vals.txt'
        #np.savetxt(file_name, frame, fmt='%s,')

        index_of_color = colors.index(color)
        refractive_index = refractive_indices[index_of_color];#self.get_value_by_key('refractive_index', sheet_names, line_data)
        groove_width = self.get_value_by_key('groove_width', sheet_names, line_data)
        etching_depth = self.get_value_by_key('etching_depth', sheet_names, line_data)
        period = self.get_value_by_key('period', sheet_names, line_data)
        color_struct = self.get_color(color)
        polarisation_s_str = self.get_value_by_key(color + '_polarization_s_in', sheet_names, line_data)
        if(polarisation_s_str is None):
            return

        polarization_s = complex(polarisation_s_str)

        polarization_p = complex(self.get_value_by_key(color + '_polarization_p_in', sheet_names, line_data))
        polarization = (polarization_s, polarization_p)

        incident_angles_theta = np.deg2rad(self.get_value_by_key(color + '_incident_angles_theta', sheet_names, line_data))

        incident_angles_phi = np.deg2rad(self.get_value_by_key(color + '_incident_angles_phi', sheet_names, line_data))
        incident_angles = (incident_angles_theta, incident_angles_phi )

        result_in_table =  self.get_value_by_key(color + '_efficiency', sheet_names, line_data)
        current_color = self.get_value_by_key('element_color', sheet_names, line_data)
        polarization_out_str = self.get_value_by_key(color + '_polarization_out', sheet_names, line_data)
        polarization_out_str = polarization_out_str.replace('j','j,')
        polarization_out_str = polarization_out_str.replace(' ','')
        polarization_out_str = polarization_out_str.replace('\n','')
        polarization_out = np.array(literal_eval(polarization_out_str))
        graph_index = index_of_color+1

        if (current_color == color):
            order = 1
            test_string = '10T'
        else:
            order = 0
            test_string = '00T'

        compute_tolerance = False
        mean_result = None
        if(compute_tolerance):
            mean_result, std_1 = self.test_optimizer.efficiency_tolerance(
                order=order,
                refractive_index=refractive_index,
                etching_depth=etching_depth,
                groove_width=groove_width,
                period=period,
                color_struct=color_struct,
                polarization=polarization,
                incident_angles=incident_angles)

        angles_rsoft, result_rsoft, field0, field1 = rsoft_compute(refractive_index, etching_depth, groove_width, period, color_struct,
                                                   polarization, np.rad2deg(incident_angles_theta), np.rad2deg(incident_angles_phi),
                                                   0, test_string)

        self.compute_field_delta(rs_field0=field0, rs_field1=field1, table_polarization=polarization_out, order=order)


        #        s4_result = self.test_optimizer.get_efficiency(order=order,
        #                                                refractive_index=refractive_index,
        #                                                etching_depth=etching_depth,
        #                                                groove_width=groove_width,
        #                                                period=period,
        #                                                color_struct=color_struct,
        #                                                polarization=polarization,
        #                                                incident_angles=incident_angles)

        #diff = mean_result-result_rsoft
        #print(1, result_rsoft, s4_result, mean_result, result_in_table)
            #if(abs(result_rsoft- result_in_table)>0.1):
            #    iii=9


        #            s4_result = self.rcwa.calculate_first_order_transmission(refractive_index=refractive_index,
#                                                                    etching_depth=etching_depth,
#                                                                    groove_width=groove_width,
#                                                                    period=period,
#                                                                    color=color_struct,
#                                                                    polarization=polarization,
#                                                                    incident_angles=incident_angles,
#                                                                    sidewall_angle=0)

            #delta = result_1 - result_in_table
            #plt.subplot(3, 1, graph_index)
            #plt.plot(line_num, result_in_table, color[0] + 'o')
            #plt.plot(line_num, result_1, 'k.')
            #plt.plot(line_num, mean_result, 'm.')
        #else:
        #    mean_result, std_0 = self.test_optimizer.efficiency_tolerance(order=0,
        #                                                                  refractive_index=refractive_index,
        #                                                                  etching_depth=etching_depth,
        #                                                                  groove_width=groove_width,
        #                                                                  period=period,
        #                                                                  color_struct=color_struct,
        #                                                                  polarization=polarization,
        #                                                                  incident_angles=incident_angles)
            #s4_0 = list()
            #s4_1 = list()
            #rsoft_0 = list()
            #rsoft_1 = list()
            #angles=list()
            #for angle in np.arange(40,50,0.1):
                #incident_angles = (np.deg2rad(angle), incident_angles[1])
            #s4_result = self.test_optimizer.get_efficiency(order=0,
            #                                               refractive_index=refractive_index,
            #                                               etching_depth=etching_depth,
            #                                               groove_width=groove_width,
            #                                               period=period,
            #                                               color_struct=color_struct,
            #                                               polarization=polarization,
            #                                               incident_angles=incident_angles)


            #angles_rsoft, result_rsoft = rsoft_compute(refractive_index, etching_depth, groove_width, period, color_struct,
            #                                           polarization, np.rad2deg(incident_angles_theta),  np.rad2deg(incident_angles_phi),
            #                                           #polarization, np.rad2deg(incident_angles_theta), np.rad2deg(incident_angles_phi),
            #                                           0, '00T')
            #if(False):
                #s4_result_1 = self.test_optimizer.get_efficiency(order=1,
                #                                               refractive_index=refractive_index,
                #                                               etching_depth=etching_depth,
                #                                               groove_width=groove_width,
                #                                               period=period,
                #                                               color_struct=color_struct,
                #                                               polarization=polarization,
                #                                               incident_angles=incident_angles)


                #angles_rsoft_1, result_rsoft_1 = rsoft_compute(refractive_index, etching_depth, groove_width, period, color_struct,
                #                                           polarization, angle,  np.rad2deg(incident_angles_phi),
                #                                           #polarization, np.rad2deg(incident_angles_theta), np.rad2deg(incident_angles_phi),
                #                                           0, '10T')

                #angles.append(angle)
                #s4_0.append(s4_result)
                #s4_1.append(s4_result_1)
                #rsoft_0.append(result_rsoft)
                #rsoft_1.append(result_rsoft_1)

            #plt.plot(angles, s4_0,'b')
            #plt.plot(angles, rsoft_0,'r')

            #plt.plot(angles, s4_1,'g')
            #plt.plot(angles, rsoft_1,'m')
            #plt.show()

            #diff = mean_result-result_rsoft
            #print(0, result_rsoft, s4_result, mean_result, result_in_table)
            #if(abs(result_rsoft- result_in_table)>0.1):
            #    iii=9

#            s4_result = self.rcwa.calculate_zero_order_transmission(refractive_index=refractive_index,
#                                                                          etching_depth=etching_depth,
#                                                                          groove_width=groove_width,
#                                                                          period=period,
#                                                                          color=color_struct,
#                                                                          polarization=polarization,
#                                                                          incident_angles=incident_angles,
#                                                                          sidewall_angle=0)


            #delta = result_0-result_in_table
            #plt.subplot(3, 1, graph_index)
            #plt.plot(line_num, result_in_table, color[0]+'x')
            #plt.plot(line_num, result_0, 'k.')
            #plt.plot(line_num, mean_result, 'm.')
        return result_in_table, result_rsoft
        #return result_in_table, s4_result, mean_result

    #s4_result = rcwa_compute_single_angle(method, refractive_index, etching_depth, groove_width, period, color,
    #                                      polarization,
    #                                      angles_as_list, sidewall_angle)
