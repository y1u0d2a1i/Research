from utils.constants.dir_path import DataDirPath
import pandas as pd

class MergeBase:
    def __init__(self):
        self.base_path = DataDirPath.base_structure_info()
        self.rdf_dir_path = DataDirPath.rdf_result()

    def is_structure_idx_plus(self, structure_idx_list):
        is_structure_idx_plus = False
        idx = structure_idx_list.unique()
        idx.sort()
        if idx[0] == 0:
            is_structure_idx_plus = True
        return is_structure_idx_plus
    
    def merge_base(self,rdf_csv_name):
        df = pd.read_csv(f'{self.rdf_dir_path}/all/{rdf_csv_name}')
        base_info = pd.read_csv(f'{self.base_path}/base_info.csv')

        is_structure_idx_plus = self.is_structure_idx_plus(df.structure_idx)
        if is_structure_idx_plus:
            df.structure_idx += 1

        structures = df.name_of_structure.unique()
        structures
        for structure in structures:
            structure_idx_uni = df[df.name_of_structure == structure].structure_idx.unique()
            structure_idx_uni.sort()
            print(structure, structure_idx_uni[0], structure_idx_uni[-1], len(structure_idx_uni))

        if 'Unnamed: 0' in df.columns:
            df.drop('Unnamed: 0', inplace=True, axis=1)

        if 'name_of_structure' in df.columns:
            df = df.rename(columns={'name_of_structure': 'structure'})

        df = pd.merge(df, base_info, on=['structure', 'structure_idx'])
        df['E_atom'] = df.E / df.natom
