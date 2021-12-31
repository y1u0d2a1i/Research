import glob
import os

from _lammps.structure_optimization import convert_xsf_to_lammps_data, setup, run_lmp
from _lammps.fix_orthogonal import fix_orthogonal

def calc_property(model, config, structure, path_to_target, run_file):
    """
    calculate property with nnp using lammps
    :param model: path to nnp-model
    :param config: path to config(property)
    :param structure: structure file
    :param path_to_target:
    :return:
    """
    convert_xsf_to_lammps_data(
        xsf_file=structure,
        path_to_save_dir=path_to_target,
        save_name='structure.data'
    )
    fix_orthogonal(
        path_to_target=f'{path_to_target}/structure.data'
    )
    setup(model, path_to_target, config)
    run_lmp(path_to_target, run_file)

if __name__ == '__main__':
    model = '/home/y1u0d2/Program/lammps/models/SiO2/04'
    config = '/home/y1u0d2/Program/lammps/scripts/elastic/20211220/config'
    path_to_root = '/home/y1u0d2/Program/lammps/scripts/elastic/20211220'

    structure_files = glob.glob('/home/y1u0d2/data/sio2-dft-data/*.cif')
    for file in structure_files:
        dirname = file.split('/')[-1]
        path_to_target = f'{path_to_root}/{dirname}'
        if not os.path.exists(path_to_target):
            os.mkdir(path_to_target)
        calc_property(model, config, file, path_to_target, 'in.elastic')


