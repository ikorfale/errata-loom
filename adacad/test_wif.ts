// Compare AdaCAD's WIF helpers (upstream vs fixed) on two files: my 8-shaft lift-plan draft, and a small
// 12-shaft treadled draft (two treadles on some picks, tie-up shafts >= 10) whose drawdown is known by construction.
import { readFileSync } from 'node:fs';
import * as up from './wif_upstream.ts';
import * as fx from './wif_fixed.ts';
const treadled = `[WIF]\nVersion=1.1\n[CONTENTS]\nWEAVING=true\nWARP=true\nWEFT=true\nTHREADING=true\nTIEUP=true\nTREADLING=true\n[WEAVING]\nShafts=12\nTreadles=4\n[WARP]\nThreads=12\n[WEFT]\nThreads=4\n[THREADING]\n${Array.from({length: 12}, (_, i) => `${i + 1}=${i + 1}`).join('\n')}\n[TIEUP]\n1=1,10\n2=2,11\n3=3,12\n4=4,5\n[TREADLING]\n1=1\n2=1,2\n3=3\n4=2,4\n`;
// expected lifted shafts per pick, from the tie-up by hand
const expected = [[1, 10], [1, 10, 2, 11], [3, 12], [2, 11, 4, 5]].map(r => r.map(x => x - 1).sort((a, b) => a - b));
for (const [name, m] of [['upstream', up], ['fixed', fx]] as const) {
  const s = m.getSubstringAfter('CONTENTS', readFileSync('../woven_log.wif', 'utf8').replace(/\r\n/g, '\n'));
  const lift = m.getLiftPlan(s, 422), counts = lift.map(r => r.length);
  const ref = readFileSync('../woven_log.wif', 'utf8').replace(/\r\n/g, '\n').split('[LIFTPLAN]')[1].split('[')[0].trim().split('\n').map(l => l.split('=')[1].split(',').length);
  const liftOk = counts.filter((c, i) => c === ref[i]).length;
  const t = m.getSubstringAfter('CONTENTS', treadled);
  const tie = m.getTieups(t, 12, 4), tr = m.getTreadling(t, 4);
  const got = tr.map(ts => [...new Set(ts.flatMap(k => tie.map((row, f) => row[k] ? f : -1).filter(f => f >= 0)))].sort((a, b) => a - b));
  const trOk = got.filter((g, i) => JSON.stringify(g) === JSON.stringify(expected[i])).length;
  console.log(`${name}: lift plan picks with the right number of shafts ${liftOk}/422; treadled picks correct ${trOk}/4`);
}
