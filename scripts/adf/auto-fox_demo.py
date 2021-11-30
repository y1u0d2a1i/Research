import glob

from FOX import MultiMolecule, example_xyz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def adf_weight(x: np.ndarray) -> np.ndarray:
    x2 = np.array(x**2)
    return np.where(x2 == 0, 0, x/x2)

TARGET_DIR = '/Users/y1u0d2/desktop/Lab/result/adf'
OUTPUT_DIR = '/Users/y1u0d2/desktop/Lab/result/adf/wip'

xyz_files = glob.glob(f'{TARGET_DIR}/coord/*.xyz')
xyz_files.sort()
for file in xyz_files:
    mol = MultiMolecule.from_xyz(file)
    file_key = file.split('/')[-1].split('.')[0]
    with open(f'{TARGET_DIR}/lattice/{file_key}.txt') as f:
        lattice = [line.strip().split(' ') for line in f.readlines()]
        lattice = [list(map(float, vec)) for vec in lattice]
        lattice = np.array(lattice)
    mol.lattice = lattice
    adf = mol.init_adf(r_max=15,weight=adf_weight , atom_subset=('Si', 'O'), periodic='xyz')
    # dataframe 転置
    t_df = adf.T
    # t_df.columns += 1
    if 'phi  /  Degrees' in t_df.columns:
        t_df.drop(['phi  /  Degrees'], inplace=True)
    t_df.reset_index(inplace=True)
    t_df.rename(columns={
        'index': 'bond'
    }, inplace=True)
    structure = file_key.split('_')[0]
    idx = file_key.split('_')[1]
    t_df.insert(0, 'structure', structure)
    t_df.insert(0, 'structure_idx', idx)
    # t_df.to_csv(f'{OUTPUT_DIR}/{file_key}.csv')