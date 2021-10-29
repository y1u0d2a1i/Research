import csv
import os
import shutil
class ConvertCsv():
    def __init__(self, target_dir, output_dir):
        self.target_dir = target_dir
        self.output_dir = output_dir

    def convert_n2p2_output_to_csv(self, header_index, target_file, output_file_name=None, diff=2):
        all_data = []
        with open(f'{self.target_dir}/{target_file}') as f:
            l_strip = [line.strip() for line in f.readlines()]
            header = list(filter(None, l_strip[header_index].split(' ')))[1:]
            all_data.append(header)

            for row in l_strip[header_index + diff:]:
                row = list(filter(None, row.split(' ')))
                all_data.append(row)

        # csvファイルへの書き込み
        if output_file_name is None:
            output_file_name = target_file

        with open(f'{self.output_dir}/{output_file_name}.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(all_data)