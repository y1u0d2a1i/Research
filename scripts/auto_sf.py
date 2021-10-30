from n2p2.auto_sf.sfparamgen import SymFuncParamGenerator

def auto_generate(r_cutoff, nb_param_pairs, target_file,):
    myGenerator = SymFuncParamGenerator(elements=['O', 'Si'], r_cutoff = r_cutoff)
    myGenerator.symfunc_type = 'radial'
    myGenerator.generate_radial_params(rule='imbalzano2018', mode='shift', nb_param_pairs=nb_param_pairs)
    with open(target_file, 'a') as f:
        myGenerator.write_settings_overview(fileobj=f)
        myGenerator.write_parameter_strings(fileobj=f)

auto_generate(8, 5, '/Users/y1u0d2/desktop/Lab/Program/python/n2p2/two-body/input.nn')