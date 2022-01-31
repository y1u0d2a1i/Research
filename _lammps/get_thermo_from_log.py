import csv
import glob
import pandas as pd


def get_thermo_csv_from_log(target_dir, output_dir):
    natom = 0
    with open(f'{target_dir}/log.lammps') as f:
        l_strip = [s.strip() for s in f.readlines()]
        start, end = 0, 0
        for i, line in enumerate(l_strip):
            specify_word_start = '### NNP EW SUMMARY ### TS:          0 EW'
            specify_word_end = "Loop time of "
            if specify_word_start in line:
                print(i)
                start = i
            if specify_word_end in line:
                print(i)
                end = i
            if 'steps with' in line:
                natom = line.split(' ')[-2]
        thermo_output = l_strip[start+2:end]
        with open(f'{output_dir}/thermo_{natom}.csv', 'w') as f:
            writer = csv.writer(f)
            for line in thermo_output:
                if 'NNP EW SUMMARY' in line:
                    continue
                line = list(filter(None, line.split(' ')))
                writer.writerow(line)
    return natom

def get_lattice_series_from_thermo_csv(_dir):
    # id = _dir.split('/')[-1].split('_')[1]
    id = _dir.split('/')[-1]
    structure = id.split('_')[1]
    idx = id.split('_')[-1].split('.')[0]
    csv_f = glob.glob(f'{_dir}/thermo*.csv')[0]
    df = pd.read_csv(csv_f)
    loc_cella = df.columns.get_loc('Cella')
    # 最終行のlattice部分取得
    l_series = df.iloc[len(df)-1:len(df),loc_cella:loc_cella+6].copy()
    l_series.insert(0, 'idx', idx)
    l_series.insert(0, 'structure', structure)
    return l_series

def get_last_structure_info_series_from_thermo_csv(_dir):
    # id = _dir.split('/')[-1].split('_')[1]
    id = _dir.split('/')[-1]
    structure = id.split('_')[1]
    idx = id.split('_')[-1].split('.')[0]
    csv_f = glob.glob(f'{_dir}/thermo*.csv')[0]
    df = pd.read_csv(csv_f)
    natom = csv_f.split('/')[-1].split('.')[0].split('_')[-1]
    loc_eng = df.columns.get_loc('TotEng')
    # 最終行のlattice部分取得
    l_series = df.iloc[len(df)-1:len(df),loc_eng:loc_eng+4].copy()
    l_series.insert(0, 'natom', natom)
    l_series.insert(0, 'idx', idx)
    l_series.insert(0, 'structure', structure)
    l_series['Eng_a'] = round(float(l_series['TotEng']) / float(l_series['natom']), 4)
    return l_series
