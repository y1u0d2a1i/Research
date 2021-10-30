import os
import datetime
import shutil
import subprocess
import copy

from n2p2.auto_sf.sfparamgen import SymFuncParamGenerator

class n2p2TrainingFlow():
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def set_up(self, dir_name, original_data_dir=None):
        os.mkdir(f'{self.root_dir}/{dir_name}')
        if original_data_dir is None:
            original_data_dir = f'{self.root_dir}/original'
        shutil.copy(f'{original_data_dir}/input.nn.original', f'{self.root_dir}/{dir_name}/')
        shutil.copy(f'{original_data_dir}/input.data', f'{self.root_dir}/{dir_name}/')
        os.rename(f'{self.root_dir}/{dir_name}/input.nn.original', f'{self.root_dir}/{dir_name}/input.nn')
        return f'{self.root_dir}/{dir_name}'

    def set_up_sf(self, r_cutoff, nb_param_pairs, dir_name):
        myGenerator = SymFuncParamGenerator(elements=['O', 'Si'], r_cutoff=r_cutoff)
        myGenerator.symfunc_type = 'radial'
        myGenerator.generate_radial_params(rule='imbalzano2018', mode='shift', nb_param_pairs=nb_param_pairs)
        with open(f'{self.root_dir}/{dir_name}/input.nn', 'a') as f:
            myGenerator.write_settings_overview(fileobj=f)
            myGenerator.write_parameter_strings(fileobj=f)


    def run_n2p2(self,dir_name):
        os.chdir(f'{self.root_dir}/{dir_name}')
        # nnp-norm
        p = subprocess.Popen('nnp-norm', shell=True)
        p.wait()
        #nnp-scaling
        p = subprocess.Popen('mpirun -np 16 nnp-scaling 500', shell=True)
        p.wait()
        #nnp-train
        p = subprocess.Popen('mpirun -np 16 nnp-train', shell=True)
        p.wait()
        os.chdir(self.root_dir)

