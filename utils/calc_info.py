import numpy as np
def calc_vol(lattice_block):
    """
    calculate volume from lattice vector
    :param lattice_block: 3*3 matrix of lattice vector
    :return: volume
    """
    a = lattice_block[0].split(' ')
    b = lattice_block[1].split(' ')
    c = lattice_block[2].split(' ')
    a = list(map(lambda x: float(x), a))
    b = list(map(lambda x: float(x), b))
    c = list(map(lambda x: float(x), c))
    vol = str(abs(np.dot(np.cross(a, b), c)))
    return vol