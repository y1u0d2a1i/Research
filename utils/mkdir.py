import os
from utils.constants.constants import Constants

def mkdir_structure_dir(path_to_root):
    structures = Constants.structures()
    for structure in structures:
        os.mkdir(f'{path_to_root}/{structure}')