"""Decode the pass category of every pick from woven_log.wif alone: the mapping is read from the file's
[PRIVATE ERRATA LEGEND] section and checked against its own digest; no import from loom.py. A file without a legend,
or with a legend that does not match its digest, is refused instead of decoded with whatever mapping the code has now.
Usage: python3 legend_decode.py [file.wif] [picks.json to compare against]"""
import hashlib, json, sys
from collections import defaultdict

def sections(path):
    S, sec = defaultdict(list), None
    for line in open(path, newline='', encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith(';'): continue
        if line.startswith('['): sec = line[1:-1].upper(); continue
        k, _, v = line.partition('='); S[sec].append((k.strip(), v.strip()))
    return S

f = sys.argv[1] if len(sys.argv) > 1 else 'woven_log.wif'
S = sections(f)
leg = S.get('PRIVATE ERRATA LEGEND')
if not leg: sys.exit(f'{f}: no legend in the file; refusing to guess the mapping')
body = [f'{k}={v}' for k, v in leg if k not in ('Legend SHA256', 'Source Rows SHA256')]
meta = dict(leg)
if hashlib.sha256('\n'.join(body).encode()).hexdigest() != meta.get('Legend SHA256'):
    sys.exit(f'{f}: legend does not match its digest; refusing')
lift = {}
for k, v in leg:
    if k.startswith('Lift.'):
        _, st, ph = k.split('.'); lift[(st, int(ph))] = set(map(int, filter(None, v.split(','))))
structs = sorted({st for st, _ in lift})
rep = {int(j): set(map(int, v.split(','))) for j, v in S.get('PRIVATE ERRATA REPAIRS', [])}
lp = dict(S['LIFTPLAN']); n = int(dict(S['WEFT'])['Threads'])
out = []
for k in range(n):
    up = set(map(int, filter(None, lp.get(str(k + 1), '').split(',')))) | rep.get(k + 1, set())
    d = sorted((len(lift[(st, k % 4)] ^ up), st) for st in structs)
    out.append(d[0][1] if d[0][0] < d[1][0] else None)
print(f'{f}: mapping version {meta.get("Mapping Version")}, legend digest ok; {n} picks, decoded {sum(x is not None for x in out)}, ties {out.count(None)}')
if len(sys.argv) > 2:
    rows = json.load(open(sys.argv[2]))['picks']
    src = hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
    print(f'source rows digest {"matches" if src == meta.get("Source Rows SHA256") else "DIFFERS from"} {sys.argv[2]}')
    print(f'agree with the published rows: {sum(o == r[3] for o, r in zip(out, rows))} of {len(rows)}')
