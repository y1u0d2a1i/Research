"""
learning-curveからRMSEpa_Rtest_puが最小のepoch取得して

testpoints.000~~.out
trainpoints.000~~.out
input.nn
取得して新しいディレクトリ作る

"""
import glob
import os
import pandas as pd
import shutil

from utils.convert_csv import ConvertCsv

class ExtractData:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def get_epoch(self,target_dir):
        obj = ConvertCsv(self.root_dir, target_dir)
        obj.convert_n2p2_output_to_csv(32,'learning-curve.out','tmp')
        df = pd.read_csv(f'{self.root_dir}/tmp.csv')
        min = df['RMSEpa_Etest_pu'].min()
        if 'NAN' in str(min):
            return
        epoch = df[df['RMSEpa_Etest_pu'] == min].epoch
        epoch = epoch.values[0]
        # os.remove(f'{self.root_dir}/tmp.csv')
        return epoch

    def copy_file(self, output_dir):
        epoch = self.get_epoch(self.root_dir)
        if epoch:
            epoch = str(epoch).zfill(2)
            shutil.copy(f'{self.root_dir}/testpoints.0000{epoch}.out', f'{output_dir}/')
            shutil.copy(f'{self.root_dir}/trainpoints.0000{epoch}.out', f'{output_dir}/')



