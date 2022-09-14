import os
import numpy as np
import subprocess
import time
from shutil import copyfile
from consts import *

rsoft_bin = 'c:\\Synopsys\\PhotonicSolutions\\2021.09\\RSoft\\bin\\'
path_data = 'c:\\Data\\IND\\'
ind_file = 'arc_sd1_18w052.ind'
dfmod_exe = 'dfmod'
most_exe = 'rsmost'

class command_builder:
    def __init__(self, command):
        self.command = command
        self.arguments = []

    def add_file(self, file):
        self.arguments.append(file)

    def add_option(self, name, value=None):
        option = ' -' + name + ' '
        if(value is not None):
            option += value + ' '
        self.arguments.append(option)

    def add_name_value(self, name, value):
        option = ' ' +  name + '=' + str(value) + ' '
        self.arguments.append(option)

    def arg_string(self):
        string = ''
        for arg in self.arguments:
            string+=arg
        return string


class Rsoft_CLI:
    def __init__(self, file_in, prefix, variable_data, hide):
        self.file_in = file_in
        self.prefix = prefix
        self.variable_data= variable_data
        self.hide = hide

        #UBUNTU stuff
        #self.init_environment()

    def compute(self, new_file):
        if(new_file):
            self.file_in = self.save_ind()

        self.make_scan()
        ######################
        #self.configure_scan(self.file_in, 'h1', 0.5, 0.7, None, 11)
        #self.configure_scan(self.file_in, 'width1', 0.1, 0.2, None, 5)
        #######################

        self.init_dfmod()
        return self.run()

    def make_scan(self):
        rs_field_name_width = 'width1'
        rs_field_name_height = 'h1'

        self.make_scan_per_param(rs_field_name_width)
        self.make_scan_per_param(rs_field_name_height)

    def make_scan_per_param(self, param_name):
        param_center = self.variable_data[param_name]
        delta = 0.01
        param_min = param_center - delta
        param_max = param_center + delta

        self.insert_scan(self.file_in, param_name, param_min, param_max, None, 5)



    def save_ind(self):
        process_command = self._build_rsmost_command()
        file_name = self._run_rsmost_command(process_command)

        return file_name

    def _build_rsmost_command(self):
        command_base = rsoft_bin + most_exe
        cmd_save = command_builder(command_base)
        #rsmost requires the filename to be before -hide
        cmd_save.add_file(self.file_in)
        cmd_save.add_option('hide')
        cmd_save.add_option('prefix', self.prefix)
        for key, value in self.variable_data.items():
            cmd_save.add_name_value(key, value)

        os.chdir(path_data)
        # os.system(command)
        process_command = [ command_base]
        process_command += cmd_save.arguments
        return process_command

    #originally due to rsmost constraints, the new ind file is created in
    #..._work subfolder. Use flag copy_to_root, in odred to copy
    # the file into the main working folder
    def _run_rsmost_command(self, process_command, copy_to_root = True):
        p = subprocess.Popen(process_command)
        p.wait(5)
        #time.sleep(1)
        #in Windows no need to kill, the wait() works ok
        #os.system('taskkill /f /t /im ' + str(p.pid))
        new_folder = self.prefix + '_work' + '//raw//'
        file_name = new_folder + self.prefix + '.ind'

        if(copy_to_root):
            new_file_name = self.prefix + '.ind'
            copyfile(file_name, new_file_name)
            file_name = new_file_name

        return file_name

    def build_scan_line(self, var_name, min, max, step, amount):
        if step == None:
            str_step = ' '
        else:
            str_step = str(step)
        result = 'SYMTAB_SCALAR ' + var_name + ' Y :  IV_LINEAR_STEPS : ' + str(min)+ ' : ' + str(max) + ' : ' + str_step  + ' : ' + str(amount) + ' :  :  :\n'
        return result

    def set_or_add_scan(self, lines, var_name, min, max, step, amount):
        new_line = self.build_scan_line(var_name, min, max, step, amount)
        #if exactly same variable exists, we gonna replace it
        id_exact = self.get_line(lines, 'SYMTAB_SCALAR', var_name)
        if(id_exact == None):
            #if just symtab_scalar exists, we would add the line after it
            id_other_name = self.get_line(lines, 'SYMTAB_SCALAR', None)
            lines.insert(id_other_name,new_line)
        else:
            lines[id_exact] = new_line

        id_to_remove = self.get_line(lines, 'SYMTAB_SCALAR', 'background_index')
        if(id_to_remove is not None):
            del lines[id_to_remove]

        return lines

    #looking for entire field name, adding spaces before and after
    def get_line(self, lines, id1, id2):
        if(id2 is not None):
            id2_padded = ' ' + id2 + ' '
        else:
            id2_padded = id2
        for num in range(len(lines)):
            line = lines[num]
            if(id1 in line):
                if(id2_padded is None):
                    return num
                else:
                    if(id2_padded in line):
                        return num
        return None


    def insert_scan(self, file_name, var_name, min, max, step, amount):
        conf = {}
        with open(file_name) as fp:
            lines = list()
            in_var_section = False
            after_var_section = False
            for line in fp:
                lines.append(line)

            lines = self.set_or_add_scan(lines, var_name, min, max, step, amount)

        f = open(file_name, "w")
        for line in lines:
            f.write(line)
        f.close()
        return

    def init_dfmod(self):
        command_base = rsoft_bin + 'dfmod' + ' '
        cmd_dfmod = command_builder(command_base)
        #dfmod requires the filename to be before -hide
        if self.hide:
            cmd_dfmod.add_option('hide')
        cmd_dfmod.add_file(self.file_in)
        cmd_dfmod.add_name_value('prefix', self.prefix)
        #for key, value in self.variable_data.items():
        #    cmd_dfmod.add_name_value(key, value)
        self.command = command_base + cmd_dfmod.arg_string()
        #print(self.command)
        #os.system(command)

    def add_pair(self, name, value):
        name_value = ' ' + name + '=' + str(value) + ' '
        self.command+=name_value

    def run(self):
        os.chdir(path_data)
        file_out = 'tmp_out.out'
        res = os.system(self.command + ' > ' + file_out)
        # if something is wrong, there is a fresh message in the file
        # upon license availability, the file size is zero
        if (os.path.getsize(file_out) > 0):
            print('License issue, please replug the dongle or restart the computer')
            fid = open(file_out, "r")
            readfile = fid.read()
            licens_problem_string = 'licensing error'
            if licens_problem_string in readfile:
                fid.close()
                return False

        return True


    #def read(self):
    #    file_name= self.prefix+'.dat'
    #    columns = np.loadtxt(file_name, unpack = True)
    #    names = np.genfromtxt(file_name, names=True, max_rows=1).dtype.names
    #    return columns, names


    def read(self, suffix='', return_names = True):
        file_name= self.prefix+suffix+'.dat'
        columns = np.loadtxt(file_name, unpack = True)
        names=None
        if return_names:
            names = np.genfromtxt(file_name, names=True, max_rows=1).dtype.names
        return columns, names

    def read_field(self, axe_name, harmonics ):
        suffix = '_e' + axe_name + '_tra_coef'
        columns, names = self.read(suffix, return_names=False)
        columns = np.transpose(np.array(columns)[..., np.newaxis])
        # angles = columns[:,0]
        index1 = 2 * harmonics - 1
        index0 = 2 * harmonics + 1
        rs_1 = columns[:, index1] + 1j * columns[:, index1 + 1]
        rs_0 = columns[:, index0] + 1j * columns[:, index0 + 1]
        return rs_0, rs_1

    def read_fields_xyz(self):
        orders = config_harmonics #ConfigManager.config.harmonics
        axes = ['x','y','z']

        field_1 = np.empty([len(axes)], complex)
        field_0 = np.empty([len(axes)], complex)
        for i in range(len(axes)):
            axe = axes[i]
            rs_0, rs_1 = self.read_field(axe, orders)
            field_1[i] = rs_1
            field_0[i] = rs_0
        return field_0, field_1

    def read_fields_sp(self):
        orders = config_harmonics #ConfigManager.config.harmonics
        axes = ['s','p']

        fields_sp = np.empty((2,2),complex)
        for i in range(len(axes)):
            axe = axes[i]
            rs_0, rs_1 = self.read_field(axe, orders)
            fields_sp[i,:] = [rs_0, rs_1]
        for order in range(2):
            fields_sp[:,order] /= np.linalg.norm(fields_sp[:,order])
        return fields_sp

def dict_to_prefix(dict):
    string = ''
    for key, value in dict.items():
        string+=key
        string+='_'
        string+=str(value)
        #string+='__'
    return string



#rsoft_runner.add_pair('Period', 0.52)



#rsoft_runner.run()
#rsoft_runner.read()

#a = read_file(path_data+ind_file)

#command = path_bin+'dfmod.exe' + ' -hide -c -v2 ' + path_data+ind_file +  ' prefix=run2 Period=0.52 ' +  ' new_ind.ind'
#os.system(command)
#print('finish')
