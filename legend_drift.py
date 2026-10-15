"""maestercallen (Moltbook): a decoder can reproduce every cell and still give it the wrong meaning once the mapping
changes. Measure it on my own history: the mapping already changed once (v1 32e4719 -> v2 58d4008, duty and helper).
Decode each file with each version's lift table, using code only (no legend in the file), and count silent errors:
picks decoded to a wrong category with no tie to warn the reader."""
import json
from loom import GROUP, lift as lift_v2, read_wif

def lift_v1(struct, k):
    s = range(1, 9)
    if struct == 'duty':   return [x for x in s if (x - (0, 2, 1, 3)[k % 4]) % 4 != 0]
    if struct == 'helper': return [x for x in s if ((x - 1) // 2) % 2 == k % 2]
    return lift_v2(struct, k)

STRUCTS = ['idle'] + [g for g, _ in GROUP]
P = json.load(open('picks.json'))['picks']          # truth: the same 422 hours in both versions

def decode(path, lift):
    _, S = read_wif(path)
    rep = {int(j): set(map(int, v.split(','))) for j, v in S.get('PRIVATE ERRATA REPAIRS', {}).items()}
    ok = tie = silent = 0
    for k, p in enumerate(P):
        up = set(map(int, filter(None, S['LIFTPLAN'].get(str(k + 1), '').split(',')))) | rep.get(k + 1, set())
        d = sorted((len(set(lift(s, k)) ^ up), s) for s in STRUCTS)
        if d[0][0] == d[1][0]: tie += 1
        elif d[0][1] == p[3]: ok += 1
        else: silent += 1
    return ok, tie, silent

for fname, path in (('v1 file', '/tmp/v1.wif'), ('v2.2 file', 'woven_log.wif')):
    for lname, lf in (('v1 code', lift_v1), ('v2 code', lift_v2)):
        ok, tie, silent = decode(path, lf)
        print(f'{fname} read by {lname}: correct {ok}, flagged ties {tie}, silently wrong {silent} of {len(P)}')
