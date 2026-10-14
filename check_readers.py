"""Two more independent readers, run headless on woven_log.wif against loom.py's drawdown:
- Treadl (https://git.wilw.dev/cmd-Shift-Go/treadl, api/util/wif.py loads(); app-only imports stubbed)
- Wifferalls (https://github.com/RemiNelson/Wifferalls, scripts.js parseWIF()+extractDraft() in node, DOM stubbed)
Usage: clone both into readers/, then python3 check_readers.py [file.wif]"""
import sys, types, json, subprocess
import numpy as np
f = sys.argv[1] if len(sys.argv) > 1 else 'woven_log.wif'; dd = np.load('drawdown.npy')
for m in ('api', 'api.uploads', 'util', 'util.database', 'PIL', 'PIL.Image', 'PIL.ImageDraw'):
    sys.modules[m] = types.ModuleType(m)
sys.modules['api'].uploads = sys.modules['api.uploads']; sys.modules['util'].database = sys.modules['util.database']
sys.modules['PIL'].Image = sys.modules['PIL.Image']; sys.modules['PIL'].ImageDraw = sys.modules['PIL.ImageDraw']
sys.path.insert(0, 'readers/treadl/api/util'); import wif as T
d = T.loads(open(f, encoding='utf-8', newline='').read())
th = [t['shaft'] for t in d['warp']['threading']]; tr = [p['treadle'] for p in d['weft']['treadling']]
tu = d['tieups']
treadl = np.array([[th[i] in tu[tr[j] - 1] for i in range(len(th))] for j in range(len(tr))], dtype=bool)
def report(name, a):
    if a.shape != dd.shape: print(f'{name}: shape {a.shape} vs loom.py {dd.shape}'); return
    print(f'{name}: {a.shape[1]} ends, {a.shape[0]} picks; cells differing from loom.py: {int((a != dd).sum())}')
report('Treadl', treadl)
js = subprocess.run(['node', 'readers/wiff_run.js', f], capture_output=True, text=True)
if js.returncode: print('Wifferalls failed:', js.stderr[-800:])
else:
    o = json.loads(js.stdout); a = np.array(o['up'], dtype=bool)
    print(f"Wifferalls: rising shed {o['rising']}"); report('Wifferalls', a)
