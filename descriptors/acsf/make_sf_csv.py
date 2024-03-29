"""
動径分布関数のCSVからACSFで説明変数作成
[eta, r_cut, r_s]を代入した基底を各列に作用させ、その和をそのパラメータでの説明変数とする
"""
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt

from descriptors.acsf.sf_function import SymmetryFunction

class MakeSfCsv:
    def __init__(self, out_path):
        self.out_path = out_path

    def make_sf_column(self,param,df,df_sf,start,end,center_atom,another_atom):
        acsf = SymmetryFunction()
        df_copy = df.copy()
        for num_column in df_copy.columns[start:end + 1]:
            # 4πr^2dr * sf
            df_copy[num_column] = df_copy[num_column] * 4 * np.pi * (float(num_column) **2) * 0.2 * \
                             acsf.radial_symmetry_function_2(eta=param[0], r_ij=float(num_column), r_shift=param[1], r_cutoff=param[2])
        df_sf[f'sf_{center_atom}-{another_atom}_e-{param[0]}_rs-{param[1]}'] = df_copy.iloc[:, start:end + 1].sum(axis=1)
        return df_sf

    def make_sf_csv(self, params, csv_path, output_filename):
        df = pd.read_csv(csv_path)
        has_structure = False
        if 'structure' in df.columns:
            has_structure = True
        df_sf = pd.DataFrame(df.another_atom)
        df_sf['center_atom'] = df.center_atom
        df_sf['structure_idx'] = df.structure_idx
        df_sf['structure'] = df.structure if has_structure else df.name_of_structure
        center_atom = df.center_atom.unique()[0]
        another_atom = df.another_atom.unique()[0]

        # インデックス取得
        arr = []
        for i, column in enumerate(df.columns):
            try:
                tmp = float(column)
                arr.append(i)
            except Exception as e:
                continue
        start = arr[0]
        end = arr[-1]

        self.plot_sf(params,f'{center_atom}-{another_atom}', self.out_path, f'sf_dist_{center_atom}-{another_atom}')
        for param in params:
            df_sf = self.make_sf_column(param, df, df_sf, start, end, center_atom, another_atom)

        df_sf.to_csv(f'{self.out_path}/{output_filename}.csv', index=False)

    def plot_sf(self, sf_parameters, bond, save_dir, save_filename):
        r_cut_list = [];
        for param in sf_parameters:
            r_cut_list.append(param[-1])
        r_cut = max(r_cut_list)
        acsf = SymmetryFunction()
        r_ij = np.linspace(0, r_cut, 100)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(f'symmetry function parameters {bond}')
        ax.set_xlabel(f'r(Å)')
        ax.set_ylabel(f'radial symmetry function : G2')
        for param in sf_parameters:
            ax.plot(r_ij,
                    [acsf.radial_symmetry_function_2(eta=param[0], r_ij=k, r_shift=param[1], r_cutoff=param[2]) for k in
                     r_ij], label=f'η: {param[0]} | Rs: {param[1]}')
        ax.legend()
        fig.show()
        fig.savefig(f'{save_dir}/{save_filename}.png')

if __name__ == '__main__':
    obj = MakeSfCsv('/Users/y1u0d2/Desktop/Lab/result/sf/sf_csv/atom')
    # params = [
    #     [4.143E+01, 6.000E-01, 6.000E+00],
    #     [2.614E+01, 7.554E-01, 6.000E+00],
    #     [1.649E+01, 9.509E-01, 6.000E+00],
    #     [1.041E+01, 1.197E+00, 6.000E+00],
    #     [6.567E+00, 1.507E+00, 6.000E+00],
    #     [4.143E+00, 1.897E+00, 6.000E+00],
    #     [2.614E+00, 2.389E+00, 6.000E+00],
    #     [1.649E+00, 3.007E+00, 6.000E+00],
    #     [1.041E+00, 3.786E+00, 6.000E+00],
    #     [6.567E-01, 4.766E+00, 6.000E+00],
    # ]
    params = [[6.629, 1.5, 15.0], [4.183, 1.888, 15.0], [2.639, 2.377, 15.0], [1.665, 2.993, 15.0], [1.051, 3.768, 15.0], [0.6629, 4.743, 15.0], [0.4183, 5.972, 15.0], [0.2639, 7.518, 15.0], [0.1665, 9.464, 15.0], [0.1051, 11.91, 15.0]]
    center_atom = 'Si'
    another_atom = 'Si'
    csv_path = f'/Users/y1u0d2/desktop/Lab/result/rdf/rdf_atom_all_converge_one/all_{center_atom}-{another_atom}.csv'
    obj.plot_sf(params,f'{center_atom}-{another_atom}',f'/Users/y1u0d2/Desktop/Lab/result/sf/sf_csv/atom',f'sf_dist_{center_atom}-{another_atom}')
    obj.make_sf_csv(params,csv_path,f'sf_{center_atom}-{another_atom}')








