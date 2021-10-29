from n2p2 import dft_pred

PATH = [
    'data_alpha-critobalite',
    'data_alpha-quartz',
    'data_beta-quartz',
    'data_beta-trydymite',
    'data_coesite',
    'data_Fdd2-beta-critobalite',
    'data_hex-trydymite',
    'data_stishovite'
]

vol_ene = dft_pred.AnalyzeCSV('/Users/y1u0d2/desktop/vol-ene-result/sample')
vol_ene.run_this_func()



