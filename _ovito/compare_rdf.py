# compare rdf of result of structure optimization and rdf of stable structure

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import csv
from ovito.io import import_file, export_file
from ovito.modifiers import CoordinationAnalysisModifier

from utils.constants.constants import Constants


# dump -> rdf (.txt)
def rdf_from_dump(path_to_dump, save_dir,rcut=15, bins=100):
    # Load a particle dataset, apply the modifier, and evaluate pipeline.
    if not os.path.exists(path_to_dump):
        raise Exception('no file')
        return
    pipeline = import_file(path_to_dump)
    modifier = CoordinationAnalysisModifier(cutoff=rcut, number_of_bins=bins, partial=True)
    pipeline.modifiers.append(modifier)

    rdf_table = pipeline.compute(pipeline.source.num_frames).tables['coordination-rdf']

    export_file(pipeline, f"{save_dir}/rdf.txt", "txt/table", key="coordination-rdf")
    convert_csv(path_to_txt=f"{save_dir}/rdf.txt", path_to_csv=save_dir)


# # dump -> rdf (.txt)
def rdf_from_xsf(path_to_xsf, save_dir, rcut, bins):
    # Load a particle dataset, apply the modifier, and evaluate pipeline.
    if not os.path.exists(path_to_xsf):
        raise Exception('no file')
        return
    save_filename = f"{path_to_xsf.split('/')[-1]}.csv"
    pipeline = import_file(path_to_xsf)
    modifier = CoordinationAnalysisModifier(cutoff=rcut, number_of_bins=bins, partial=True)
    pipeline.modifiers.append(modifier)

    rdf_table = pipeline.compute().tables['coordination-rdf']

    export_file(pipeline, f"{save_dir}/rdf.txt", "txt/table", key="coordination-rdf")
    convert_csv(path_to_txt=f"{save_dir}/rdf.txt", path_to_csv=save_dir, filename=save_filename)


# rdf(.txt) ->rdf (.csv)
def convert_csv(path_to_txt, path_to_csv, filename=None):
    if filename is None:
        filename = 'rdf.csv'
    with open(f'{path_to_csv}/{filename}', mode='w') as csv_f:
        with open(path_to_txt, mode='r') as f:
            l_strip = [s.strip() for s in f.readlines()]
            header = l_strip[1].split(' ')[-3:]
            header.insert(0, 'distance')
            writer = csv.writer(csv_f)
            writer.writerow(header)
            for line in l_strip[2:]:
                writer.writerow(line.split(' '))



if __name__ == '__main__':
    root_dir = '/Users/y1u0d2/desktop/Lab/result/lammps/structure-optimization/02'
    structures = Constants.structures()
    for structure in structures:
        dirs = glob.glob(f'{root_dir}/{structure}/*')
        for _dir in dirs:
            print(_dir)
            rdf_from_dump(
                path_to_dump=f'{_dir}/traj.dump',
                save_dir=_dir,
                rcut=15,
                bins=100
            )