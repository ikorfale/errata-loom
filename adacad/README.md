# AdaCAD WIF import check

Opens `woven_log.wif` with the WIF helpers of [AdaCAD](https://github.com/UnstableDesign/AdaCAD) (commit fc76462,
`projects/ui/src/app/core/model/wif.ts`, copied as `wif_upstream.ts` without the library import and logging).

- Upstream: every lift-plan pick keeps only its first shaft; 15,552 of 40,512 drawdown cells differ from `loom.py`.
- With the fix in `wif_fixed.ts` (3 changed lines): 0 cells differ; a 12-shaft treadled test draft reads 4/4 picks right.

Run (needs Node and TypeScript): `tsc --target es2022 --module nodenext --moduleResolution nodenext
--allowImportingTsExtensions --rewriteRelativeImportExtensions --outDir out *.ts && node out/test_wif.js && node out/run_adacad.js`.
Threading is reversed back to WIF order before comparing (AdaCAD stores `threading[warps - warp]`).
