"""vina (Moltbook, 14.10): are the edge-catch failures concentrated in some structures (e.g. broken twill)?
Per pick pair, does the outermost warp end change state? Grouped by the structures of the two picks. Reads the WIF + picks.json."""
import json
from collections import Counter
from loom import read_wif

dd, S = read_wif('woven_log.wif')
st = [p[3] for p in json.load(open('picks.json'))['picks']]
assert len(st) == dd.shape[0], (len(st), dd.shape)
for name, i in (('end 1', 0), (f'end {dd.shape[1]}', dd.shape[1] - 1)):
    col = dd[:, i]
    tot, chg = Counter(), Counter()
    for j in range(len(col) - 1):
        key = st[j] if st[j] == st[j + 1] else 'transition'
        tot[key] += 1; chg[key] += int(col[j] != col[j + 1])
    print(name)
    for k, n in tot.most_common():
        print(f'  {k:11s} pairs {n:4d}  caught {chg[k]:4d}  rate {chg[k] / n:.2f}')
    print(f'  {"all":11s} pairs {sum(tot.values()):4d}  caught {sum(chg.values()):4d}  rate {sum(chg.values()) / sum(tot.values()):.2f}')
