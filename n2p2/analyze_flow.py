import glob
import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

    def convert_test_train_csv(self, type=1):
        """
        convert n2p2 output to csv
        :param type: {1:energy, 2:force}
        :return:
        """
        if type == 1:
            header_num = 10
            test_files = glob.glob(f'{self.dir_path}/testpoints.0000*')
            train_files = glob.glob(f'{self.dir_path}/trainpoints.0000*')
        elif type == 2:
            header_num = 11
            test_files = glob.glob(f'{self.dir_path}/testforces.0000*')
            train_files = glob.glob(f'{self.dir_path}/trainforces.0000*')
        if test_files and train_files:
            obj = ConvertCsv(output_dir=f'{self.dir_path}/analyze', target_dir=self.dir_path)
            for test_file_path, train_file_path in zip(test_files, train_files):
                out_test_file_name = test_file_path.split('/')[-1]
                out_train_file_name = train_file_path.split('/')[-1]
                # csvファイルに変換
                obj.convert_n2p2_output_to_csv(header_num, out_test_file_name, f'{out_test_file_name}')
                obj.convert_n2p2_output_to_csv(header_num, out_train_file_name, f'{out_train_file_name}')

    @staticmethod
    def get_score(df, process, type='E'):
        try:
            mae = mean_absolute_error(df[f'{type}ref'], df[f'{type}nnp'])
            mse = mean_squared_error(df[f'{type}ref'], df[f'{type}nnp'])
            rmse = np.sqrt(mse)
            r2 = r2_score(df[f'{type}ref'], df[f'{type}nnp'])
        except TypeError as e:
            print('NANが含まれています')
            return
        return [process, mae, mse, rmse, r2]

    def write_score_csv(self, epoch, test_score, train_score, type='E'):
        test_score.insert(0, epoch)
        train_score.insert(0, epoch)
        with open(f'{self.dir_path}/analyze/score_{type}.csv', 'a') as f:
            writer = csv.writer(f)
            if epoch == 0:
                writer.writerow(['epoch', 'type', 'MAE', 'MSE', 'RMSE', 'R2'])
            writer.writerow(test_score)
            writer.writerow(train_score)

    @staticmethod
    def get_base_merged_df(df_test, df_train, base_df, type="E"):
        if type == "E":
            df_test_new = pd.merge(df_test, base_df, left_on='index', right_on='structure_idx')
            df_train_new = pd.merge(df_train, base_df, left_on='index', right_on='structure_idx')
        elif type == "F":
            df_test_new = pd.merge(df_test, base_df, left_on='index_s', right_on='structure_idx')
            df_train_new = pd.merge(df_train, base_df, left_on='index_s', right_on='structure_idx')
        return df_test_new, df_train_new


    @staticmethod
    def plot_epoch_error(directory, save_dir, error, type='E', ymin=0, ymax=1):
        error_list = ['R2', 'RMSE', 'MAE', 'MSE']
        if error not in error_list:
            print('invalid error name')
            return
        # r_cut = directory.split('/')[-1].split('_')[1]
        # num_pairs = directory.split('/')[-1].split('_')[-1]
        r_cut = 5
        num_pairs = 3
        if os.path.exists(f'{directory}/analyze/score_{type}.csv'):
            df = pd.read_csv(f'{directory}/analyze/score_{type}.csv')
            df['r_cut'] = r_cut
            df['num_pairs'] = num_pairs
            df_test = df[df.type == 'test']
            df_train = df[df.type == 'train']

            fig = plt.figure(figsize=(6, 4))
            plt.title(f'r_cut: {r_cut}, num_pairs: {num_pairs}')
            plt.ylim(ymin, ymax)
            plt.xlabel('epoch')
            plt.ylabel(f'{error}({type})')
            plt.plot(df_test.epoch, df_test[error], label="test")
            plt.plot(df_train.epoch, df_train[error], label="train")
            plt.legend()
            fig.savefig(f'{save_dir}/{type}_r_cut-{r_cut}_pairs-{num_pairs}.png')
    
    @staticmethod
    def plot_dft_pred(csv_path, save_path, setting_path, epoch, type='E', prefix=0, is_title=True):
        """
        plot dft vs pred from n2p2 output csv
        :param save_path: path to save folder
        :param csv_path: path to analyze dir
        :param setting_path: path to input.nn(normed)
        :param epoch:
        :param type: E(Energy) or F(Force)
        :return:
        """
        epoch = str(epoch).zfill(2)
        base_df = get_reindex_base()
        if type == "E":
            df_test = pd.read_csv(f'{csv_path}/testpoints.0000{epoch}.out.csv')
            df_train = pd.read_csv(f'{csv_path}/trainpoints.0000{epoch}.out.csv')
        elif type == "F":
            df_test = pd.read_csv(f'{csv_path}/testforces.0000{epoch}.out.csv')
            df_train = pd.read_csv(f'{csv_path}/trainforces.0000{epoch}.out.csv')
        # add columns about type
        df_test['type'] = 'test'
        df_train['type'] = 'train'
        df_test_new, df_train_new = N2p2AnalyzeFlow.get_base_merged_df(df_test=df_test, df_train=df_train, base_df=base_df, type=type)
        df_concat = pd.concat([df_test_new, df_train_new])
        # NAN処理
        df_bool = df_concat == '-NAN'
        if df_bool.values.sum() > 0:
            print('NANが含まれています')
            return

        setting_path = f'{setting_path}/input.nn'
        with open(setting_path) as f:
            l_strip = [line.strip() for line in f.readlines()]
            l_strip = list(filter(None, l_strip))
            mean_arr = [line for line in l_strip if 'mean_energy' in line]
            # sigma e
            norm_arr = [line for line in l_strip if 'conv_energy' in line]
            # sigma f
            norm_force_arr = [line for line in l_strip if 'conv_length' in line]

        mean = ""
        conv_e = ""
        conv_l = ""
        for mean, norm, norm_force in zip(mean_arr, norm_arr, norm_force_arr):
            mean = float(mean.split(' ')[-1])
            conv_e = float(norm.split(' ')[-1])
            conv_l = float(norm_force.split(' ')[-1])
            norm = 1/conv_e

        if type == "E":
            df_concat['Ediff'] = df_concat.natom * norm * (df_concat.Eref - df_concat.Ennp)
            df_concat['E_nnp_from_norm'] = df_concat.natom * ((norm * df_concat.Ennp) + mean)
            df_concat['E_ref_from_norm'] = df_concat.natom * ((norm * df_concat.Eref) + mean)
            df_concat['E_ref_sio2'] = df_concat['E_ref_from_norm'] / (df_concat.natom)
            df_concat['E_nnp_sio2'] = df_concat['E_nnp_from_norm'] / (df_concat.natom)
            min_energy = df_concat['E_ref_sio2'].min()
            df_concat['E_ref_sio2'] -= min_energy
            df_concat['E_nnp_sio2'] -= min_energy
            xmin = 0
            xmax = df_concat['E_ref_sio2'].max()
            x = np.linspace(xmin, xmax, 100)
            y = x
            # train
            fig, ax = plt.subplots()
            plt.plot(x, y, color='red')
            ax.scatter(df_concat[df_concat.type == 'train']['E_ref_sio2'], df_concat[df_concat.type == 'train']['E_nnp_sio2'])
            if is_title:
                ax.set_title('Train : DFT_E vs Pred_E')
            ax.set_xlabel('DFT_E (eV)')
            ax.set_ylabel('Pred_E (eV)')
            fig.savefig(f'{save_path}/train_energy_{prefix}.png')
            # test
            fig, ax = plt.subplots()
            plt.plot(x, y, color='red')
            ax.scatter(df_concat[df_concat.type == 'test']['E_ref_sio2'], df_concat[df_concat.type == 'test']['E_nnp_sio2'])
            if is_title:
                ax.set_title('test : DFT_E vs Pred_E')
            ax.set_xlabel('DFT_E (eV)')
            ax.set_ylabel('Pred_E (eV)')
            fig.savefig(f'{save_path}/test_energy_{prefix}.png')
        elif type == "F":
            CONVERT_FACTOR = conv_l/conv_e
            df_concat['Fdiff'] = CONVERT_FACTOR * (df_concat.Fref - df_concat.Fnnp)
            df_concat['F_nnp_from_norm'] = CONVERT_FACTOR * df_concat.Fnnp
            df_concat['F_ref_from_norm'] = CONVERT_FACTOR * df_concat.Fref
            xmin = 0
            xmax = df_concat['F_ref_from_norm'].max()
            x = np.linspace(-xmax, xmax, 100)
            y = x
            # train
            fig, ax = plt.subplots()
            plt.plot(x, y, color='red')
            ax.scatter(df_concat[df_concat.type == 'train']['F_ref_from_norm'], df_concat[df_concat.type == 'train']['F_nnp_from_norm'])
            if is_title:
                ax.set_title('Train : DFT_F vs Pred_F')
            ax.set_xlabel('DFT_F (eV/ang)')
            ax.set_ylabel('Pred_F (eV/ang)')
            fig.savefig(f'{save_path}/train_force_{prefix}.png')
            # test
            fig, ax = plt.subplots()
            plt.plot(x, y, color='red')
            ax.scatter(df_concat[df_concat.type == 'test']['F_ref_from_norm'], df_concat[df_concat.type == 'test']['F_nnp_from_norm'])
            if is_title:
                ax.set_title('test : DFT_F vs Pred_F')
            ax.set_xlabel('DFT_F (eV/ang)')
            ax.set_ylabel('Pred_F (eV/ang)')
            fig.savefig(f'{save_path}/test_force_{prefix}.png')
        


if __name__ == '__main__':
    def conduct_flow(dir_path, is_send_local=False, scp_dir_path=None):
        analyze_flow = N2p2AnalyzeFlow(dir_path)
        analyze_flow.make_analyze_dir()
        analyze_flow.convert_test_train_csv(type=1)
        analyze_flow.convert_test_train_csv(type=2)
        base_df = get_reindex_base(is_gpu=False)

        # Energy
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
                test_score = analyze_flow.get_score(df_test_new, process='test', type='E')
                train_score = analyze_flow.get_score(df_train_new, process='train', type='E')
                analyze_flow.write_score_csv(epoch, test_score, train_score, type='E')
            except Exception as e:
                continue
        # Force
        all_test_csv = glob.glob(f'{dir_path}/analyze/testforces*')
        all_train_csv = glob.glob(f'{dir_path}/analyze/trainforces*')
        all_test_csv.sort()
        all_train_csv.sort()
        for i, (test_csv, train_csv) in enumerate(zip(all_test_csv, all_train_csv)):
            epoch = i
            df_test = pd.read_csv(test_csv)
            df_train = pd.read_csv(train_csv)
            try:
                test_score = analyze_flow.get_score(df_test, process='test', type='F')
                train_score = analyze_flow.get_score(df_train, process='train', type='F')
                analyze_flow.write_score_csv(epoch, test_score, train_score, type='F')
            except Exception as e:
                continue
        if is_send_local and scp_dir_path is not None:
            dir_name = directory.split('/')[-1]
            if not os.path.exists(f'{scp_dir_path}/{dir_name}'):
                os.mkdir(f'{scp_dir_path}/{dir_name}')
            shutil.move(f'{dir_path}/analyze', f'{scp_dir_path}/{dir_name}/')

    dirs = glob.glob('/Users/y1u0d2/desktop/Lab/result/nnp-train/two-three-body/02/01')
    for i, directory in enumerate(dirs):
        conduct_flow(directory)
        save_dir = '/Users/y1u0d2/desktop/Lab/result/nnp-train/two-three-body/02/01/error'
        r2_dir = f'{save_dir}/r2'
        rmse_dir = f'{save_dir}/rmse'
        mae_dir = f'{save_dir}/mae'
        for i in [r2_dir, rmse_dir, mae_dir]:
            if not os.path.exists(i):
                os.mkdir(i)
            if not os.path.exists(f'{i}/energy'):
                os.mkdir(f'{i}/energy')
            if not os.path.exists(f'{i}/force'):
                os.mkdir(f'{i}/force')
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{r2_dir}/energy',error='R2', type='E', ymin=0.9, ymax=1.05)
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{r2_dir}/force',error='R2', type='F', ymin=0.9, ymax=1.05)
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{rmse_dir}/energy',error='RMSE', type='E')
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{rmse_dir}/force',error='RMSE', type='F')
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{mae_dir}/energy',error='MAE', type='E')
        N2p2AnalyzeFlow.plot_epoch_error(directory, save_dir=f'{mae_dir}/force',error='MAE', type='F')
        # plot dft vs pred
        # print(directory)
        # N2p2AnalyzeFlow.plot_dft_pred(f'{directory}/analyze',
        #                               save_path='/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126/dft_vs_pred',
        #                               setting_path='/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126/scp/original',
        #                               epoch = 10,
        #                               type='E',
        #                               prefix = i
        #                               )
        # N2p2AnalyzeFlow.plot_dft_pred(f'{directory}/analyze',
        #                               save_path='/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126/dft_vs_pred',
        #                               setting_path='/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126/scp/original',
        #                               epoch = 10,
        #                               type='F',
        #                               prefix = i
        #                               )
