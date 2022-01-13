import glob

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv

from ovito.io import import_file, export_file
from ovito.modifiers import BondAnalysisModifier, CreateBondsModifier

from utils.constants.dir_path import DataDirPath
from utils.constants.constants import Constants


def calc_adf(path_to_output,cutoff=10):
    xsf = DataDirPath.xsf()
    dirs = glob.glob(f'{xsf}/data_*')
    # path_to_output = "/Users/y1u0d2/desktop/Lab/result/adf/ovito/out_txt"
    for _dir in dirs:
        files = glob.glob(f'{_dir}/data_*')
        structure = _dir.split('/')[-1].split('_')[-1]
        if not structure in Constants.structures():
            print(f'invalid structure: {structure}')
            break
        for xsf_file in files:
            structure_idx = xsf_file.split('/')[-1].split('.')[0].split('_')[-1]
            pipeline = import_file(xsf_file)
            pipeline.modifiers.append(CreateBondsModifier(cutoff=cutoff))
            pipeline.modifiers.append(
                BondAnalysisModifier(partition=BondAnalysisModifier.Partition.ByParticleType))
            # data = pipeline.compute()
            export_file(pipeline, f'{path_to_output}/{structure}/{structure}_{structure_idx}.txt', 'txt/table', key='bond-angle-distr')

def convert_txt_to_csv(txt_file, path_to_output, structure, structure_idx):
    with open(txt_file, mode='r') as f:
        l_strip = [s.strip() for s in f.readlines()][1:]
        with open('./wip.csv', mode='w') as cf:
            for i, line in enumerate(l_strip):
                line = line.split(' ')[1:] if i == 0 else line.split(' ')
                writer = csv.writer(cf)
                writer.writerow(line)
    df = pd.read_csv('./wip.csv', index_col='Angle')
    df = df.T
    df.insert(0, 'structure', structure)
    df.to_csv(f'{path_to_output}/{structure}_{structure_idx}.csv')

def divide_by_natom():
    from utils.constants.constants import Constants
    import glob

    csv_path = '/Users/y1u0d2/desktop/Lab/result/adf/ovito/csv'
    structures = Constants.structures()
    all_path = []
    for structure in structures:
        files = glob.glob(f'{csv_path}/{structure}/*')
        for file in files:
            all_path.append(file)
    print(len(all_path))
    df = pd.read_csv(all_path[0])
    for file in all_path[1:]:
        print(file)
        df_tmp = pd.read_csv(file)
        df = pd.concat([df, df_tmp])

if __name__ == '__main__':
    txt_dir = '/Users/y1u0d2/desktop/Lab/result/adf/ovito/out_txt'
    path_to_output = '/Users/y1u0d2/desktop/Lab/result/adf/ovito/csv'
    calc_adf(path_to_output=path_to_output, cutoff=3)
    # dirs = glob.glob(f'{txt_dir}/*')
    # for _dir in dirs:
    #     structure = _dir.split('/')[-1]
        # files = glob.glob(f'{_dir}/*.txt')
        # for txt_file in files:
        #     structure_idx = txt_file.split()
        #     convert_txt_to_csv(txt_file,
        #                        path_to_output=f'{path_to_output}/{structure}',
        #                        structure=structure,
        #                        structure_idx= txt_file.split('/')[-1].split('.')[0].split('_')[-1]
        #                        )
