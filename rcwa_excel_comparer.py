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

from Rsoft_tester import *

polarization_out_header = 'polarization_out'
rs_field_header = 'rs_field'
#rs_field_1_header = 'rs_field_1'
s4_efficiency_header = 'efficiency'
s4_tolerance_efficiency_header = 'tolerance_efficiency'

class rcwa_excel_comparer:
    def __init__(self, file_name, files_available, scan_tolerance):

        Rsoft_tester.kill_residuals()

        os.chdir(path_data)
        #self.test_optimizer = Optimizer_Unitest()
        #self.rcwa = Rcwa()
        self.file_name = file_name
        self.scan_tolerance = scan_tolerance
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
                        self.analyze_color(columns, c, sheet_name)
                except IOError:
                    print('File '+ file_name + ' not found, consider setting files_available flag')

    def analyze_color(self, columns, color, sheet_name):
        self.analyze_efficiency(columns, color, sheet_name)
        self.analyze_fields(columns, color, sheet_name)

    def analyze_efficiency(self, columns, color, sheet_name):
        rs_efficiency = np.array(columns['rs_efficiency']).astype(np.float)
        rs_efficiency_tolerance = np.array(columns['rs_efficiency_tolerance']).astype(np.float)
        s4_efficiency = np.array(columns[s4_efficiency_header]).astype(np.float)
        s4_efficiency_tolerance = np.array(columns[s4_tolerance_efficiency_header]).astype(np.float)
        diff_efficiency = rs_efficiency-s4_efficiency_tolerance

        s4_fields_str = np.array(columns[polarization_out_header])
        s4_fields = self.to_complex(s4_fields_str)

        thresh = 90
        percent = np.percentile(np.abs(diff_efficiency),thresh)

        fig, ax = plt.subplots(3, 1)
        plt.suptitle('Efficiency\n Component: '+ sheet_name +'\n Color: ' + color )
        plt.subplot(3, 1, 1)
        plt.title(str(thresh) + '%  <= ' + str(percent))
        plt.plot(rs_efficiency, 'r', linewidth=3)
        plt.plot(s4_efficiency_tolerance, 'b', linewidth=1)
        #plt.plot(s4_efficiency, 'g-', linewidth=1)
        plt.subplot(3, 1, 2)
        plt.plot(diff_efficiency, 'g-', linewidth=1)
        plt.subplot(3, 1, 3)
        plt.plot(100.0*np.abs((diff_efficiency)/s4_efficiency), 'b', linewidth=1)
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

    def analyze_fields(self, columns, color, sheet_name):
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

        fig, ax = plt.subplots(2, 1)
        plt.suptitle('Fields\n Component: '+ sheet_name +'\n Color: ' + color )
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

        plt.show()

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
                time_str = str(datetime.now().time())
                print(time_str + ' : ' + str(line_index) + '/' + str(len(matrix)))

        return results_S4_RS


    def process_line(self, ray_color, column_names, line_data):
        s4_data = S4_inputs( ray_color, column_names, line_data )
        order = s4_data.get_order_sign()

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
        out_S4_RS[s4_efficiency_header] = s4_data.s4_efficiency
        out_S4_RS[s4_tolerance_efficiency_header] = s4_data.s4_tolerance_efficiency

        compute_rsoft_tolerance = False
        result_rsoft_mean=0

        rsoft_tester = Rsoft_tester(s4_data, scan_tolerance=self.scan_tolerance)
        if not rsoft_tester.run():
            print('!!!!!!!!!!!! Something went wrong, check license !!!!!!!!!!!!!!!')
            return None
        efficiency_rsoft = rsoft_tester.read_efficiency()
        field_rsoft = rsoft_tester.read_field()

        field = field_rsoft[..., np.newaxis]

        out_S4_RS['rs_efficiency'] = efficiency_rsoft
        out_S4_RS['rs_efficiency_tolerance'] = result_rsoft_mean
        out_S4_RS[rs_field_header] = field
        return out_S4_RS

