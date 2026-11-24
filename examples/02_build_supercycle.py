#%%
"""
02 - Building a supercycle: fixed period, automatic injections, wrap-around, editing.
"""
from supercycles import Supercycle, PlacementError

#%%
# A supercycle has a fixed period (in BP), common to PSB, PS and SPS
sc = Supercycle('My supercycle', period_bp=36)
print(sc)

#%%
# Adding an SPS cycle also places the PS and PSB cycles that inject into it.
# SFTPRO at BP 1 needs PS MTE at BP 0 and 1: BP 0 is the last BP of the previous
# repetition, i.e. BP 36 (wrap-around). The PSB MTE go to BP 35 and 36.
sc.add('SPS', 'SFTPRO', 1)
print(sc)

#%%
# Without a start BP, a cycle goes right after the previous one added to that machine
sc.add('SPS', 'deGauss')            # BP 10
sc.add('SPS', 'SFTPRO')             # BP 13
sc.add('SPS', 'deGauss')            # BP 22
sc.add('SPS', 'SFTPRO')             # BP 25
sc.add('SPS', 'deGauss')            # BP 34
print(sc)

#%%
# PS cycles for the East Area and nTOF, at explicit BPs
for bp in [2, 14, 20, 26]:
    sc.add('PS', 'EAST_T8', bp)
for bp in [4, 8, 16, 22, 28]:
    sc.add('PS', 'TOF', bp)
print(sc)

#%%
# Overlaps are refused, with the reason, and the supercycle is left unchanged
try:
    sc.add('PS', 'EAST_T9', 12)     # PS BP 12-13 feed the second SFTPRO
except PlacementError as error:
    print('Refused:', error)

#%%
# Fill all remaining PSB BPs with ISOLDE
n_added = sc.fill('PSB', 'ISOLDE')
print(f'{n_added} ISOLDE cycles added')
print(sc)

#%%
# Removing a cycle also removes the cycles injecting into it
sc.remove_at('PS', 4)               # the TOF at BP 4 (and its PSB TOF at BP 3)
print(sc)

#%%
# Everything is a placement: (id, cycle type, start BP, parent it injects into)
print(sc.to_dataframe().head(10))
print('PS free BPs:', sc.free_bps('PS'))
