import sys, collections, hashlib, html
from pathlib import Path
exec(open('/tmp/cand/gen.py').read().split("fontjs = ")[0])
fontjs = Path('/workspace/sigil/fonttest.html').read_text(encoding='utf-8')
fontjs = fontjs[fontjs.index('const c = document.createElement'):fontjs.index('</script>')]
BASE = EC + ('Vai', 'Georgian', 'Tifinagh') + INDIC
EXTRAS = ('Tibetan', 'Runic', 'Coptic', 'Glagolitic', 'Javanese', 'Lepcha', 'Balinese', 'Cham', 'Saurashtra', 'Bamum')
SIZES = (8, 10, 16, 24, 32, 64)
rows = []
for extra in EXTRAS:
    full = pipeline(lambda c: three(c) and sc(c) in BASE + (extra,) and c not in DEV_EXT)
    # Keep the 2,048 oldest by Unicode version, ties to the lowest code point.
    keep = sorted(sorted(full, key=lambda c: (p['age'][c], c))[:2048])
    trimmed = sorted(set(full) - set(keep))
    assert len(keep) == 2048
    a = keep
    alpha = ''.join(map(chr, a))
    per = ', '.join(f"{s.replace('_Aboriginal','')} {n}" for s, n in collections.Counter(sc(c) for c in a).most_common())
    tr = ', '.join(f"{s} {n}" for s, n in collections.Counter(sc(c) for c in trimmed).most_common())
    ages = collections.Counter('.'.join(map(str, p['age'][c])) for c in trimmed)
    samples = [(l, encode(a, hashlib.sha256(l.encode()).digest(), 2)) for l in ('one', 'two', 'three')]
    samples.append(('BLAKE3 of nothing (32 bytes)', encode(a, bytes.fromhex('af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'), 2)))
    for nb in SIZES:
        if nb != 32: samples.append((f'{nb} bytes', encode(a, hashlib.sha512(str(nb).encode()).digest()[:nb], 2)))
    slug = f"2048-{extra.lower()}"
    table = ''.join(f'<tr><td>{8*L}-bit</td><td>{layout(2048, L, 2)[0]}</td><td>1 in {layout(2048, L, 2)[1]:,}</td></tr>' for L in SIZES)
    page = f'''<!doctype html><html lang="en" translate="no"><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sigil candidate: 2,048 characters with {extra}</title>
<body class="notranslate" style="font-family:sans-serif;font-size:18px;max-width:46em;margin:1em auto;padding:0 0.6em">
<p><a href="index.html">all candidates</a></p>
<h3>2,048 characters: the 2,011-character set plus {html.escape(extra)}</h3>
<p>{html.escape(per)}. Every character is three bytes of UTF-8.</p>
<p style="font-size:15px;color:#555">Trimmed to 2,048 by keeping the characters with the oldest Unicode version (ties to the lowest code point): {len(trimmed)} left out ({html.escape(tr)}; added in Unicode {", ".join(sorted(ages))}).</p>
<h4>Does this device draw every character?</h4>
<pre id="out" style="white-space:pre-wrap">measuring...</pre>
<h4>Sample sigils (256-bit unless marked)</h4>
<div style="font-size:28px;line-height:1.6;word-break:break-all">{''.join(f'<div><span style="font-size:14px;color:#888">{html.escape(l)}</span><br>{s}</div>' for l, s in samples)}</div>
<h4>Characters for common sizes (2 marker bits)</h4>
<table style="border-collapse:collapse" cellpadding="4"><tr><th>data</th><th>characters</th><th>a random error passes</th></tr>{table}</table>
<h4>The whole alphabet</h4>
<p style="font-size:24px;word-break:break-all">{alpha}</p>
<script>
const ALPHABET = "{alpha}";
{fontjs}</script>
'''
    Path(f'/tmp/cand/{slug}.html').write_text(page, encoding='utf-8')
    rows.append((slug, extra, len(full), len(trimmed), tr))
    print(f"{extra}: {len(full):,} before the trim; left out {len(trimmed)} ({tr})")
links = ''.join(f'<li><a href="{s}.html">2,048 with {html.escape(e)}</a> ({t} left out by age)</li>' for s, e, f, t, tr in rows)
idx = Path('/tmp/cand/index.html').read_text(encoding='utf-8')
marker = '<h4>2,048 characters'
if marker in idx: idx = idx[:idx.index(marker)]
idx = idx.replace('</ul>', '</ul>', 1)
idx += f'''<h4>2,048 characters: encoding and decoding in linear, constant time</h4><p>With exactly 2,048 characters, each is 11 bits. The 2,011-character set plus one more script, trimmed to 2,048 by oldest Unicode version. Please report each page's "drawn" line.</p><ul>{links}</ul>'''
Path('/tmp/cand/index.html').write_text(idx, encoding='utf-8')
