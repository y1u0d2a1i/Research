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
    
    def merge_base(self,csv_path, is_save=False, save_dir=None, save_file_name=None):
        df = pd.read_csv(f'{csv_path}')
        base_info = pd.read_csv(f'{self.base_path}/base_info.csv')

        is_structure_idx_plus = self.is_structure_idx_plus(df.structure_idx)
        if is_structure_idx_plus:
            df.structure_idx += 1

        if 'Unnamed: 0' in df.columns:
            df.drop('Unnamed: 0', inplace=True, axis=1)

        if 'name_of_structure' in df.columns:
            df = df.rename(columns={'name_of_structure': 'structure'})

        structures = df.structure.unique()
        for structure in structures:
            structure_idx_uni = df[df.structure == structure].structure_idx.unique()
            structure_idx_uni.sort()
            print(structure, structure_idx_uni[0], structure_idx_uni[-1], len(structure_idx_uni))

        df = pd.merge(df, base_info, on=['structure', 'structure_idx'])
        df['E_atom'] = df.E / df.natom

        if is_save:
            df.to_csv(f'{save_dir}/{save_file_name}.csv')

# obj = MergeBase()
# save_dir='/Users/y1u0d2/Desktop/Lab/result/rdf/rdf_base_csv'
# obj.merge_base('all_O-O.csv',is_save=True,save_dir=save_dir)
