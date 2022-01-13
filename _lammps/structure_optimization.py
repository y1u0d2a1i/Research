# convert xsf to lammps datafile using ovito api
import glob
import os
import random
import shutil
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ovito.io import export_file, import_file
from descriptors.base_info import get_reindex_base
from utils.constants.dir_path import DataDirPath
from utils.constants.constants import Constants
from _lammps.get_thermo_from_log import get_thermo_csv_from_log


def convert_xsf_to_lammps_data(xsf_file, path_to_save_dir, save_name):
    pipeline = import_file(xsf_file)
    export_file(pipeline, f'{path_to_save_dir}/{save_name}', 'lammps/data', atom_style='atomic')


def setup(model, path_to_target, path_to_config):
    shutil.copytree(model, f'{path_to_target}/nnp-data')
    files = glob.glob(f'{path_to_config}/*')
    for file in files:
        shutil.copy(file, path_to_target)


def run_lmp(path_to_target, run_file):
    os.chdir(path_to_target)
    if os.path.exists(f'{path_to_target}/nnp-data') and os.path.exists(f'{path_to_target}/{run_file}'):
        p = subprocess.Popen(f'mpirun -np 4 lmp_mpi -in {run_file}', shell=True)
        p.wait()
    else:
        raise FileNotFoundError('not sufficient')


def plot_opt(path_to_target, target_structure, natom, idx=None,savename=None, is_gpu=False, is_min=False):
    df = get_reindex_base(is_gpu=is_gpu)
    df['Vol_a'] = df['Vol'] / df['natom']
    df['E_a'] = df['E'] / df['natom']
    # 元データ
    tmp = df[df.structure == target_structure]
    if is_min:
        tmp = tmp.groupby('Vol').min()
    plt.figure(figsize=(10, 8))
    if idx is not None:
        plt.title(f'{target_structure}-{idx}: structure optimization')
    else:
        plt.title(f'{target_structure}: structure optimization')
    plt.xlabel('Vol/atom (ang^3)')
    plt.ylabel('Energy/atom (eV)')
    plt.scatter(tmp.Vol_a, tmp.E_a, color="blue")
    # thermo csv
    df_thermo = pd.read_csv(f'{path_to_target}/thermo_{natom}.csv')
    df_thermo['Vol_a'] = df_thermo.Volume / natom
    df_thermo['E_a'] = df_thermo.TotEng / natom
    plt.plot(df_thermo.Vol_a, df_thermo.E_a, lw=3, color="red")
    if savename is None:
        plt.savefig(
        f'{path_to_target}/{target_structure}.png')
    else:
        plt.savefig(
        f'{path_to_target}/{savename}.png')

if __name__ == '__main__':
    path_to_root = "/home/y1u0d2/Program/lammps/scripts/structure-optimization/02"
    path_to_model = "/home/y1u0d2/Program/lammps/models/SiO2/03"
    path_to_config = "/home/y1u0d2/Program/lammps/scripts/structure-optimization/02/config"
    is_gpu = True
    path_to_xsf = DataDirPath.xsf_gpu() if is_gpu else DataDirPath.xsf()

    # make directory
    structures = Constants.structures()
    for structure in structures:
        if not os.path.exists(f'{path_to_root}/{structure}'):
            os.mkdir(f'{path_to_root}/{structure}')

    for structure in structures:
        files = glob.glob(f'{path_to_xsf}/data_{structure}/*')
        files = random.sample(files, 10)
        for file in files:
            dir_name = file.split('/')[-1].split('.')[0]
            path_to_target = f'{path_to_root}/{structure}/{dir_name}'
            os.mkdir(path_to_target)
            convert_xsf_to_lammps_data(xsf_file=file, path_to_save_dir=path_to_target, save_name='structure.data')
            setup(model=path_to_model, path_to_target=path_to_target, path_to_config=path_to_config)
            try:
                run_lmp(path_to_target, run_file='opt.lmp')
                natom = get_thermo_csv_from_log(target_dir=path_to_target,
                                                output_dir=path_to_target)
                plot_opt(path_to_target, structure, natom, is_gpu=is_gpu)
            except Exception as e:
                print('failed to finish')
                continue


