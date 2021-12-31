import glob
import os
from _lammps.calc_property import calc_property
from utils.constants.constants import Constants

model = '/home/y1u0d2/Program/lammps/models/SiO2/04'
config = '/home/y1u0d2/Program/lammps/scripts/structure-optimization/04/config'
path_to_root = '/home/y1u0d2/Program/lammps/scripts/structure-optimization/04'

structures = Constants.structures()
for structure in structures:
    path = f'{path_to_root}/{structure}'
    if not os.path.exists(path):
        os.mkdir(path)
    structure_files = glob.glob(f'{path_to_root}/data/{structure}/*.xsf')
    for file in structure_files:
        dirname = file.split('/')[-1]
        path_to_target = f'{path}/{dirname}'
        if not os.path.exists(path_to_target):
            os.mkdir(path_to_target)
        calc_property(model, config, file, path_to_target, 'opt.lmp')