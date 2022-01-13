import pandas as pd

dft_data_path = '/Users/y1u0d2/desktop/Lab/data/stable-structure/'
nn_data_path = '/Users/y1u0d2/desktop/Lab/result/lammps/structure-optimization/07'

dft_lattice = pd.read_csv(f'{dft_data_path}/lattice_info.csv')
dft_rdf = pd.read_csv(f'{dft_data_path}/rdf.csv')
nn_lattice = pd.read_csv(f'{nn_data_path}/lattice.csv')
nn_rdf = pd.read_csv(f'{nn_data_path}/rdf.csv')
nn_lattice.rename(columns={'Cella':'a', 'Cellb':'b', 'Cellc':'c', 'CellAlpha':'alpha', 'CellBeta':'beta', 'CellGamma':'gamma'}, inplace=True)

def get_diff_df(index, dft_lattice, nn_lattice):
    nn_lattice_row = nn_lattice.iloc[index,:]
    structure = nn_lattice_row.structure
    idx = nn_lattice_row.idx
    dft_lattice_row_index = dft_lattice.reset_index().query(f'structure == "{nn_lattice_row.structure}"').index[0]
    dft_lattice_row = dft_lattice.iloc[dft_lattice_row_index,:]
    lattice_diff_sum = ((nn_lattice_row[2:5] - dft_lattice_row[1:4])**2).sum()
    diff_series = pd.Series([structure,idx,lattice_diff_sum],index=['structure', 'idx', 'lattice_diff'])
    return pd.DataFrame([diff_series])

lattice_diff_df = get_diff_df(0, dft_lattice, nn_lattice)
for i in range(len(nn_lattice)-1):
    tmp_diff_df = get_diff_df(i+1, dft_lattice, nn_lattice)
    lattice_diff_df = pd.concat([lattice_diff_df, tmp_diff_df])

def get_rdf_diff_df(index, dft_rdf, nn_rdf):
    nn_rdf_row = nn_rdf.iloc[index,:]
    structure = nn_rdf_row.structure
    idx = nn_rdf_row.idx
    bond = nn_rdf_row.bond
    dft_rdf_row_index = dft_rdf.reset_index().query(f'structure == "{nn_rdf_row.structure}" and bond == "{bond}"').index[0]
    dft_rdf_row = dft_rdf.iloc[dft_rdf_row_index,:]
    wip = (nn_rdf_row[3:] - dft_rdf_row[2:])**2
    diff_rdf = ((nn_rdf_row[3:] - dft_rdf_row[2:])**2).sum()
    diff_series = pd.Series([structure,idx,bond,diff_rdf],index=['structure', 'idx', 'bond', 'rdf_diff'])
    return pd.DataFrame([diff_series])

rdf_diff_df = get_rdf_diff_df(0, dft_rdf, nn_rdf)
for i in range(len(nn_rdf)-1):
    tmp_diff_df = get_rdf_diff_df(i+1, dft_rdf, nn_rdf)
    rdf_diff_df = pd.concat([rdf_diff_df, tmp_diff_df])
print(rdf_diff_df)
# rdf_diff_df = rdf_diff_df.groupby(['structure', 'idx']).mean().reset_index()