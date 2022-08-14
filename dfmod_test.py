import os
import numpy as np
import subprocess
import time
from shutil import copyfile

rsoft_bin = 'c:\\Synopsys\\PhotonicSolutions\\2021.09\\RSoft\\bin\\'
path_data = 'c:\\Data\\IND\\'
ind_file = 'base_3d_00.ind'
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
        self.init_dfmod()
        return self.run()


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
        p.wait()
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


    def init_dfmod(self):
        command_base = rsoft_bin + dfmod_exe + ' '
        cmd_dfmod = command_builder(command_base)
        #dfmod requires the filename to be before -hide
        if self.hide:
            cmd_dfmod.add_option('hide')
        cmd_dfmod.add_file(self.file_in)
        cmd_dfmod.add_name_value('prefix', self.prefix)
        for key, value in self.variable_data.items():
            cmd_dfmod.add_name_value(key, value)
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
        # upon license avaulability, the file size is zero
        if (os.path.getsize(file_out) > 0):
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

    def read_fields(self):
        orders = 20#ConfigManager.config.harmonics
        axes = ['x','y','z']

        field_1 = np.empty([3], complex)
        field_0 = np.empty([3], complex)
        for i in range(len(axes)):
            axe = axes[i]
            suffix = '_e' + axe + '_tra_coef'
            columns, names = self.read(suffix, return_names=False)
            columns = np.transpose(np.array(columns)[..., np.newaxis])
            #angles = columns[:,0]
            index1 = 2*orders-1
            index0 = 2*orders+1
            rs_1 = columns[:,index1] + 1j*columns[:,index1+1]
            rs_0 = columns[:,index0] + 1j*columns[:,index0+1]
            field_1[i] = rs_1
            field_0[i] = rs_0
        #np.savetxt("phi_x_y_z.csv", acc, delimiter=" ")

        return field_0, field_1

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
