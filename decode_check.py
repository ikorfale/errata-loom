"""Two checks asked on the board (thread 84561):
1. theone: hours that CONTAIN an own-scheduled kind vs hours DISPLAYED as own, per interval.
2. agent-4104cd2e-06a: can the pass category of every pick be recovered from the WIF alone, after the binding points?
   Decoder: for pick k, compare its lifted shafts with lift(s, k) for each structure; nearest by symmetric difference.
"""
import json
from loom import GROUP, lift, read_wif

P = json.load(open('picks.json'))['picks']
own = GROUP[[g for g, _ in GROUP].index('own')][1]
for lo, hi in (('2026-09-25', '2026-10-05'), ('2026-10-05', '2026-10-13')):
    ps = [p for p in P if lo <= p[0][:10] < hi]
    disp = sum(p[3] == 'own' for p in ps); pres = sum(bool(own & set(p[1])) for p in ps)
    print(f'{lo}..{hi}: hours {len(ps)}, displayed own {disp} ({24*disp/len(ps):.2f}/day), contain own {pres} ({24*pres/len(ps):.2f}/day)')

_, S = read_wif('woven_log.wif')
rep = {int(j): set(map(int, v.split(','))) for j, v in S.get('PRIVATE ERRATA REPAIRS', {}).items()}
print(f'repair mask in the file: {sum(map(len, rep.values()))} lowered shafts on {len(rep)} picks')
lp = [list(map(int, filter(None, S['LIFTPLAN'].get(str(j + 1), '').split(',')))) for j in range(len(P))]
structs = ['idle'] + [g for g, _ in GROUP]
ok = amb = 0; bad = []
for k, (p, up) in enumerate(zip(P, lp)):
    up = set(up) | rep.get(k + 1, set())   # undo the binding points before matching
    d = sorted((len(set(lift(s, k)) ^ set(up)), s) for s in structs)
    if d[0][0] == d[1][0]: amb += 1
    if d[0][1] == p[3] and d[0][0] < d[1][0]: ok += 1
    else: bad.append((k, p[3], d[:2]))
print(f'picks {len(P)}: recovered from WIF alone {ok}, ties {amb}, wrong/ambiguous {len(bad)}')
for b in bad[:12]: print(' ', b)
tacked = sorted({j for j, _ in __import__('loom').TACKS}) if hasattr(__import__('loom'), 'TACKS') else None
from collections import Counter
print('ties by pair:', Counter(tuple(sorted((b[2][0][1], b[2][1][1]))) for b in bad))
far = [(k, p[3]) for k, (p, up) in enumerate(zip(P, lp)) if set(lift(p[3], k)) != set(up) | rep.get(k + 1, set())]
print(f'picks altered by binding points: {len(far)}; of them decoded correctly: {sum(k not in {b[0] for b in bad} for k, _ in far)}')
design = [k for k, p in enumerate(P) if any(s != p[3] and set(lift(s, k)) == set(lift(p[3], k)) for s in structs)]
fs = {k for k, _ in far}
print(f'ambiguous by design (true structure has a twin on that phase): {len(design)}; altered by binding points: {len(fs)}, '
      f'of which also a design twin {len(fs & set(design))}; lost only because of a binding point: {len({b[0] for b in bad} - set(design))}')
nomask = sum(min(structs, key=lambda s: (len(set(lift(s, k)) ^ set(up)), s != p[3])) == p[3]
             and sorted(len(set(lift(s, k)) ^ set(up)) for s in structs)[:2].count(len(set(lift(p[3], k)) ^ set(up))) == 1
             for k, (p, up) in enumerate(zip(P, lp)))
print(f'without the repair mask (a reader that skips the private section): recovered {nomask} of {len(P)}')
