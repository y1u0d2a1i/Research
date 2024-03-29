class FormatDataSet():
    def __init__(self, output_dir, output_file, input_dir, is_comment=True):
        self.output_dir = output_dir
        self.output_file = output_file
        self.input_dir = input_dir
        self.is_comment = is_comment
        # Bohr -> ang
        self.CONVERT_ANG = 0.529177;
        # Hartree -> eV
        self.CONVERT_EV = 27.2114;
        # Hartree/Bohr -> eV/ang
        self.CONVERT_FORCE = self.CONVERT_EV / self.CONVERT_ANG;

    def qmas_to_n2p2(self):
        # データのファイル名
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

        # 出力ファイル
        export_file = open(f'{self.output_dir}/{self.output_file}', 'a')
        structure_idx = 0
        for raw_data_file in PATH:
            structure = raw_data_file.split('_')[-1]
            with open(f'{self.input_dir}/{raw_data_file}') as file:
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
                position_frac_index = 8 + (number_of_atom)
                energy_index = 8 + number_of_atom * 2
                force_index = 10 + number_of_atom * 2

                # n2p2のフォーマットに変更
                for block in block_list:
                    # begin出力
                    export_file.write('begin\n')

                    # comment
                    export_file.write(f'comment structure:{structure} structure_idx:{structure_idx}.\n')
                    structure_idx += 1

                    # lattice
                    lattice_block = block[lattice_index:lattice_index + 3]

                    for lattice in lattice_block:
                        # convert
                        # lattice = ' '.join([str(float(i) * self.CONVERT_ANG) for i in lattice.split(' ')])
                        export_file.write(f'lattice {lattice}\n')

                    # atom
                    # position_block = block[position_abs_index:position_abs_index + number_of_atom]
                    position_block = block[position_frac_index:position_frac_index + number_of_atom]
                    force_block = block[force_index:force_index + number_of_atom]
                    atom_block = []
                    dummy_data = [0.0, 0.0]
                    for position, force in zip(position_block, force_block):
                        position = position.split()[2:]
                        force = force.split()[1:]
                        # convert
                        # position = [str(float(i) * self.CONVERT_ANG) for i in position]
                        atom = force[0]
                        force = [str(float(i) * self.CONVERT_FORCE) for i in force[1:]]
                        force.insert(0, atom)

                        force.insert(1, '0.0')
                        force.insert(1, '0.0')
                        row = position + force
                        atom_block.append(row)

                    for atom in atom_block:
                        atom_str = ' '.join(atom)
                        export_file.write(f'atom {atom_str}\n')

                    # energy
                    energy = float(block[energy_index].split()[1]) * self.CONVERT_EV
                    export_file.write(f'energy {energy}\n')

                    # charge
                    charge = 0.0
                    export_file.write(f'charge {charge}\n')

                    # end出力
                    export_file.write('end\n')

        export_file.close()

if __name__ == '__main__':
    obj = FormatDataSet('/Users/y1u0d2/desktop/Lab/data/qmas_frac', 'frac.data',
                        '/Users/y1u0d2/desktop/Lab/data/qmas_data')
    obj.qmas_to_n2p2()