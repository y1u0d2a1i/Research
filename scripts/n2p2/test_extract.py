import glob
import os

from n2p2.extract_data import ExtractData

pro_root_dir = '/home/y1u0d2/Program/n2p2/two-body'
dirs = glob.glob(f'{pro_root_dir}/nnp*')
os.mkdir(f'{pro_root_dir}/scp_data')
for directory in dirs:
    dir_name = directory.split('/')[-1]
    output_dir = f'{pro_root_dir}/scp_data/{dir_name}'
    os.mkdir(output_dir)
    obj = ExtractData(directory)
    obj.copy_file(output_dir)