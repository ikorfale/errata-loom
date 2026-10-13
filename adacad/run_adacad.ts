// Parse woven_log.wif with AdaCAD's own WIF helpers (copied verbatim from UnstableDesign/AdaCAD fc76462,
// projects/ui/src/app/core/model/wif.ts, minus the library import and console.log) and write the drawdown.
import { readFileSync, writeFileSync } from 'node:fs';
import { getInt, getSubstringAfter, getLiftPlan, getThreading } from './wif_upstream.ts';
let data = readFileSync('../woven_log.wif', 'utf8').replace(/\r\n/g, '\n');
const s = getSubstringAfter('CONTENTS', data);
const warps = getInt('Threads', getSubstringAfter('WARP]', s)), wefts = getInt('Threads', getSubstringAfter('WEFT]', s));
const lift = getLiftPlan(s, wefts), thr = getThreading(s, warps);
// AdaCAD stores threading reversed (threading[warps - warp]); undo it to compare in WIF order
const thrWif = thr.slice().reverse();
const dd = lift.map(row => thrWif.map(f => row.includes(f) ? 1 : 0));
const lifted = lift.map(r => r.length);
writeFileSync('adacad_drawdown.json', JSON.stringify(dd));
console.log(`AdaCAD parse: ${warps} ends, ${wefts} picks; shafts lifted per pick: min ${Math.min(...lifted)} max ${Math.max(...lifted)}`);
