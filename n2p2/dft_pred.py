import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import numpy as np
import glob
import csv

class AnalyzeCSV:
    """
    export 'dft energy  vs pred energy' from csv
    """
    def __init__(self,structure_dir):
        self.structure_dir = structure_dir

    def calc_rmse(self,dataframe,E_ref,E_pred):
        """
        calculate RMSE
        :param dataframe:
        :param E_ref:
        :param E_pred:
        :return:
        """
        rmse = np.sqrt(mean_squared_error(E_ref, E_pred))
        return rmse

    def get_structures(self, path_to_all_csv=None):
        if path_to_all_csv is None:
            path_to_all_csv = f'{self.structure_dir}/concat_all.csv'
        original_csv = pd.read_csv(path_to_all_csv)
        structures = original_csv['structure'].unique()
        return structures

    def add_column_to_csv(self, original_csv, diff=True):
        original_csv['E_ref_sio2'] = original_csv['E_ref']/(original_csv['natom']/3)
        original_csv['E_nnp_sio2'] = original_csv['E_nnp']/(original_csv['natom']/3)
        min_ref_energy = original_csv['E_ref_sio2'].min()
        if diff:
            original_csv['E_ref_sio2'] = original_csv['E_ref_sio2']-min_ref_energy
            min_nnp_energy = original_csv[original_csv['E_ref_sio2'] == original_csv['E_ref_sio2'].min()]['E_nnp_sio2']
            # min_nnp_energy = float(min_nnp_energy)
            original_csv['E_nnp_sio2'] = original_csv['E_nnp_sio2']-min_ref_energy

        original_csv['vol_sio2'] = original_csv['vol']/(original_csv['natom']/3)
        return original_csv

    def concat_csv(self, files,save_filename=None, is_save_csv=True, is_add_columns=True, diff=True):
        original_csv = pd.read_csv(files[0])
        for file in files[1:]:
            tmp = pd.read_csv(file)
            original_csv = pd.concat([original_csv,tmp], axis=0)

        if is_add_columns:
            original_csv = self.add_column_to_csv(original_csv, diff=diff)

        if is_save_csv:
            if save_filename is None:
                original_csv.to_csv(f'{self.structure_dir}/concat_all.csv')
            else:
                original_csv.to_csv(f'{self.structure_dir}/{save_filename}.csv')
        return original_csv

    def plot_training_data_distribution(self, original_csv):
        # 訓練データ分布
        structures = self.get_structures()
        fig, ax = plt.subplots(figsize=(8.0, 6.0))
        ax.set_xlabel("volume(Å^3/SiO2)")
        ax.set_ylabel("energy(eV/SiO2)")
        ax.set_title("reference : volume vs energy")

        for structure in structures:
            tmp = original_csv[original_csv.structure == f'{structure}']
            tmp = tmp.groupby('vol_sio2', as_index=False).min()
            ax.scatter(tmp['vol_sio2'], tmp['E_ref_sio2'], label=f"{structure}")
            ax.grid(True)
            ax.legend(loc=0)

        fig.savefig(f"{self.structure_dir}/pic/reference-vol-ene.png")

    def plot_training_data_distribution(self, original_csv):
        # 結果データ分布
        structures = self.get_structures()
        fig,ax = plt.subplots(figsize=(8.0, 6.0))
        ax.set_xlabel("volume(Å^3/SiO2)")
        ax.set_ylabel("energy(eV/SiO2)")
        ax.set_title("result : volume vs enstructures = self.get_structures()ergy")

        for structure in structures:
            tmp = original_csv[original_csv.structure == f'{structure}']
            tmp = tmp.groupby('vol_sio2',as_index=False).min()
            ax.scatter(tmp['vol_sio2'],tmp['E_nnp_sio2'],label=f"{structure}")
            ax.grid(True)
            ax.legend(loc=0)

        fig.savefig(f"{self.structure_dir}/pic/result-vol-ene.png")

    def plot_vol_ene(self, structure, original_csv):
        fig,ax = plt.subplots(figsize=(8.0, 6.0))
        ax.set_xlabel("volume(Å^3/SiO2)")
        ax.set_ylabel("energy(eV/SiO2)")
        ax.set_title(f"{structure} result : volume vs energy")

        tmp = original_csv[original_csv.structure == f'{structure}']

        tmp = tmp.groupby('vol_sio2',as_index=False).min()

        ax.scatter(tmp['vol_sio2'],tmp['E_ref_sio2'],label="ref")
        ax.scatter(tmp['vol_sio2'],tmp['E_nnp_sio2'],label="pred")
        ax.grid(True)
        ax.legend(loc=0)
        # plt.show()
        fig.savefig(f"{self.structure_dir}/pic/ref-result/{structure}-ref-result.png")

    def plot_dft_pred(self, structure, original_csv):
        fig, ax = plt.subplots(figsize=(8.0, 6.0))
        ax.set_xlabel("E_DFT")
        ax.set_ylabel("E_pred")
        ax.set_title(f"{structure} DFT vs prediction")

        tmp = original_csv[original_csv.structure == f'{structure}']

        rmse = self.calc_rmse(tmp, tmp['E_ref_sio2'], tmp['E_nnp_sio2'])
        mae = mean_absolute_error(tmp['E_ref_sio2'], tmp['E_nnp_sio2'])
        r2 = r2_score(tmp['E_ref_sio2'], tmp['E_nnp_sio2'])

        at = AnchoredText(f" RMSE : {format(rmse, '.3E')}\n MAE : {format(mae, '.3E')}\n R2 : {format(r2, '.3E')}",
                          prop=dict(size=15), frameon=True, loc='upper left')
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        ax.add_artist(at)

        ax.scatter(tmp['E_ref_sio2'], tmp['E_nnp_sio2'], label=f"{structure}")
        ax.grid(True)
        ax.legend(loc=0)
        # plt.show()
        fig.savefig(f"{self.structure_dir}/pic/dft-pred/{structure}-dft-pred.png")

    def export_error_csv(self, structures, original_csv):
        # エラーcsv出力
        error_arr = []
        for structure in structures:
            tmp = original_csv[original_csv.structure == f'{structure}']
            rmse = self.calc_rmse(tmp,tmp['E_ref_sio2'],tmp['E_nnp_sio2'])
            mae = mean_absolute_error(tmp['E_ref_sio2'],tmp['E_nnp_sio2'])
            r2 = r2_score(tmp['E_ref_sio2'],tmp['E_nnp_sio2'])
            error_arr.append([structure,str(format(rmse,'.3E')),str(format(mae,'.3E')),str(format(r2,'.3E'))])

        with open(f'{self.structure_dir}/error_info.csv','w') as f:
            f.write('structure,RMSE,MAE,R2 \n')
            writer = csv.writer(f)
            writer.writerows(error_arr)

    def run_this_func(self):
        files = glob.glob(f'{self.structure_dir}/csv/output*')

        original_csv = self.concat_csv(files)

        structures = self.get_structures()

        os.mkdir(f'{self.structure_dir}/pic')

        # 各構造のrefとnnpの比較
        os.mkdir(f'{self.structure_dir}/pic/ref-result')
        for structure in structures:
            self.plot_vol_ene(structure, original_csv)

        # 各構造のref vs pred
        os.mkdir(f'{self.structure_dir}/pic/dft-pred')
        for structure in structures:
            self.plot_dft_pred(structure, original_csv)

        self.export_error_csv(structures,original_csv)




