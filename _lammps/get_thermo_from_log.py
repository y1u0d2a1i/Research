import csv


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
