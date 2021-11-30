# パパラメータ設定
# acsf作成
# csv作成
import os
import csv

import numpy as np

from n2p2.auto_sf.sfparamgen import SymFuncParamGenerator
from dscribe.descriptors import ACSF
from ase.io import read

class TwoBodyACSF:
    def __init__(self,species,r_cutoff,nb_param_pairs):
        self.species = species
        self.r_cutoff = r_cutoff
        self.nb_param_pairs = nb_param_pairs
        self.sf_params = self.get_two_body_parameters()

    def get_two_body_parameters(self,rule='imbalzano2018',mode='shift'):
        myGenerator = SymFuncParamGenerator(elements=self.species, r_cutoff=self.r_cutoff)
        myGenerator.symfunc_type = 'radial'
        myGenerator.generate_radial_params(rule=rule, mode=mode, nb_param_pairs=self.nb_param_pairs)

        with open('./tmp.txt', 'w') as f:
            myGenerator.write_parameter_strings(fileobj=f)
        with open('./tmp.txt') as f:
            l_strip = [s.strip() for s in f.readlines()]
        os.remove('./tmp.txt')
        l_strip = list(filter(None, l_strip))

        params = []
        for i, line in enumerate(l_strip):
            if i > self.nb_param_pairs-1:
                break
            line = list(filter(None, line.split(' ')))
            params.append([line[4],line[5]])

        return params

    def get_acsf_obj(self):
        params = self.sf_params

        acsf = ACSF(
            species=self.species,
            rcut=self.r_cutoff,
            g2_params=params,
            periodic=True,
        )
        return acsf

    def calc_acsf(self, xsf_file_path):
        acsf = self.get_acsf_obj()

        structure = read(xsf_file_path, format='xsf')
        structure_name = xsf_file_path.split('/')[-1].split('_')[1]
        structure_idx = xsf_file_path.split('/')[-1].split('_')[-1].split('.')[0]
        acsf_values = acsf.create_single(structure)
        print(acsf_values)
        csv_arr = []
        for num,sf_value in zip(structure.numbers,acsf_values):
            sf_value = sf_value.tolist()
            sf_value.insert(0,num)
            sf_value.insert(0,structure_idx)
            sf_value.insert(0,structure_name)
            # np.insert(sf_value,0,[structure_name,structure_idx,num])
            csv_arr.append(sf_value)
        return csv_arr

    def write_csv(self,output_dir_path,filename,data, write_header=False):
        with open(f'{output_dir_path}/{filename}.csv','a') as f:
            writer = csv.writer(f)
            if write_header:
                header = ['structure','structure_idx','center_atom']
                sf_header = ['G1']
                for param in self.sf_params:
                    eta = round(float(param[0]),2)
                    rs = round(float(param[1]),2)
                    sf_header.append(f'G2_{eta}_{rs}')
                # ２結合あるので2回追加
                header += sf_header
                header += sf_header
                writer.writerow(header)
            writer.writerows(data)










# tmp = TwoBodyACSF(['Si','O'],10,10)
# # tmp.get_two_body_parameters(['Si','O'],6,nb_param_pairs=10)
# tmp.calc_acsf('/Users/y1u0d2/desktop/Lab/Program/python/RDF/xsf/data_beta-quartz/data_beta-quartz_442.xsf')
