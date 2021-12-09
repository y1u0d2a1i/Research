# get lattice, atom info from qmas_frac

from decimal import Decimal

def get_structure_block(structure, idx):
    QMAS_FRAC_PATH = '/Users/y1u0d2/desktop/Lab/data/qmas_frac/frac.data'
    with open(QMAS_FRAC_PATH) as f:
        l_strip = [s.strip() for s in f.readlines()]
        structure_block = []
        start = 0
        end = 0
        for i, line in enumerate(l_strip):
            if f'structure:{structure} structure_idx:{idx}.' in line:
                start = i
            if 'end' in line:
                end = i
                if start != 0 and start < end:
                    structure_block = l_strip[start:end]
                    break
    return structure_block


def get_lattice(structure_block):
    l_block = []
    for line in structure_block:
        if 'lattice' in line:
            line = line.split(' ')[1:]
            line.insert(0, f'a{len(l_block)+1}')
            line.append('&')
            line = ' '.join(line)
            l_block.append(line)
        if len(line) == 3:
            break
    return l_block


def get_atom_coord(structure_block):
    coord = []
    filter_atom_line = filter(lambda x: 'atom' in x, structure_block)
    for line in filter_atom_line:
        if 'e-' in line:
            line = fix_e(line)
        if '-' in line:
            line = fix_negative(line)
        line = line.split(' ')
        if len(line) > 3:
            line = line[1:4]
        line.insert(0, 'basis')
        line.append('&')
        line = ' '.join(line)
        coord.append(line)
    coord[-1] = ' '.join(coord[-1].split(' ')[0:-1])
    return coord


def fix_e(line):
    line = line.split(' ')[1:4]
    tmp_line = []
    for tmp in line:
        if 'e-' in tmp:
            tmp = "{0:.10f}".format(Decimal(tmp))
        tmp_line.append(tmp)
    line = ' '.join(tmp_line)
    return line


def fix_negative(line):
    line = line.split(' ')[1:4]
    tmp_line = []
    for tmp in line:
        if '-' in tmp:
            tmp = '0.0'
        tmp_line.append(tmp)
    line = ' '.join(tmp_line)
    return line

def get_create_atom_line(structure_block, emap):
    coord = []
    filter_atom_line = filter(lambda x: 'atom' in x, structure_block)
    for i, line in enumerate(filter_atom_line):
        atom = line.split(" ")[4]
        atom_num = emap[atom]
        coord.append(f'basis {i+1} {atom_num} &')
    return coord

structure_block = get_structure_block('alpha-quartz', 1941)
l_block = get_lattice(structure_block)
coord = get_atom_coord(structure_block)
create_atom_lines = get_create_atom_line(structure_block, emap={'Si':1, 'O':2})
save_dir = "/Users/y1u0d2/desktop/Lab/result/lammps/20211207"
with open(f'{save_dir}/lammps.txt', 'w') as f:
    for line in l_block:
        f.write(f'{line} \n')
    for line in coord:
        f.write(f'{line} \n')
    for line in create_atom_lines:
        f.write(f'{line} \n')