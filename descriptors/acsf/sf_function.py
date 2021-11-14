import math
import numpy as np
import matplotlib.pyplot as plt

class SymmetryFunction:
    def cutoff_func1(self, r_ij, r_c):
        if r_ij <= r_c:
            return 0.5 * (math.cos(((np.pi * r_ij) / r_c)) + 1)
        elif r_ij > r_c:
            return 0

    def radial_symmetry_function_2(self, eta, r_ij, r_shift, r_cutoff, cut_func_type=1):
        cutoff_func = ''
        if cut_func_type == 1:
           cutoff_func = self.cutoff_func1(r_ij, r_cutoff)
        return math.exp(-1 * eta * (r_ij - r_shift) ** 2) * cutoff_func