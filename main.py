from dfmod_test import *
from rcwa_excel_parser import*

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_name = 'c:\\Data\\10Jul_1757_double_pass_with_transparency.xlsx'
    # file_name = '/home/urik/Data/16May_1800_double_pass_with_transparency.xlsx'
    rcwa_parser = rcwa_excel_parser(file_name)

    variable_data = dict({'dimension':3})
    dir_name = 'run_' + dict_to_prefix(variable_data)
    #rsoft_runner = Rsoft_CLI(ind_file, prefix=dir_name,  variable_data = variable_data)
    #rsoft_runner.compute(new_file=True)