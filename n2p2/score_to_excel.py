# scoreをexcelのシートにまとめる
# TODO functional implementation
import glob
import os.path

import pandas as pd

import openpyxl

SAVE_DIR = '/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126'
TARGET_DIR = '/Users/y1u0d2/desktop/Lab/result/nnp-train/20211126/scp'

dirs = glob.glob(f'{TARGET_DIR}/nnp*')
dirs.sort()

# wb = openpyxl.Workbook()
writer = pd.ExcelWriter(f'{SAVE_DIR}/score.xlsx')
for directory in dirs:
    r_cut = directory.split('/')[-1].split('_')[1]
    num_pairs = directory.split('/')[-1].split('_')[2]
    if os.path.exists(f'{directory}/analyze/score_E.csv') and os.path.exists(f'{directory}/analyze/score_F.csv'):
        df_E = pd.read_csv(f'{directory}/analyze/score_E.csv')
        df_F = pd.read_csv(f'{directory}/analyze/score_F.csv')
        df_E.to_excel(writer, sheet_name=f'Energy, r_cut={r_cut}, num_pairs={num_pairs}', index=False)
        df_F.to_excel(writer, sheet_name=f'Force, r_cut={r_cut}, num_pairs={num_pairs}', index=False)
writer.save()
writer.close()