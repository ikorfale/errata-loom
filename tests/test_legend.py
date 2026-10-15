"""Regression fixtures for the in-file legend (suggested by maestercallen on Moltbook):
a future change to the mapping or the decoder must still refuse what it cannot read and still read what it can.
Run: python3 -m unittest discover -s tests"""
import hashlib, os, re, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIX = os.path.join(HERE, 'fixtures')


def decode(*args):
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'legend_decode.py'), *args],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def resign(text):
    """recompute the legend digest the way legend_decode.py checks it (a forger who knows the scheme)"""
    lines = text.split('\n')
    a = lines.index('[PRIVATE ERRATA LEGEND]') + 1
    b = next((i for i in range(a, len(lines)) if lines[i].startswith('[')), len(lines))
    body = [l.strip() for l in lines[a:b] if l.strip() and not l.startswith(';')
            and l.split('=')[0].strip() not in ('Legend SHA256', 'Source Rows SHA256')]
    h = hashlib.sha256('\n'.join(body).encode()).hexdigest()
    return '\n'.join(re.sub(r'^Legend SHA256=.*', 'Legend SHA256=' + h, l) if a <= i < b else l
                     for i, l in enumerate(lines))


class LegendFixtures(unittest.TestCase):
    def test_current_file_reads_every_pick(self):
        rc, out = decode('woven_log.wif', 'picks.json')
        self.assertEqual(rc, 0, out)
        self.assertIn('ties 0', out)
        self.assertIn('agree with the published rows: 422 of 422', out)

    def test_v1_file_without_legend_is_refused(self):
        # v1 (32e4719) carried no legend; v2 code read it with 14 silently wrong hours (legend_drift.txt)
        rc, out = decode(os.path.join(FIX, 'v1.wif'))
        self.assertNotEqual(rc, 0)
        self.assertIn('no legend', out)

    def test_tampered_legend_is_refused(self):
        rc, out = decode(os.path.join(FIX, 'v2_tampered_legend.wif'))
        self.assertNotEqual(rc, 0)
        self.assertIn('does not match its digest', out)

    def test_resigned_swap_is_caught_only_by_the_source_rows(self):
        # the limit of a self-digest: swap duty and helper and re-sign; the file decodes "cleanly",
        # and only the comparison with the published rows shows the meaning moved
        t = open(os.path.join(ROOT, 'woven_log.wif'), encoding='utf-8').read()
        t = re.sub(r'^Lift\.duty\.', 'Lift.TMP.', t, flags=re.M)
        t = re.sub(r'^Lift\.helper\.', 'Lift.duty.', t, flags=re.M)
        t = re.sub(r'^Lift\.TMP\.', 'Lift.helper.', t, flags=re.M)
        with tempfile.NamedTemporaryFile('w', suffix='.wif', delete=False, encoding='utf-8') as f:
            f.write(resign(t))
        try:
            rc, out = decode(f.name, 'picks.json')
        finally:
            os.unlink(f.name)
        self.assertEqual(rc, 0, out)
        self.assertIn('legend digest ok', out)
        n = int(re.search(r'agree with the published rows: (\d+) of 422', out).group(1))
        self.assertLess(n, 422)


if __name__ == '__main__':
    unittest.main()
