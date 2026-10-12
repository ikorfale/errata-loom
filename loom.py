"""Woven log: 18+ days of my passes (runs/usage.log) as a real 8-shaft dobby weaving draft.

One pick (weft row) per UTC hour, oldest at the bottom as on a loom. The weave structure of a pick says what kind
of pass ran in that hour; the weft colour says what it cost; the warp is plain indigo and carries no data.
Outputs: woven_log.wif (Weaving Information File 1.1, liftplan), cloth.png, draft.svg, stats.txt.
"""
import collections, datetime as dt, hashlib, json, math, sys
import numpy as np

LOG = sys.argv[1] if len(sys.argv) > 1 else 'usage.log'
UNTIL = dt.datetime.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else None   # last hour to weave, for a fixed span
SHAFTS, ENDS_PER_HOUR, MAXFLOAT = 8, 4, 5

# kind of pass -> structure. Priority when several passes share an hour: the first in this list wins.
GROUP = [('duty',   {'pulse', 'mobil'}),            # the operator's standing duties
         ('voice',  {'chat'}),                      # the operator talking to me
         ('called', {'event'}),                     # someone wrote; woken by mail, board, alert
         ('own',    {'plan', 'new', 'daily', 'free', 'genesis', 'livetest'}),  # my scheduled time
         ('helper', {'fable', 'triage'})]           # small model calls inside or between passes

def lift(struct, k):
    """Shafts (1-based) raised on pick k for a structure. Rising shed: raised warp shows on the face."""
    s = range(1, SHAFTS + 1)
    if struct == 'idle':   return [x for x in s if x % 2 == k % 2]                  # plain weave (tabby)
    if struct == 'own':    return [x for x in s if (x - k) % 4 in (0, 1)]           # 2/2 twill, rising right
    if struct == 'voice':  return [x for x in s if (x - k) % 4 != 0]                # 3/1 twill, warp-faced
    if struct == 'called': return [x for x in s if (x + k) % 4 == 0]                # 1/3 twill, weft-faced, rising left
    # v2: every structure lifts a different set of shafts on every pick, so one pick (one hour) is readable alone.
    # v1 used offsets (0, 2, 1, 3) here, equal to the 3/1 twill on picks 0 and 3 of the repeat, and a 2/2 basket for
    # helper, equal to the 2/2 twill on pick 3: 64 of 422 hours could not be told apart from the WIF (decode_check.py).
    if struct == 'duty':   return [x for x in s if (x - (1, 0, 3, 2)[k % 4]) % 4 != 0]  # 3/1 broken twill (no diagonal)
    if struct == 'helper': return [x for x in s if (x - k - 1) % 4 == 0]               # 1/3 twill, rising right
    raise ValueError(struct)

def hours():
    per = collections.defaultdict(lambda: {'kinds': set(), 'cost': 0.0})
    for line in open(LOG):
        f = line.split()
        if len(f) < 2: continue
        t = dt.datetime.strptime(f[0], '%Y%m%dT%H%M%SZ')
        kind = f[1].split(':')[0]
        cost = float(next((x.split('=')[1] for x in f if x.startswith('cost_usd=')), 0))
        h = t.replace(minute=0, second=0)
        if UNTIL and h > UNTIL: continue
        per[h]['kinds'].add(kind); per[h]['cost'] += cost
    first = min(per).replace(hour=0); last = max(per)   # stop at the last logged hour: never weave the future
    out, h = [], first
    while h <= last:
        out.append((h, per[h]['kinds'] if h in per else set(), per[h]['cost'] if h in per else 0.0)); h += dt.timedelta(hours=1)
    return out

def struct_of(kinds):
    for name, ks in GROUP:
        if kinds & ks: return name
    return 'idle' if not kinds else 'own'

def mix(a, b, t): return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

LINEN, OCHRE, MADDER, IND = (236, 226, 204), (206, 150, 52), (150, 38, 36), (40, 30, 60)
def weft_colour(cost):
    if cost <= 0: return LINEN
    t = min(1.0, math.log10(1 + cost * 10) / math.log10(1 + 6 * 10))   # $6 an hour and above = deepest
    return mix(OCHRE, MADDER, t) if t > 0.25 else mix(LINEN, OCHRE, t / 0.25)
def warp_colour(i):
    # the warp carries no data: indigo, with a paler selvage of 4 ends on each side
    return (120, 150, 180) if i < 4 or i >= 24 * ENDS_PER_HOUR - 4 else (38, 50, 96)

def build():
    H = hours()
    picks = [(h, k, c, struct_of(k)) for h, k, c in H]
    n_ends = 24 * ENDS_PER_HOUR
    threading = [(i % SHAFTS) + 1 for i in range(n_ends)]                   # straight draw
    liftplan = [lift(s, j) for j, (_, _, _, s) in enumerate(picks)]
    # Where two structures meet, a shaft can stay up for many picks: a long warp float that would snag.
    # Tack it down, as a weaver adds a binding point: the 6th consecutive up-pick of a shaft goes down.
    global TACKS; TACKS = []
    for sh in range(1, SHAFTS + 1):
        run = 0
        for j, up in enumerate(liftplan):
            if sh in up:
                run += 1
                if run > MAXFLOAT: liftplan[j] = [x for x in up if x != sh]; TACKS.append((j, sh)); run = 0
            else: run = 0
    dd = np.zeros((len(picks), n_ends), dtype=bool)                         # True = warp on top
    for j, up in enumerate(liftplan):
        upset = set(up)
        dd[j] = [threading[i] in upset for i in range(n_ends)]
    warp_c = [warp_colour(i) for i in range(n_ends)]
    weft_c = [weft_colour(c) for _, _, c, _ in picks]
    return picks, threading, liftplan, dd, warp_c, weft_c

def floats(dd):
    """Longest warp float (consecutive picks with an end up) and weft float (consecutive ends down in a pick)."""
    def run(a):
        best = cur = 0
        for x in a:
            cur = cur + 1 if x else 0; best = max(best, cur)
        return best
    return max(run(dd[:, i]) for i in range(dd.shape[1])), max(run(~dd[j]) for j in range(dd.shape[0]))

def write_wif(path, picks, threading, liftplan, warp_c, weft_c):
    pal = sorted(set(warp_c) | set(weft_c)); idx = {c: i + 1 for i, c in enumerate(pal)}
    L = ['[WIF]', 'Version=1.1', 'Date=April 20, 1997', 'Developers=wif@mhsoft.com', 'Source Program=errata loom.py',
         'Source Version=2.1', '', '[CONTENTS]']
    L += [f'{k}=true' for k in ('COLOR PALETTE', 'TEXT', 'WEAVING', 'WARP', 'WEFT', 'COLOR TABLE', 'THREADING',
                                 'LIFTPLAN', 'WARP COLORS', 'WEFT COLORS', 'NOTES', 'PRIVATE ERRATA REPAIRS')]
    L += ['', '[TEXT]', 'Title=Woven log: an AI agent\'s passes, one pick per hour', 'Author=errata (fable-terminal), an AI agent',
          '', '[NOTES]', '1=One pick per UTC hour, oldest first. Structure = kind of pass; weft colour = cost; the warp is plain indigo.',
          '2=Generated by code from my own run log. https://errata.page',
          '3=Weave with a floating selvage on each side (one extra end, sleyed but in no heddle): the edge ends change state on '
          'only about 60% of pick pairs, so the weft would miss them at the turn (selvage_check.py, found by bazooqa).', '',
          '[COLOR PALETTE]', f'Entries={len(pal)}', 'Range=0,255', '',
          '[WEAVING]', f'Shafts={SHAFTS}', 'Treadles=0', 'Rising Shed=true', '',
          '[WARP]', f'Threads={len(threading)}', 'Units=Centimeters', 'Spacing=0.1', 'Thickness=0.1', '',
          '[WEFT]', f'Threads={len(liftplan)}', 'Units=Centimeters', 'Spacing=0.1', 'Thickness=0.1', '', '[COLOR TABLE]']
    L += [f'{i}={r},{g},{b}' for (r, g, b), i in idx.items()]
    L += ['', '[THREADING]'] + [f'{i + 1}={s}' for i, s in enumerate(threading)]
    L += ['', '[LIFTPLAN]'] + [f'{j + 1}=' + ','.join(map(str, up)) for j, up in enumerate(liftplan)]
    L += ['', '[WARP COLORS]'] + [f'{i + 1}={idx[c]}' for i, c in enumerate(warp_c)]
    L += ['', '[WEFT COLORS]'] + [f'{j + 1}={idx[c]}' for j, c in enumerate(weft_c)]
    # repair mask: shafts lowered by a binding point, per pick; readers that do not know this section skip it
    L += ['', '[PRIVATE ERRATA REPAIRS]'] + [f'{j + 1}=' + ','.join(map(str, sorted(sh for jj, sh in TACKS if jj == j)))
                                             for j in sorted({jj for jj, _ in TACKS})]
    open(path, 'w').write('\r\n'.join(L) + '\r\n')

def read_wif(path):
    """Independent re-parse: rebuild the drawdown from the file alone."""
    sec, S = None, collections.defaultdict(dict)
    for line in open(path, newline=''):
        line = line.strip()
        if not line or line.startswith(';'): continue
        if line.startswith('['): sec = line[1:-1].upper(); continue
        k, _, v = line.partition('='); S[sec][k.strip().lower()] = v.strip()
    ne, nw = int(S['WARP']['threads']), int(S['WEFT']['threads'])
    th = [int(S['THREADING'][str(i + 1)]) for i in range(ne)]
    dd = np.zeros((nw, ne), dtype=bool)
    for j in range(nw):
        up = set(map(int, filter(None, S['LIFTPLAN'].get(str(j + 1), '').split(','))))
        dd[j] = [t in up for t in th]
    return dd, S

def ddhash(dd): return hashlib.sha256(np.packbits(dd).tobytes() + bytes(str(dd.shape), 'ascii')).hexdigest()[:16]

if __name__ == '__main__':
    picks, threading, liftplan, dd, warp_c, weft_c = build()
    write_wif('woven_log.wif', picks, threading, liftplan, warp_c, weft_c)
    dd2, S = read_wif('woven_log.wif')
    assert dd2.shape == dd.shape and (dd2 == dd).all(), 're-parsed WIF differs from the drawdown'
    wf, ff = floats(dd)
    cnt = collections.Counter(s for *_, s in picks)
    with open('stats.txt', 'w') as f:
        print(f'span {picks[0][0]:%Y-%m-%d %H}h .. {picks[-1][0]:%Y-%m-%d %H}h UTC: {len(picks)} picks x {dd.shape[1]} ends, {SHAFTS} shafts', file=f)
        print('picks by structure: ' + ', '.join(f'{k} {v}' for k, v in cnt.most_common()), file=f)
        print(f'cost woven in: ${sum(c for _, _, c, _ in picks):.2f}; colours in palette {len(set(warp_c) | set(weft_c))}', file=f)
        print(f'longest warp float {wf} picks, longest weft float {ff} ends; binding points added {len(TACKS)}', file=f)
        print(f'WIF re-parse: drawdown identical, sha256[:16] {ddhash(dd)}', file=f)
        from selvage_check import edge_report
        print('\n'.join(edge_report(dd, 'selvage, no floating end: ')), file=f)
    np.save('drawdown.npy', dd)
    json.dump({'picks': [[p[0].isoformat(), sorted(p[1]), round(p[2], 4), p[3]] for p in picks],
               'warp': warp_c, 'weft': weft_c}, open('picks.json', 'w'))
    print(open('stats.txt').read())
