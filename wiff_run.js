// Threading, liftplan and pick numbers are 1-indexed in Wifferalls, as in the file.
// Load Wifferalls' scripts.js in a sandbox with a stub DOM, then use its own parseWIF + extractDraft.
const fs = require('fs'), vm = require('vm');
const stub = new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => '' : stub, apply: () => stub, construct: () => stub, set: () => true });
const ctx = { document: stub, window: stub, localStorage: stub, navigator: stub, console, setTimeout: () => 0, requestAnimationFrame: () => 0,
              ResizeObserver: function () { return stub; }, matchMedia: () => stub, location: stub, jspdf: stub, Image: function () { return stub; } };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(__dirname + '/readers/Wifferalls/scripts.js', 'utf8') + '\n;this.__p = parseWIF; this.__x = extractDraft; this.__set = (v) => { wifData = v; };', ctx);
ctx.__set(ctx.__p(fs.readFileSync(process.argv[2], 'utf8')));
const d = ctx.__x(), up = [];
for (let j = 1; j <= d.weftThreads; j++) {
  const s = d.getRaisedShafts(j), row = [];
  for (let i = 1; i <= d.warpThreads; i++) { const sh = d.threading[i]; const lifted = (Array.isArray(sh) ? sh : [sh]).some(x => s.has(x)); row.push(d.risingShed ? lifted : !lifted); }
  up.push(row);
}
process.stdout.write(JSON.stringify({ rising: d.risingShed, up }));
