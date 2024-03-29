import sys
import os
from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
from pymatgen.io.xcrysden import XSF
from pymatgen.core.periodic_table import Element
import numpy as np
import matplotlib.pyplot as plt
import glob
import csv

class AtomicDensity:
    def __init__(self, output_dir, xsf_file_path=None):
        self.output_dir = output_dir
        self.xsf_file_path = xsf_file_path

    def fileconvert2cif(self,file1, file2):
        """
        file format conversion
        ref.s
        http://pymatgen.org/usage.html

        @param file1 : input filename, any formats pymatgen accepts
        @param file2 : cif output filename
        """
        tmpfilename = "__temp__.cif"

        def write2cif(f1, f2):
            structure = Structure.from_file(f1)
            w = CifWriter(structure)
            w.write_file(f2)

            return structure

        def write2xsf(f1, f2):
            structure = Structure.from_file(f1)

            xsf = XSF(structure)
            s = xsf.to_string()
            with open(f2, "wb") as f:
                f.write(s)

            return structure
        _ = write2cif(file1, tmpfilename)
        """
        run twice to make atoms inside the cell automatically.
        """
        structure = write2cif(tmpfilename, file2)

        os.remove(tmpfilename)
        return structure

    def get_num_of_center_atom(self, structure, center_atom):
        n_center_atom = 0
        for atom in structure.species:
            if atom == center_atom:
                n_center_atom += 1
        return n_center_atom

    def calc_density(self, structure, center_elm, another_elm, r_max):
        center_elm = Element(center_elm)
        another_elm = Element(another_elm)
        n_center_atom = self.get_num_of_center_atom(structure, center_elm)
        density_list = []
        for s in structure:
            if (s.specie.value == center_elm.value):
                nn = structure.get_neighbors(s, r_max)
                # print("center", s.coords, s.specie)
                natom = 0
                for n in nn:
                    if (n[0].specie.value == another_elm.value):
                        natom += 1
                        # print("cart", n[0].coords, n[0].specie, "distance", n[1])
                vol_sphere = 4 / 3 * np.pi * r_max ** 3
                density = natom / vol_sphere
                density_list.append(density)
        density_list = np.array(density_list)
        # density_average = np.average(density_list) / n_center_atom
        return np.average(density_list), n_center_atom

    def run_this_func(self):
        PATH = [
            'alpha-critobalite',
            'alpha-quartz',
            'beta-quartz',
            'beta-trydymite',
            'coesite',
            'Fdd2-beta-critobalite',
            'hex-trydymite',
            'stishovite'
        ]
        dirs = glob.glob(f'{self.xsf_file_path}/data*')

        for directory in dirs:
            name_of_structure = directory.split('/')[-1].split('_')[-1]

            if name_of_structure not in PATH:
                continue

            if not os.path.exists(f'{self.output_dir}/{name_of_structure}'):
                os.mkdir(f'{self.output_dir}/{name_of_structure}')

            files = glob.glob(f'{directory}/*')
            for i, file in enumerate(files):
                self.fileconvert2cif(file, 'tmp.cif')
                structure = Structure.from_file('./tmp.cif')
                structure_idx = file.split('/')[-1].split('_')[-1].split('.')[0]

                with open(f'{self.output_dir}/{name_of_structure}/density_Si-Si.csv', 'a') as f:
                    writer = csv.writer(f)
                    if i == 0:
                        writer.writerow(
                            ['structure_idx', 'name_of_structure', 'num center atom', 'density', 'center atom',
                             'another atom'])
                    density, n_center_atom = self.calc_density(structure, 'Si', 'Si', 15)
                    print(density,n_center_atom)
                    writer.writerow([structure_idx,name_of_structure,n_center_atom,density,'Si','Si'])

                with open(f'{self.output_dir}/{name_of_structure}/density_O-Si.csv', 'a') as f:
                    writer = csv.writer(f)
                    if i == 0:
                        writer.writerow(
                            ['structure_idx', 'name_of_structure', 'num center atom', 'density', 'center atom',
                             'another atom'])
                    density, n_center_atom = self.calc_density(structure, 'O', 'Si', 15)
                    print(density,n_center_atom)
                    writer.writerow([structure_idx,name_of_structure,n_center_atom,density,'O','Si'])

                with open(f'{self.output_dir}/{name_of_structure}/density_Si-O.csv', 'a') as f:
                    writer = csv.writer(f)
                    if i == 0:
                        writer.writerow(
                            ['structure_idx', 'name_of_structure', 'num center atom', 'density', 'center atom',
                             'another atom'])
                    density, n_center_atom = self.calc_density(structure, 'Si', 'O', 15)
                    print(density,n_center_atom)
                    writer.writerow([structure_idx,name_of_structure,n_center_atom,density,'Si','O'])

                with open(f'{self.output_dir}/{name_of_structure}/density_O-O.csv', 'a') as f:
                    writer = csv.writer(f)
                    if i == 0:
                        writer.writerow(
                            ['structure_idx', 'name_of_structure', 'num center atom', 'density', 'center atom',
                             'another atom'])
                    density, n_center_atom = self.calc_density(structure, 'O', 'O', 15)
                    print(density,n_center_atom)
                    writer.writerow([structure_idx,name_of_structure,n_center_atom,density,'O','O'])

if __name__ == '__main__':
    atomic_density = AtomicDensity('/Users/y1u0d2/desktop/Lab/Program/python/RDF/20211031/density','/Users/y1u0d2/desktop/Lab/Program/python/RDF/xsf')
    atomic_density.run_this_func()

