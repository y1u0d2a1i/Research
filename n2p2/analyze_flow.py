import glob
import os
import csv
import pandas as pd
import numpy as np
import shutil
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils.convert_csv import ConvertCsv
from descriptors.base_info import get_reindex_base


class N2p2AnalyzeFlow():
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def make_analyze_dir(self):
        path = f'{self.dir_path}/analyze'
        if os.path.exists(path):
            files = glob.glob(f'{path}/*.csv')
            for file in files:
                os.remove(file)
        else:
            os.mkdir(path)

    def convert_test_train_csv(self):
        test_files = glob.glob(f'{self.dir_path}/testpoints.0000*')
        train_files = glob.glob(f'{self.dir_path}/trainpoints.0000*')
        if test_files and train_files:
            obj = ConvertCsv(output_dir=f'{self.dir_path}/analyze', target_dir=self.dir_path)
            for test_file_path, train_file_path in zip(test_files, train_files):
                out_test_file_name = test_file_path.split('/')[-1]
                out_train_file_name = train_file_path.split('/')[-1]
                # csvファイルに変換
                obj.convert_n2p2_output_to_csv(10, out_test_file_name, f'{out_test_file_name}')
                obj.convert_n2p2_output_to_csv(10, out_train_file_name, f'{out_train_file_name}')

    @staticmethod
    def get_score(df, type):
        try:
            mae = mean_absolute_error(df['Eref'], df['Ennp'])
            mse = mean_squared_error(df['Eref'], df['Ennp'])
            rmse = np.sqrt(mse)
            r2 = r2_score(df['Eref'], df['Ennp'])
        except TypeError as e:
            print('NANが含まれています')
            return
        return [type, mae, mse, rmse, r2]

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
    # dir_path = '/Users/y1u0d2/Desktop/Lab/result/nnp-train/20211123'
    def conduct_flow(dir_path, is_send_local=False, scp_dir_path=None):
        analyze_flow = N2p2AnalyzeFlow(dir_path)
        analyze_flow.make_analyze_dir()
        analyze_flow.convert_test_train_csv()
        base_df = get_reindex_base(is_gpu=False)
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
            try:
                test_score = analyze_flow.get_score(df_test_new, type='test')
                train_score = analyze_flow.get_score(df_train_new, type='train')
                analyze_flow.write_score_csv(epoch, test_score, train_score)
            except Exception as e:
                continue
        if is_send_local and scp_dir_path is not None:
            dir_name = directory.split('/')[-1]
            if not os.path.exists(f'{scp_dir_path}/{dir_name}'):
                os.mkdir(f'{scp_dir_path}/{dir_name}')
            shutil.move(f'{dir_path}/analyze', f'{scp_dir_path}/{dir_name}/')

    dirs = glob.glob('/Users/y1u0d2/Desktop/Lab/result/nnp-train/rdf-inform/20211117/angular/01')
    for directory in dirs:
        conduct_flow(directory)
