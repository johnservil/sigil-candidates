"""chosen.html: the alphabet johnservil/sigil's alphabet/alphabet.py chooses, with sample sigils."""
import sys, json, collections, hashlib, html
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
sys.path.insert(0, '/workspace/sigil/python'); import sigilcode as S  # Sigil 0.1, the reference
fontjs = Path('/workspace/sigil/fonttest.html').read_text(encoding='utf-8')
fontjs = fontjs[fontjs.index('const c = document.createElement'):fontjs.index('</script>')]
def layout(N, L, b=2):
    assert N == 2048 and b == 2
    return S.layout(L)
def encode(a, data, b=2, marker=1):
    return S.encode(data)
a = sorted(map(ord, Path('/workspace/sigil/alphabet.txt').read_text(encoding='utf-8')))
assert len(a) == 2048
alpha = ''.join(map(chr, a))
per = ', '.join(f"{s.replace('_Aboriginal','')} {n}" for s, n in collections.Counter(p['script'][c] for c in a).most_common())
SIZES = (8, 10, 16, 20, 24, 32, 64)
samples = [(l, encode(a, hashlib.sha256(l.encode()).digest(), 2)) for l in ('one', 'two', 'three')]
samples.append(('BLAKE3 of nothing (32 bytes)', encode(a, bytes.fromhex('af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'), 2)))
for nb in SIZES:
    if nb != 32: samples.append((f'{nb} bytes ({8*nb}-bit)', encode(a, hashlib.sha512(str(nb).encode()).digest()[:nb], 2)))
table = ''.join(f'<tr><td>{8*L}-bit</td><td>{layout(2048, L, 2)[0]}</td><td>once in 2^{11 * layout(2048, L, 2)[0] - 8 * L}</td></tr>' for L in SIZES)
page = f'''<!doctype html><html lang="en" translate="no"><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sigil: the alphabet the rules choose</title>
<body class="notranslate" style="font-family:sans-serif;font-size:18px;max-width:46em;margin:1em auto;padding:0 0.6em">
<p><a href="index.html">all candidates</a></p>
<h3>Sigil 0.1's alphabet: 2,048 letters</h3>
<p>{html.escape(per)}. Chosen by <a href="https://github.com/johnservil/sigil">Sigil</a>'s alphabet rules from Unicode 14.0.0 and twelve font tests (macOS, iOS, Windows, Android and Linux, in Safari, Chrome, Brave and Firefox).</p>
<h4>Sample sigils (256-bit unless marked)</h4>
<div style="font-size:28px;line-height:1.6;word-break:break-all">{''.join(f'<div><span style="font-size:14px;color:#888">{html.escape(l)}</span><br>{s}</div>' for l, s in samples)}</div>
<h4>Characters for the sizes that matter most</h4>
<table style="border-collapse:collapse" cellpadding="4"><tr><th>data</th><th>characters</th><th>a random string decodes</th></tr>{table}</table>
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
