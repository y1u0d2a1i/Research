import os
import shutil
import subprocess
import numpy as np
import csv

class VolEneFromQmasAndn2p2:
    """
    n2p2でのnnp-predictの出力とDFT(Qmas)のデータからcsvを作成する

    dir
        -n2p2_predict
        -csv
        -original_data
    """
    def __init__(self, PATH=None, application_root_dir=None, qmas_data_dir=None):
        self.PATH = PATH
        self.appplication_root_dir = application_root_dir
        self.qmas_data_dir = qmas_data_dir
        self.vol = ''

    def copy_file(self, now_dir, copy_list=None):
        """
        nnp-predictに必要なファイルコピー
        :param now_dir: now directory
        :param copy_list: list of file name
        :return:
        """
        if copy_list is None:
            copy_list = [
                'input.nn',
                'scaling.data',
                'weights.008.data',
                'weights.014.data'
            ]
        for file in copy_list:
            shutil.copy(f"{self.appplication_root_dir}/original-data/{file}", now_dir)

    def write_to_csv(self, raw_data_file, output_arr):
        """
        入力配列をcsvファイルとして書き出す
        :param raw_data_file: name of file
        :param output_arr: array to csv
        :return:
        """
        with open(f'{self.appplication_root_dir}/csv/output.{raw_data_file}.csv', 'w') as export_all_file:
            export_all_file.write('vol,E_ref,E_nnp,natom,structure\n')
            writer = csv.writer(export_all_file)
            writer.writerows(output_arr)

    def convert_qmas_to_n2p2(self, file, raw_data_file, structure, is_run_predict=True):
        """
        qmasデータをn2p2のフォーマットに変更
        :param file: file of qmas
        :param raw_data_file: name of file
        :param structure: name of structure
        :param is_run_predict: nnp-predict実行するか
        :return: csvに出力する配列 (vol,ene)
        """
        # 入力ファイル一行ずつリストで取得する
        l_strip = [line.strip() for line in file.readlines()]

        # ブロックに分割する
        number_of_atom = int(l_strip[5].split()[1])
        all_lines = len(l_strip)
        lines_in_block = number_of_atom * 3 + 10
        number_of_block = int(all_lines / lines_in_block)

        # ブロックに分けた連想配列
        block_list = []
        for i in range(number_of_block):
            block_list.append(l_strip[lines_in_block * i:lines_in_block * (i + 1)])

        # index取得
        lattice_index = 2
        position_abs_index = 7
        # position_frac_index = 8 + (number_of_atom)
        energy_index = 8 + number_of_atom * 2
        force_index = 10 + number_of_atom * 2

        # n2p2のフォーマットに変更
        vol_ene_arr = []
        for block_count,block in enumerate(block_list):
            now_dir = f'{self.appplication_root_dir}/n2p2_predict/{raw_data_file}/nnp-predict-{block_count}'

            if not os.path.exists(now_dir):
                os.mkdir(now_dir)

            # nnp-predictに必要なファイル揃える
            export_file = open(f'{now_dir}/input.data', 'w')
            self.copy_file(now_dir)

            # begin出力
            export_file.write('begin\n')

            # lattice
            lattice_block = block[lattice_index:lattice_index + 3]
            self.vol = self.calc_vol(lattice_block)

            for lattice in lattice_block:
                export_file.write(f'lattice {lattice}\n')

            # atom
            position_block = block[position_abs_index:position_abs_index + number_of_atom]
            force_block = block[force_index:force_index + number_of_atom]
            atom_block = []

            for position, force in zip(position_block, force_block):
                position = position.split()[2:]
                force = force.split()[1:]
                force.insert(1, '0.0')
                force.insert(1, '0.0')
                row = position + force
                atom_block.append(row)

            for atom in atom_block:
                atom_str = ' '.join(atom)
                export_file.write(f'atom {atom_str}\n')

            energy = float(block[energy_index].split()[1])
            export_file.write(f'energy {energy}\n')
            charge = 0.0
            export_file.write(f'charge {charge}\n')
            export_file.write('end\n')
            export_file.close()

            if is_run_predict:
                self.run_n2p2_predict(now_dir)

            output_energy = self.get_energy_from_n2p2_output(now_dir)
            vol_ene_arr.append([self.vol, str(energy), str(output_energy), str(number_of_atom), structure])
        return vol_ene_arr

    def calc_vol(self, lattice_block):
        """
        calculate volume from lattice vector
        :param lattice_block: 3*3 matrix of lattice vector
        :return: volume
        """
        a = lattice_block[0].split(' ')
        b = lattice_block[1].split(' ')
        c = lattice_block[2].split(' ')
        a = list(map(lambda x: float(x), a))
        b = list(map(lambda x: float(x), b))
        c = list(map(lambda x: float(x), c))
        vol = str(abs(np.dot(np.cross(a, b), c)))
        return vol

    def get_energy_from_n2p2_output(self,now_dir):
        """
        get energy from n2p2 output
        :param now_dir: now directory
        :return: energy from ML
        """
        # energy取得
        with open(f'{now_dir}/energy.out') as input_file:
            l_strip = [line.strip() for line in input_file.readlines()]
            output_energy = list(filter(None, l_strip[13].split(' ')))[0]
        return output_energy

    def run_n2p2_predict(self, now_dir):
        """
        run 'nnp-predict 1'
        :param now_dir: now directory
        :return:
        """
        # nnp-predict実行
        os.chdir(now_dir)
        subprocess.call(['nnp-predict', '1'])
        os.chdir(self.appplication_root_dir)

    def make_csv(self):
        """
        指定されたPATHのデータについてCSV出力する
        :return:
        """
        for raw_data_file in self.PATH:
            os.mkdir(f"./n2p2_predict/{raw_data_file}")
            structure = raw_data_file.split('_')[1]
            with open(f'./qmas_data/{raw_data_file}') as file:
                vol_ene_arr = self.convert_qmas_to_n2p2(file, raw_data_file, structure)
                output_arr = vol_ene_arr
                self.write_to_csv(raw_data_file, output_arr)
