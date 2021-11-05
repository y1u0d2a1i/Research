from descriptors.acsf import TwoBodyACSF
import glob

obj = TwoBodyACSF(['Si','O'],10,10)
# tmp.get_two_body_parameters(['Si','O'],6,nb_param_pairs=10)

xsf_dir = glob.glob('/home/y1u0d2/Program/python/RDF/xsf/data*')
write_header = True
for directory in xsf_dir:
    xsf_files = glob.glob(f'{directory}/data*')
    for file in xsf_files:
        data = obj.calc_acsf(file)
        obj.write_csv('/home/y1u0d2/Program/python/sf', 'sf', data, write_header=write_header)
        if write_header:
            write_header = False