import pandas as pd
import numpy as np
import os
import subprocess

from distutils.dir_util import copy_tree
from utils.convert_csv import ConvertCsv


class InterAtomicPotential():
    def __init__(self, root_dir, r_from, r_to, space=50, species=('Si', 'O')):
        self.root_dir = root_dir
        self.r_from = r_from
        self.r_to = r_to
        self.space = space
        self.species = species

    def set_up_predict(self, dir_name):
        target_dir = f'{self.root_dir}/{dir_name}'
        original_dir = f'{self.root_dir}/original'
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        if not os.path.exists(original_dir):
            print('please make original folder')
            return
        else:
            copy_tree(original_dir, target_dir)

    def make_structure(self, target_dir, distance):
        with open(f'{target_dir}/input.data', 'w') as f:
            f.write('begin \n')
            lattice = [
                'lattice 1000 0.0 0.0 \n',
                'lattice 0.0 1000 0.0 \n',
                'lattice 0.0 0.0 1000 \n',
            ]
            f.writelines(lattice)
            atom = [
                f'atom 500 500 500 {self.species[0]} 0.0 0.0 0.0 0.0 0.0 \n'
                f'atom 500 {500 + distance} 500 {self.species[1]} 0.0 0.0 0.0 0.0 0.0 \n'
            ]
            f.writelines(atom)
            f.write('energy 0.0 \n')
            f.write('charge 0.0 \n')
            f.write('end \n')
    # make dir and copy from original

    # run nnp-predict
    def run_nnp_predict(self, target_dir):
        os.chdir(target_dir)
        p = subprocess.Popen('nnp-predict 1', shell=True)
        p.wait()
        os.chdir(self.root_dir)

    # get energy from energy.out
    def get_enery(self, target_dir):
        if not os.path.exists(f'{target_dir}/energy.out'):
            print('no energy.out')
            return
        else:
            obj = ConvertCsv(target_dir=target_dir, output_dir=target_dir)
            obj.convert_n2p2_output_to_csv(header_index=11, target_file='energy.out')
            df = pd.read_csv(f'{target_dir}/energy.out.csv')
            energy = df.iat[0,0]
            return energy

    # conduct all flow
    def flow(self):
        r_from = self.r_from
        r_to = self.r_to
        r_space = self.space
        species = self.species
        distance_list = np.linspace(r_from, r_to, r_space)
        energy_df = pd.DataFrame(columns=['distance', 'energy', 'center', 'another'])
        for i, distance in enumerate(distance_list):
            distance = round(distance, 3)
            dir_name = f'nnp-predict_{distance}'
            target_dir = f'{self.root_dir}/{dir_name}'
            self.set_up_predict(dir_name)
            self.make_structure(target_dir=target_dir, distance=distance)
            self.run_nnp_predict(target_dir=target_dir)
            energy = self.get_enery(target_dir=target_dir)
            energy_df.loc[f'{i}'] = [distance, energy, species[0], species[1]]
        energy_df.to_csv(f'{self.root_dir}/two-body_{species[0]}_{species[1]}.csv', index=False)


if __name__ == "__main__":
    obj = InterAtomicPotential(
        root_dir='/home/y1u0d2/Program/n2p2/interatomic/01',
        r_from=0.5,
        r_to=15,
        space=50,
        species=('Si', 'O')
    )
    obj.flow()

