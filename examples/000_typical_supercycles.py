from supercycles.database import SPSCYCLES
from supercycles.supercycle import Supercycle

empty_supercycle = Supercycle('SPS', 'Test', [])

physics_supercycle = Supercycle('SPS', 'Physics',
                                [SPSCYCLES['SFTPRO'], SPSCYCLES['deGauss'], SPSCYCLES['SFTPRO'], SPSCYCLES['deGauss']])

lhcfilling_supercycle = Supercycle('SPS', 'LHC filling',
                                   [SPSCYCLES['SFTPRO'], SPSCYCLES['LHC filling'], SPSCYCLES['deGauss']])
