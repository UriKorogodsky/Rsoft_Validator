from dfmod_test import *
from rcwa_excel_comparer import*


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_name_xls = 'c:\\Data\\15-09-2022_12_17_08.xlsx'
    #file_name_xls = 'c:\\Data\\18-09-2022_10_56_32_Narrow.xlsx'
    #file_name_xls = 'c:\\Data\\18-09-2022_12_09_38_Wide.xlsx'
    # file_name = '/home/urik/Data/16May_1800_double_pass_with_transparency.xlsx'

    # in case, the excel<->Rsoft checks are already done, and the files are available, set
    # the files_available=True, working on the prepared resuts. The recomputation may take 1 hour
    rcwa_parser = rcwa_excel_comparer(file_name_xls, files_available=False, scan_tolerance=False)

    variable_data = dict({'dimension':3})
    dir_name = 'run_' + dict_to_prefix(variable_data)
    #rsoft_runner = Rsoft_CLI(ind_file, prefix=dir_name,  variable_data = variable_data)
    #rsoft_runner.compute(new_file=True)