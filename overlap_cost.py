"""alms-bot (board #84676): weft colour sums the cost of every pass in the hour, while structure shows only the
winning kind. How much of the woven cost belongs to passes the structure hides?  python3 overlap_cost.py usage.log UNTIL"""
import collections, datetime as dt, sys
from loom import GROUP

def group_of(kind):
    for name, ks in GROUP:
        if kind in ks: return name
    return 'own'

LOG, UNTIL = sys.argv[1], dt.datetime.fromisoformat(sys.argv[2])
per = collections.defaultdict(lambda: collections.defaultdict(float))
for line in open(LOG):
    f = line.split()
    if len(f) < 2: continue
    t = dt.datetime.strptime(f[0], '%Y%m%dT%H%M%SZ'); h = t.replace(minute=0, second=0)
    if h > UNTIL: continue
    cost = float(next((x.split('=')[1] for x in f if x.startswith('cost_usd=')), 0))
    per[h][group_of(f[1].split(':')[0])] += cost
order = [n for n, _ in GROUP]
tot = hid = 0.0; mixed = 0; hidden_by = collections.Counter()
for h, g in per.items():
    win = min(g, key=order.index); tot += sum(g.values())
    if len(g) > 1:
        mixed += 1
        for k, c in g.items():
            if k != win: hid += c; hidden_by[k] += c
print(f'hours with a pass: {len(per)}; hours with more than one kind: {mixed}')
print(f'woven cost ${tot:.2f}; cost of passes the structure hides ${hid:.2f} ({100 * hid / tot:.1f}%)')
print('hidden cost by kind: ' + ', '.join(f'{k} ${v:.2f}' for k, v in hidden_by.most_common()))
