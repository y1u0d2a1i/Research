
import sys
import os
from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
from pymatgen.io.xcrysden import XSF
import numpy as np
import matplotlib.pyplot as plt
import glob
import csv

path_to_csv = '/home/y1u0d2/Program/python/sf/rdf_result'
def fileconvert2cif(file1, file2):
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

def plot_rdf(dir,center_atom,another_atom,rcut):
    """
    plot radial distribution function (rdf) with the distance list given by pymatgen library

    @param structure : pymatgen structure
    @param center_atom : center atom
    @param another_atom : another atom
    @param  rcut : cutoff distance
    """

    def plot_hist(distancelist, bins=50):
        """
        histgram plot

        @param distancelist : a list of distances
        @param bins : a list of bins
        """
        fig = plt.figure()
        # plt.title(f'{name_of_structure}_{center_atom}-{another_atom}_hist')
        plt.xlabel("r(Å)")
        plt.ylabel("occurence")
        """
        histgram library of matplotlib
        """
        plt.hist(distancelist, bins=bins)
        plt.show()
        # fig.savefig(f'./rdf_result/pic/{name_of_structure}_{center_atom}-{another_atom}_hist.png')

    # plot_hist(distancelist)

    def plot_rdf_div_r2(distancelist, rcut, xmin=1.0, bins=70):
        """
        multiply histgram by 1/r**2
        and plot it

        @param distancelist : a list of distance
        @param xrange : 1d array [2], min and max
        @param bins : number of bins of histgram
        """
        dr = (rcut-xmin)/bins
        bins = np.linspace(xmin, rcut, bins)
        # print(bins)
        index = np.digitize(distancelist, bins)
        """
        add to hist array
        """
        hist = np.zeros((len(bins)))
        for i, d in zip(index, distancelist):
            if i > 0 and i < len(bins):
                if bins[i-1] < d and d < bins[i]:
                    hist[i] += 1.0/(4 * np.pi * d**2 * dr)
                    continue
            print("warning i", i, d)
        """
        visualization
        """
        fig = plt.figure()
        # plt.title(f'{name_of_structure}_{center_atom}-{another_atom}_rdf')
        plt.xlabel("r")
        plt.ylabel("occurence/r**2")
        """
        use the middle point for x points
        """
        bins_mid = (bins[0:-1]+bins[1:])*0.5

        # plt.plot(bins_mid, hist[1:])
        # plt.show()

        return bins_mid,hist[1:]
        # fig.savefig(f'./rdf_result/pic/{name_of_structure}_{center_atom}-{another_atom}_rdf.png')

    # plot_rdf_div_r2(distancelist, rcut)

    files = glob.glob(f'{dir}/*')
    name_of_structure = dir.split('/')[-1].split('_')[-1]

    if os.path.exists(f'{path_to_csv}/{name_of_structure}/{name_of_structure}_{center_atom}-{another_atom}.csv'):
        return

    for i, file in enumerate(files):
        print(file)
        structure_idx = file.split('/')[-1].split('_')[-1].split('.')[0]
        distancelist = []
        fileconvert2cif(file,'tmp.cif')
        structure = Structure.from_file('./tmp.cif')
        for j,s in enumerate(structure):
            if (not s.specie.value == center_atom):
                continue
            nn = structure.get_neighbors(s, rcut)
            for n in nn:
                if (not n[0].specie.value == another_atom):
                    continue
                distancelist.append(n[1])

            bins_mid, hist = plot_rdf_div_r2(distancelist, rcut)
            bins_mid = bins_mid.tolist()
            hist = hist.tolist()
            hist_insert = [name_of_structure, structure_idx, center_atom, another_atom]
            for tmp in hist_insert:
                # np.insert(hist,0,tmp)
                hist.insert(0, tmp)
            with open(f'{path_to_csv}/{name_of_structure}/{name_of_structure}_{center_atom}-{another_atom}.csv',
                      'a') as f:
                writer = csv.writer(f)
                if i == 0 and j == 0:
                    bins_mid_insert = ['name_of_structure', 'structure_idx', 'center_atom', 'another_atom']
                    for tmp in bins_mid_insert:
                        # np.insert(bins_mid,0,tmp)
                        bins_mid.insert(0, tmp)
                    writer.writerow(bins_mid)
                writer.writerow(hist)

dirs = glob.glob('/home/y1u0d2/Program/python/RDF/xsf/*')
for directory in dirs:
    name_of_structure = directory.split('/')[-1].split('_')[-1]
    print(name_of_structure)
    if not os.path.exists(f'{path_to_csv}/{name_of_structure}'):
        os.mkdir(f'{path_to_csv}/{name_of_structure}')
    plot_rdf(directory, 'Si', 'Si', rcut=15.0)
    plot_rdf(directory, 'O', 'O', rcut=15.0)
    plot_rdf(directory, 'Si', 'O', rcut=15.0)
    plot_rdf(directory, 'O', 'Si', rcut=15.0)
