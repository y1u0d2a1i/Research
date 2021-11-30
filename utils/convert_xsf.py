# データのファイル名
import os

class ConvertXSF():
    def __init__(self,export_file_dir_path,qmas_data_path,PATH=None,):
        self.PATH = PATH
        self.export_file_dir_path = export_file_dir_path
        self.qmas_data_path = qmas_data_path

    def convert_xsf(self,raw_data_file,export_file_dir_path,qmas_data_path):
        os.mkdir(f'{self.export_file_dir_path}/{raw_data_file}')
        with open(f'{self.qmas_data_path}/{raw_data_file}') as file:
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
            for i, block in enumerate(block_list):
                export_file = open(f'{self.export_file_dir_path}/{raw_data_file}/{raw_data_file}_{i}.xsf', 'w')
                # begin出力
                export_file.write('CRYSTAL\n')

                # lattice
                lattice_block = block[lattice_index:lattice_index + 3]

                export_file.write('PRIMVEC\n')
                for lattice in lattice_block:
                    export_file.write(f'{lattice}\n')

                # atom
                position_block = block[position_abs_index:position_abs_index + number_of_atom]
                force_block = block[force_index:force_index + number_of_atom]
                atom_block = []
                for position, force in zip(position_block, force_block):
                    position = position.split()[1:]
                    print(position)
                    if (position[0] == 'O'):
                        position[0] = '8'
                    elif (position[0] == 'Si'):
                        position[0] = '14'
                    atom_block.append(position)

                export_file.write('PRIMCOORD\n')
                export_file.write(f' {number_of_atom} 1\n')
                for atom in atom_block:
                    atom_str = ' '.join(atom)
                    export_file.write(f'{atom_str}\n')

                export_file.close()

    def run_this_func(self):
        for raw_data_file in self.PATH:
            self.convert_xsf(raw_data_file,self.export_file_dir_path,self.qmas_data_path,self.PATH)




PATH = [
    'data_alpha-critobalite',
    'data_alpha-quartz',
    'data_beta-quartz',
    'data_beta-trydymite',
    'data_coesite',
    'data_Fdd2-beta-critobalite',
    'data_hex-trydymite',
    'data_stishovite'
]
# obj = ConvertXSF()

