from supercycles.cycle import Cycle


PSBCYCLES = {
    'ISOLDE':   Cycle(accelerator='PSB', name='ISOLDE', bps=1, color='#00FFFF',
                      total_intensity_per_cycle = 3.2e13, transmission_to_destination=1),
    'AD':       Cycle(accelerator='PSB', name='AD',     bps=1, color='#800080'),
    'TOF':      Cycle(accelerator='PSB', name='TOF',    bps=1, color='#FFA500'),
    'EAST':     Cycle(accelerator='PSB', name='EAST',   bps=1, color='#EE82EE'),
    'MTE':      Cycle(accelerator='PSB', name='MTE',    bps=1, color='#8B0000'),
    'LHC':      Cycle(accelerator='PSB', name='LHC',    bps=1, color='#FFD700'),
    'AWAKE':    Cycle(accelerator='PSB', name='AWAKE',  bps=1, color='royalblue'),
    'HiRadMat': Cycle(accelerator='PSB', name='LHC',    bps=1, color='royalblue'),
    'ZERO':     Cycle(accelerator='PSB', name='ZERO',   bps=1, color='#D3D3D3'),
    'MD':       Cycle(accelerator='PSB', name='MD',     bps=1, color='pink'),
    'Other':    Cycle(accelerator='PSB', name='Other',  bps=1, color='pink'),
}

PSCYCLES = {
    'AD':          Cycle(accelerator='PS', name='AD', bps=2,
                         coupled_cycle=PSBCYCLES['AD'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='AD', color='#800080'),
    'TOF':         Cycle(accelerator='PS', name='TOF', bps=1,
                         coupled_cycle=PSBCYCLES['TOF'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='TOF', color='#FFA500'),
    'EAST':        Cycle(accelerator='PS', name='EAST', bps=2,
                         coupled_cycle=PSBCYCLES['EAST'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='EAST1', color='#EE82EE'),
    'EAST T8':      Cycle(accelerator='PS', name='EAST T8', bps=2,
                         coupled_cycle=PSBCYCLES['EAST'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='EAST1', color='#EE82EE',
                         total_intensity_per_cycle = 80e10, transmission_to_destination=0.8),
    'EAST T9':      Cycle(accelerator='PS', name='EAST T9', bps=2,
                         coupled_cycle=PSBCYCLES['EAST'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='EAST1', color='#EE82EE',
                         total_intensity_per_cycle = 30e10, transmission_to_destination=0.8),
    'EAST TN':      Cycle(accelerator='PS', name='EAST TN', bps=2,
                         coupled_cycle=PSBCYCLES['EAST'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='EAST1', color='#EE82EE',
                         total_intensity_per_cycle = 30e10, transmission_to_destination=0.8),
    'MTE':         Cycle(accelerator='PS', name='MTE', bps=1,
                         coupled_cycle=PSBCYCLES['MTE'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='SFTPRO1', color='#8B0000'),
    'LHC filling': Cycle(accelerator='PS', name='LHC', bps=3,
                         coupled_cycle=PSBCYCLES['LHC'], number_of_injections=2, offset_to_upstream=1,
                         timing_user='LHC1', color='#FFD700'),
    'LHC pilot':   Cycle(accelerator='PS', name='LHC pilot', bps=2,
                         coupled_cycle=PSBCYCLES['LHC'], number_of_injections=1, offset_to_upstream=1,
                         color='#FFD700'),
    'AWAKE':       Cycle(accelerator='PS', name='AWAKE', bps=2,
                         coupled_cycle=PSBCYCLES['AWAKE'], number_of_injections=1, offset_to_upstream=1,
                         timing_user='AWAKE1', color='royalblue'),
    'HiRadMat':    Cycle(accelerator='PS', name='HiRadMat', bps=3,
                         coupled_cycle=PSBCYCLES['HiRadMat'], number_of_injections=2, offset_to_upstream=1,
                         timing_user='LHC1', color='royalblue'),
    'MD':          Cycle(accelerator='PS', name='MD', bps=3,
                         coupled_cycle=PSBCYCLES['Other'], number_of_injections=2, offset_to_upstream=1,
                         color='pink'),
    'SPSMD ded.':  Cycle(accelerator='PS', name='MD dedicated', bps=3,
                         coupled_cycle=PSBCYCLES['Other'], number_of_injections=2, offset_to_upstream=1,
                         color='pink'),
    'SPSMD par.':  Cycle(accelerator='PS', name='MD parallel', bps=2,
                         coupled_cycle=PSBCYCLES['Other'], number_of_injections=1, offset_to_upstream=1, 
                         color='pink'),
    'Scrubbing':   Cycle(accelerator='PS', name='Scrubbing', bps=3, color='pink'),
    'ZERO':        Cycle(accelerator='PS', name='ZERO', bps=1, color='#D3D3D3'),
}

SPSCYCLES = {
    'SFTPRO':       Cycle(accelerator='SPS', name='SFTPRO', bps=9,
                          coupled_cycle=PSCYCLES['MTE'], number_of_injections=2, offset_to_upstream=1,
                          timing_user='SFTPRO1',average_power=52.83, color='#8B0000'), 
    'LHC filling':  Cycle(accelerator='SPS', name='LHC filling', bps=20,
                          coupled_cycle=PSCYCLES['LHC filling'], number_of_injections=4, offset_to_upstream=2,
                          timing_user='LHC25NS',average_power=18.03, color='#FFD700'),
    'LHC pilot':    Cycle(accelerator='SPS', name='LHC pilot', bps=11,
                          coupled_cycle=PSCYCLES['LHC pilot'], number_of_injections=2, offset_to_upstream=1,
                          timing_user='LHCPILOT',average_power=32.5, color='#FFD700'),
    'MD dedicated': Cycle(accelerator='SPS', name='MD dedicated', bps=20,
                          coupled_cycle=PSCYCLES['SPSMD ded.'], number_of_injections=4, offset_to_upstream=2,
                          timing_user='MD5',average_power=18.03, color='pink'), # LHC25NS
    'MD parallel':  Cycle(accelerator='SPS', name='MD parallel', bps=6,
                          coupled_cycle=PSCYCLES['SPSMD par.'], number_of_injections=1, offset_to_upstream=1,
                          timing_user='MD5',average_power=2.81, color='pink'),
    'AWAKE':        Cycle(accelerator='SPS', name='AWAKE', bps=6,
                          coupled_cycle=PSCYCLES['AWAKE'], number_of_injections=1, offset_to_upstream=1,
                          timing_user='AWAKE1', average_power=31.19, color='royalblue'),
    'HiRadMat':     Cycle(accelerator='SPS', name='HiRadMat', bps=20,
                          coupled_cycle=PSCYCLES['HiRadMat'], number_of_injections=4, offset_to_upstream=2,
                          timing_user='HIRADMT2', average_power=17.52, color='royalblue'),
    'Scrubbing':    Cycle(accelerator='SPS', name='Scrubbing', bps=20, 
                          coupled_cycle=PSCYCLES['Scrubbing'], number_of_injections=4, offset_to_upstream=2,
                          timing_user='',average_power=18.03, color='pink'), # LHC25NS
    'Zero':         Cycle(accelerator='SPS', name='Zero', bps=1,
                          timing_user='ZERO',average_power=1.2, color='#D3D3D3'),
    'deGauss':      Cycle(accelerator='SPS', name='deGauss', bps=3,
                          timing_user='MD1',average_power=4.77, color='#D3D3D3')
}