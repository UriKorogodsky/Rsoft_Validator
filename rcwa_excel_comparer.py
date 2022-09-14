import csv
import pickle

import matplotlib.pyplot as plt
import pandas as pd
#from ddd.efficiency.rcwa import Rcwa
import numpy as np
from color import Color
#from ddd.efficiency.optimizer import *
from dfmod_test import *
from rcwa_test import *
from ast import literal_eval
from datetime import datetime
from collections import namedtuple

polarization_out_header = 'polarization_out'
rs_field_header = 'rs_field'
#rs_field_1_header = 'rs_field_1'
s4_efficiency_header = 'efficiency'


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



class rcwa_excel_comparer:
    def __init__(self, file_name, files_available):
        os.chdir(path_data)
        self.test_optimizer = Optimizer_Unitest()
        #self.rcwa = Rcwa()
        self.file_name = file_name
        self.xls = pd.ExcelFile(file_name)

        #in case, the excel<->Rsoft checks are already done, and the files are available, set
        # the files_available=True, working on the prepared resuts. The recomputation may take 1 hour
        if not files_available:
            self.process_xls()
        self.analyze()
        #plt.show(block=True)

    def process_xls(self):
        for sheet_name in self.xls.sheet_names:
            if (sheet_name[0] == 'f' or sheet_name == 'Config'):
                break

            print(sheet_name + ' start')
            plt.clf()
            plt.title(sheet_name)

            sheet = self.process_sheet(sheet_name)

            fig_manager = plt.get_current_fig_manager()
            fig_manager.window.showMaximized()
            plt.savefig(sheet_name + '.png', dpi=600)
            # plt.show(block=False)
            print(sheet_name + ' end')

    def analyze(self):
        for sheet_name in self.xls.sheet_names:
            if (sheet_name[0] == 'f'):
                break
            colors = ['green']
            for c in colors:
                file_name = self.make_file_name(sheet_name, c)
                try:
                    with open(file_name, 'r') as file:
                        reader = csv.DictReader(file)
                        columns = {}
                        for row in reader:
                            for fieldname in reader.fieldnames:
                                columns.setdefault(fieldname, []).append(row.get(fieldname))
                        plt.title(sheet_name)
                        self.analyze_color(columns)
                except IOError:
                    print('File '+ file_name + ' not found, consider setting files_available flag')

    def analyze_color(self, columns):
        self.analyze_efficiency(columns)
        self.analyze_fields(columns)

    def analyze_efficiency(self, columns):
        rs_efficiency = np.array(columns['rs_efficiency']).astype(np.float)
        rs_efficiency_tolerance = np.array(columns['rs_efficiency_tolerance']).astype(np.float)
        s4_efficiency = np.array(columns[s4_efficiency_header]).astype(np.float)
        diff_efficiency = rs_efficiency-s4_efficiency

        s4_fields_str = np.array(columns[polarization_out_header])
        s4_fields = self.to_complex(s4_fields_str)

        thresh = 90
        percent = np.percentile(np.abs(s4_efficiency-rs_efficiency),thresh)

        plt.subplot(3, 1, 1)
        plt.title(str(thresh) + '%  <= ' + str(percent))
        plt.plot(rs_efficiency, 'r', linewidth=1)
        plt.plot(s4_efficiency, 'g-', linewidth=1)
        plt.subplot(3, 1, 2)
        plt.plot(s4_efficiency-rs_efficiency, 'g-', linewidth=1)
        plt.subplot(3, 1, 3)
        plt.plot(100.0*np.abs((s4_efficiency-rs_efficiency)/s4_efficiency), 'b', linewidth=1)
        plt.show()


    def to_complex(self, str_array):
        str_array = np.array(str_array)
        str_array = np.array([s.replace('\n', ',') for s in str_array])
        complex_array=[]
        for s in str_array:
            vec = literal_eval(s)
            complex_array.append(np.array(vec))
        complex_array = np.array(complex_array)
        return complex_array

    def analyze_fields(self, columns):
        ##########################################
        #get bad line
        d_items = columns.keys()
        index = 0
        values_line = dict()
        for key in d_items:
            value = columns[key][index]
            values_line[key] = value

        ##########################################

        s4_polarization_out = np.squeeze(self.to_complex(columns['polarization_out']))
        rs_fields = np.squeeze(self.to_complex(columns['rs_field']))

        thresh = 90
        plt.subplot(2,1,1)
        plt.plot(np.abs(rs_fields[:,0]),'r')
        plt.plot(np.abs(s4_polarization_out[:,0]),'g')
        percent_s = np.percentile(np.abs(np.abs(rs_fields[:,0]) - np.abs(s4_polarization_out[:,0])), thresh)
        plt.title('S: '+ str(thresh) +'% <= ' + str(percent_s))

        plt.subplot(2,1,2)
        plt.plot(np.abs(rs_fields[:,1]),'r')
        plt.plot(np.abs(s4_polarization_out[:,1]),'b')
        percent_p = np.percentile(np.abs(np.abs(rs_fields[:,1]) - np.abs(s4_polarization_out[:,1])), thresh)
        plt.title('P: '+ str(thresh) + '% <= ' + str(percent_p))

        #angles_phi = np.squeeze(self.to_complex(columns['incident_angles_theta']))
        #s4_polarization_s = self.to_complex(columns['polarisation_s'])
        #s4_polarization_p = self.to_complex(columns['polarisation_p'])
        #rs_fields_0 = self.to_complex(columns[rs_field_0_header])

        #rs_fields_s = np.real(rs_fields)
        #rs_fields_p = np.imag(rs_fields)


        #rs_s4 = np.hstack([rs_fields,s4_polarization_out ])


        #amplitude_difference = np.abs(rs_fields) - np.abs(s4_polarization_out)
        #phase_difference = np.linalg.norm(np.angle(rs_fields) - np.angle(s4_polarization_out), axis=1)# % (2 * np.pi)

        #s4_difference = (np.angle(s4_polarization_out[:,0]) - np.angle(s4_polarization_out[:,1]))%(2 * np.pi)
        #rs_difference = (np.angle(rs_fields[:,0]) - np.angle(rs_fields[:,1]))% (2 * np.pi)

        #plt.plot(amplitude_difference[:,0], 'r', linewidth=1)
        #plt.plot(amplitude_difference[:,1], 'm', linewidth=1)
        #plt.plot(rs_fields_s, 'c.', linewidth=1)

        #plt.plot(rs_difference, 'b.', linewidth=1)
        #phase_diffs = s4_difference-rs_difference
        #plt.plot(phase_diffs, 'g.', linewidth=1)

        plt.show()

        #dummy operation, consider compute_field_delta or other math
        #diff = s4_polarization-rs_fields_1
        #return diff


    def make_file_name(self, sheet_name, c):
        file_name = sheet_name + '_' + c + '.csv'
        return file_name


    def process_sheet(self, sheet_name):
        sheet = pd.read_excel(self.xls, sheet_name)
        column_names = sheet.axes[1]
        matrix = sheet.values.tolist()

        ray_colors = [ 'green']
        for ray_color in ray_colors:
            print(ray_color)
            results_S4_RS = self.process_color(ray_color, column_names, matrix)

            file_name = self.make_file_name(sheet_name, ray_color)

            with open(file_name, 'w', newline='') as output_file:
                fc = csv.DictWriter(output_file,
                                    fieldnames=results_S4_RS[0].keys(),
                                    )
                fc.writeheader()
                fc.writerows(results_S4_RS)

            #file_name = sheet_name+'_' + c + '.csv'
            #np.savetxt(file_name, frame, fmt='%s,', header=header, comments='')
        #plt.show()
        return sheet


    def process_color(self, ray_color, column_names, matrix):
        results_S4_RS = list()
        step_lines = 1
        for line_index in range(0,len(matrix),step_lines):
            line_data = matrix[line_index]
            #if(np.isnan(line_data[0]) or line_data[0] == 0):
            #    break
            out_S4_RS = self.process_line(ray_color, column_names, line_data)

            results_S4_RS.append( out_S4_RS)
            if(line_index%10 == 0):
                print(str(line_index) + '/' + str(len(matrix)))

        return results_S4_RS


        #results_table = np.array(results_table)[..., np.newaxis]
        #rsoft_results = np.array(rsoft_results)[..., np.newaxis]
        #frame = np.concatenate([rsoft_results, results_table], axis=1)
        #the header is coupled with the structure, change accurately
        #header = 'rsoft, s4, s4_mean, table'

        #index_of_color = colors.index(color)
        #draw = True
        #if(draw):
        #    plt.subplot(3, 2, 2*index_of_color+1)
        #    #plt.plot(100.0*(np.array(results_table)-np.array(results_mean))/np.array(results_table), color[0], linewidth=1 )
        #
        #    plt.subplot(3, 2, 2*index_of_color+2)
        #    plt.plot(results_table, 'k', linewidth=1 )
        #    plt.plot(rsoft_results, color[0], linewidth=1 )
        #return frame, header



    #test delta computation , works correcyl against Igor's S4 wrapping
    def compute_field_delta(self, rs_field, table_polarization):

        paralellity = np.abs(np.cross(rs_field.T, table_polarization.T))
        phase_difference = (np.angle(rs_field) - np.angle(table_polarization))%(2*np.pi)
        print('Field diff= ' + str(np.linalg.norm(paralellity)) + ',' + str(np.linalg.norm(phase_difference-phase_difference[0])))
        return

    def process_line(self, ray_color, column_names, line_data):
        s4_data = S4_inputs( ray_color, column_names, line_data )
        #index_of_color = colors.index(color)
        #refractive_index = self.get_value_by_key('refractive_index', sheet_names, line_data)
        #refractive_index = refractive_indices;#self.get_value_by_key('refractive_index', sheet_names, line_data)

        #groove_width = self.get_value_by_key('groove_width', sheet_names, line_data)
        #etching_depth = self.get_value_by_key('etching_depth', sheet_names, line_data)
        #period = self.get_value_by_key('period', sheet_names, line_data)
        #color_struct = self.get_color(color)

        #polarisation_name = 'polarization'
        #polarisation_str = self.get_value_by_key(polarisation_name, sheet_names, line_data)
        #polarization = literal_eval(polarisation_str)

        #incident_angles_theta_name = 'incident_angle_theta'
        #incident_angles_theta = (self.get_value_by_key(incident_angles_theta_name, sheet_names, line_data))

        #incident_angles_phi_name = 'incident_angle_phi'
        #incident_angles_phi = (self.get_value_by_key(incident_angles_phi_name, sheet_names, line_data))
        #incident_angles = (incident_angles_theta, incident_angles_phi )

        #s4_efficiency_in_table = self.get_value_by_key( 'tolerance_efficiency', sheet_names, line_data)
        #current_color = self.get_value_by_key('element_color', sheet_names, line_data)

        #fixing incosistent separators issue in vector of complex numbers
        #polarization_out_str = self.get_value_by_key( polarization_out_header, sheet_names, line_data)
        #polarization_out_str = ''.join(polarization_out_str.splitlines())
        #polarization_out_str = polarization_out_str.strip()
        #polarization_out_str = polarization_out_str.replace('j','j,')
        #polarization_out = np.array(literal_eval(polarization_out_str))#[..., np.newaxis]

        order = s4_data.get_order()
        column_name = s4_data.get_test_string()

        out_S4_RS = dict()
        out_S4_RS['color'] = ray_color
        out_S4_RS['groove_width'] = s4_data.groove_width
        out_S4_RS['etching_depth'] = s4_data.etching_depth
        out_S4_RS['period'] = s4_data.period
        out_S4_RS['refractive_index'] = s4_data.refractive_index
        out_S4_RS['polarisation_s'] = s4_data.polarization_s
        out_S4_RS['polarisation_p'] = s4_data.polarization_p
        out_S4_RS['incident_angles_theta'] = np.rad2deg(s4_data.incident_angle_theta)
        out_S4_RS['incident_angles_phi'] = np.rad2deg(s4_data.incident_angle_phi)
        out_S4_RS[polarization_out_header] = s4_data.polarization_out
        out_S4_RS[s4_efficiency_header] = s4_data.s4_efficiency_in_table


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

        compute_rsoft_tolerance = False
        result_rsoft_mean=0
        if  True:# not compute_rsoft_tolerance:
            angles_rsoft, result_rsoft, field_0, field_1 = rsoft_compute(s4_data, column_name)#refractive_index, etching_depth, groove_width, period, color_struct,
                                                       #polarization, np.rad2deg(incident_angles_theta), np.rad2deg(incident_angles_phi),
                                                       #0, test_string)
        if False:#else :
            groove_step_interval = 0.000005
            groove_tolerance = 0.00001
            groove_elements = 2*int(groove_tolerance/groove_step_interval) + 1

            #etching_step_interval = 0.000005
            etching_step_interval = 0.00001
            etching_tolerance_percent = 10
            etching_tolerance = etching_depth*(etching_tolerance_percent/100.0)
            etching_elements = 2*int(etching_tolerance/etching_step_interval)+1

            axis_spread_groove = groove_width + np.linspace(-groove_tolerance, groove_tolerance, groove_elements)
            axis_spread_etching = np.linspace(etching_depth-etching_tolerance, etching_depth + etching_tolerance, etching_elements)
            groove_offsets, etching_offsets = np.meshgrid(axis_spread_groove, axis_spread_etching)

            groove_range = groove_offsets.flatten()
            etching_range = etching_offsets.flatten()

            num_of_points = len(groove_range)
            cost_main = np.zeros([num_of_points])

            for i in range(num_of_points):
                current_groove = groove_range[i]
                current_etching = etching_range[i]
                angles_rsoft, cost_rsoft, field_0_dummy, field_1_dummy = rsoft_compute(refractive_index, current_etching,
                                                                             current_groove, period, color_struct,
                                                                             polarization,
                                                                             np.rad2deg(incident_angles_theta),
                                                                             np.rad2deg(incident_angles_phi),
                                                                             0, test_string)
                cost_main[i] = cost_rsoft
            result_rsoft_mean = np.mean(cost_main)

        #print(s4_data.s4_efficiency_in_table, result_rsoft, result_rsoft_mean)
        #print(datetime.now().time())

        if(order == 1):
            field = field_1
        else:
            field = field_0

        field = field[..., np.newaxis]
        #field_1 = field_1[..., np.newaxis]

        self.compute_field_delta(rs_field=field,table_polarization=s4_data.polarization_out)

        out_S4_RS['rs_efficiency'] = result_rsoft
        out_S4_RS['rs_efficiency_tolerance'] = result_rsoft_mean
        out_S4_RS[rs_field_header] = field
        #out_S4_RS[rs_field_1_header] = field_1

        #difff = out_S4_RS[rs_efficiency_header] - out_S4_RS[rs_field_0_header]

        return out_S4_RS
        #return s4_efficiency_in_table, s4_result, mean_result

    #s4_result = rcwa_compute_single_angle(method, refractive_index, etching_depth, groove_width, period, color,
    #                                      polarization,
    #                                      angles_as_list, sidewall_angle)

