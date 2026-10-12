"""Third-party check: open woven_log.wif with pyweaving (https://github.com/storborg/pyweaving, 0.0.7) and compare
its drawdown with the one loom.py wove. Usage: pip install pyweaving; python3 check_pyweaving.py"""
import numpy as np
from pyweaving.wif import WIFReader
d = WIFReader('woven_log.wif').read(); dd = np.load('drawdown.npy')
bad = sum((w.shaft in t.connected_shafts) != dd[j, i] for j, t in enumerate(d.weft) for i, w in enumerate(d.warp))
print(f'pyweaving: {len(d.warp)} ends, {len(d.weft)} picks, {len(d.shafts)} shafts, rising shed {d.rising_shed}; cells differing from loom.py: {bad}')
