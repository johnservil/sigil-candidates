"""chosen.html: the alphabet johnservil/sigil's alphabet/alphabet.py chooses, with sample sigils."""
import sys, json, collections, hashlib, html
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
def isprime(k): return k > 1 and all(k % i for i in range(2, int(k**0.5) + 1))
def layout(N, L, b):
    """Fewest characters whose room holds 2^b marker values times a prime above N; the largest such prime."""
    lk = N + 1
    while not isprime(lk): lk += 1
    n, pw = 0, 1
    while (pw >> (8*L + b)) < lk: pw *= N; n += 1
    k = pw >> (8*L + b)
    while not isprime(k): k -= 1
    return n, k
def encode(a, data, b=2, marker=1):
    N = len(a); n, k = layout(N, len(data), b)
    w = ((marker << (8*len(data))) + int.from_bytes(data, 'big')) * k
    out = []
    for _ in range(n): out.append(chr(a[w % N])); w //= N
    assert w == 0
    return ''.join(reversed(out))
fontjs = Path('/workspace/sigil/fonttest.html').read_text(encoding='utf-8')
fontjs = fontjs[fontjs.index('const c = document.createElement'):fontjs.index('</script>')]
a = sorted(map(ord, Path('/workspace/sigil/alphabet.txt').read_text(encoding='utf-8')))
assert len(a) == 2048
alpha = ''.join(map(chr, a))
per = ', '.join(f"{s.replace('_Aboriginal','')} {n}" for s, n in collections.Counter(p['script'][c] for c in a).most_common())
SIZES = (8, 10, 16, 20, 24, 32, 64)
samples = [(l, encode(a, hashlib.sha256(l.encode()).digest(), 2)) for l in ('one', 'two', 'three')]
samples.append(('BLAKE3 of nothing (32 bytes)', encode(a, bytes.fromhex('af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'), 2)))
for nb in SIZES:
    if nb != 32: samples.append((f'{nb} bytes ({8*nb}-bit)', encode(a, hashlib.sha512(str(nb).encode()).digest()[:nb], 2)))
table = ''.join(f'<tr><td>{8*L}-bit</td><td>{layout(2048, L, 2)[0]}</td><td>1 in {layout(2048, L, 2)[1]:,}</td></tr>' for L in SIZES)
page = f'''<!doctype html><html lang="en" translate="no"><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sigil: the alphabet the rules choose</title>
<body class="notranslate" style="font-family:sans-serif;font-size:18px;max-width:46em;margin:1em auto;padding:0 0.6em">
<p><a href="index.html">all candidates</a></p>
<h3>The alphabet the rules choose: 2,048 letters</h3>
<p>{html.escape(per)}. Chosen by <a href="https://github.com/johnservil/sigil">Sigil</a>'s alphabet rules from Unicode 14.0.0 and twelve font tests (macOS, iOS, Windows, Android and Linux, in Safari, Chrome, Brave and Firefox).</p>
<h4>Sample sigils (256-bit unless marked)</h4>
<div style="font-size:28px;line-height:1.6;word-break:break-all">{''.join(f'<div><span style="font-size:14px;color:#888">{html.escape(l)}</span><br>{s}</div>' for l, s in samples)}</div>
<h4>Characters for the sizes that matter most</h4>
<table style="border-collapse:collapse" cellpadding="4"><tr><th>data</th><th>characters</th><th>a random error passes</th></tr>{table}</table>
<h4>Does this device draw every letter?</h4>
<pre id="out" style="white-space:pre-wrap">measuring...</pre>
<h4>The whole alphabet</h4>
<p style="font-size:24px;word-break:break-all">{alpha}</p>
<script>
const ALPHABET = "{alpha}";
{fontjs}</script>
'''
Path('/tmp/cand/chosen.html').write_text(page, encoding='utf-8')
print(samples[3][1])
