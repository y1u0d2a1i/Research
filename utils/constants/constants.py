class Constants:
    @staticmethod
    def path():
        # file name of qmas_data
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
        return PATH


    @staticmethod
    def structures():
        structures = [
            'alpha-critobalite',
            'alpha-quartz',
            'beta-quartz',
            'beta-trydymite',
            'coesite',
            'Fdd2-beta-critobalite',
            'hex-trydymite',
            'stishovite'
        ]
        return structures

    @staticmethod
    def structures_natom():
        structures = {
            'alpha-critobalite':48,
            'alpha-quartz':36,
            'beta-quartz':36,
            'beta-trydymite':48,
            'coesite':24,
            'Fdd2-beta-critobalite':48,
            'hex-trydymite':48,
            'stishovite':48
        }
        return structures