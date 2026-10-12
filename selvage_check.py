"""Selvage check (bazooqa, board #84641): does the outermost warp end change state between consecutive picks?
If it does not, the weft misses it at the turn and the edge end floats. Reads the WIF alone."""
import sys
from loom import read_wif

def edge_report(dd, label):
    out = []
    for name, i in (('end 1', 0), (f'end {dd.shape[1]}', dd.shape[1] - 1)):
        col = dd[:, i]
        same = sum(col[j] == col[j + 1] for j in range(len(col) - 1))
        best = cur = 1
        for j in range(1, len(col)):
            cur = cur + 1 if col[j] == col[j - 1] else 1; best = max(best, cur)
        out.append(f'{label}{name:7s} same state on {same}/{len(col) - 1} pick pairs, longest same-state run {best} picks')
    return out

if __name__ == '__main__':
    dd, S = read_wif(sys.argv[1] if len(sys.argv) > 1 else 'woven_log.wif')
    print('\n'.join(edge_report(dd, '')))
