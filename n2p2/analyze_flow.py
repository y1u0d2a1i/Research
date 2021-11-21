import glob
import os
import csv
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils.convert_csv import ConvertCsv
from descriptors.base_info import get_reindex_base


class N2p2AnalyzeFlow():
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def make_analyze_dir(self):
        path = f'{self.dir_path}/analyze'
        if not os.path.exists(path):
            os.mkdir(path)

    def convert_test_train_csv(self):
        test_files = glob.glob(f'{self.dir_path}/testpoints.0000*')
        train_files = glob.glob(f'{self.dir_path}/trainpoints.0000*')
        if test_files and train_files:
            obj = ConvertCsv(output_dir=f'{self.dir_path}/analyze', target_dir=self.dir_path)
            for test_file_path, train_file_path in zip(test_files, train_files):
                test_file = pd.read_csv(test_file_path)
                train_file = pd.read_csv(train_file_path)
                out_test_file_name = test_file_path.split('/')[-1]
                out_train_file_name = train_file_path.split('/')[-1]
                # csvファイルに変換
                obj.convert_n2p2_output_to_csv(10, out_test_file_name, f'{out_test_file_name}')
                obj.convert_n2p2_output_to_csv(10, out_train_file_name, f'{out_train_file_name}')

    def get_test_score(self, df_test_new):
        # テストに対して
        mae_test = mean_absolute_error(df_test_new['Eref'], df_test_new['Ennp'])
        mse_test = mean_squared_error(df_test_new['Eref'], df_test_new['Ennp'])
        rmse_test = np.sqrt(mse_test)
        r2_test = r2_score(df_test_new['Eref'], df_test_new['Ennp'])
        print('TEST')
        print(f'mae:{mae_test}, mse:{mse_test}, rmse:{rmse_test}, r2:{r2_test}')
        return ['test', mae_test, mse_test, rmse_test, r2_test]

    def get_train_score(self, df_train_new):
        # 訓練データに対して
        mae_train = mean_absolute_error(df_train_new['Eref'], df_train_new['Ennp'])
        mse_train = mean_squared_error(df_train_new['Eref'], df_train_new['Ennp'])
        rmse_train = np.sqrt(mse_train)
        r2_train = r2_score(df_train_new['Eref'], df_train_new['Ennp'])
        print('TRAIN')
        print(f'mae:{mae_train}, mse:{mse_train}, rmse:{rmse_train}, r2:{r2_train}')
        return ['train', mae_train, mse_train, rmse_train, r2_train]

    def write_score_csv(self, epoch, test_score, train_score):
        test_score.insert(0, epoch)
        train_score.insert(0, epoch)
        with open(f'{self.dir_path}/analyze/score.csv', 'a') as f:
            writer = csv.writer(f)
            if epoch == 0:
                writer.writerow(['epoch', 'type', 'MAE', 'MSE', 'RMSE', 'R2'])
            writer.writerow(test_score)
            writer.writerow(train_score)


if __name__ == '__main__':
    dir_path = '/Users/y1u0d2/Desktop/Lab/result/nnp-train/two-body/for_angular/nnp-train_10_10'
    analyze_flow = N2p2AnalyzeFlow(dir_path)
    analyze_flow.make_analyze_dir()
    analyze_flow.convert_test_train_csv()
    base_df = get_reindex_base()
    all_test_csv = glob.glob(f'{dir_path}/analyze/testpoints*')
    all_train_csv = glob.glob(f'{dir_path}/analyze/trainpoints*')
    all_test_csv.sort()
    all_train_csv.sort()
    for i, (test_csv, train_csv) in enumerate(zip(all_test_csv, all_train_csv)):
        epoch = i
        df_test = pd.read_csv(test_csv)
        df_train = pd.read_csv(train_csv)
        df_test_new = pd.merge(df_test, base_df, left_on='index', right_on='structure_idx')
        df_train_new = pd.merge(df_train, base_df, left_on='index', right_on='structure_idx')
        test_score = analyze_flow.get_test_score(df_test_new)
        train_score = analyze_flow.get_train_score(df_train_new)
        analyze_flow.write_score_csv(epoch, test_score, train_score)
