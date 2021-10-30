class FormatDataSet():
    def __init__(self, output_dir, output_file, input_dir):
        self.output_dir = output_dir
        self.output_file = output_file
        self.input_dir = input_dir

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
        structure_idx = 1
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
                # position_frac_index = 8 + (number_of_atom)
                energy_index = 8 + number_of_atom * 2
                force_index = 10 + number_of_atom * 2

                # n2p2のフォーマットに変更
                for block in block_list:
                    # begin出力
                    export_file.write('begin\n')

                    #comment
                    export_file.write(f'comment structure:{structure} structure_idx:{structure_idx}\n')
                    structure_idx += structure_idx

                    # lattice
                    lattice_block = block[lattice_index:lattice_index + 3]
                    print(lattice_block)

                    for lattice in lattice_block:
                        export_file.write(f'lattice {lattice}\n')

                    # atom
                    position_block = block[position_abs_index:position_abs_index + number_of_atom]
                    force_block = block[force_index:force_index + number_of_atom]
                    atom_block = []
                    dummy_data = [0.0, 0.0]
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

                    # energy
                    energy = float(block[energy_index].split()[1])
                    export_file.write(f'energy {energy}\n')

                    # charge
                    charge = 0.0
                    export_file.write(f'charge {charge}\n')

                    # end出力
                    export_file.write('end\n')

        export_file.close()