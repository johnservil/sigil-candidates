import sys, collections, hashlib, html, math, json
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
base_rules = A.rules(p)[:-1]
pool_all = list(range(0x110000))
for name, test in base_rules: pool_all = [c for c in pool_all if test(c)]
def pipeline(ok):
    left = [c for c in pool_all if ok(c)]
    classes = collections.defaultdict(list)
    for c in left: classes[p["skeleton"].get(c, (c,))].append(c)
    kept = set(min(cs) for cs in classes.values())
    while True:
        sp = A.sequence_look_alikes(kept, p["skeleton"])
        if not sp: break
        counts = collections.Counter(x for whole, pieces in sp.items() for x in {whole} | {c for c in pieces if c >= 0x80})
        kept.discard(max(counts, key=lambda c: (counts[c], -c)))
    hexc = {p["skeleton"].get(ord(h), (ord(h),)) for h in "0123456789abcdef"}
    return sorted(c for c in kept if p["skeleton"].get(c, (c,)) not in hexc)
def isprime(k): return k > 1 and all(k % i for i in range(2, int(k**0.5) + 1))
def least_k(N):
    k = N + 1
    while not isprime(k): k += 1
    return k
def layout(N, L, b):
    """Fewest characters whose room holds 2^b marker values times a prime above N."""
    lk = least_k(N); n, pw = 0, 1
    while (pw >> (8*L + b)) < lk: pw *= N; n += 1
    k = pw >> (8*L + b)
    while not isprime(k): k -= 1
    return n, k
def encode(a, data, b=3, marker=1):
    N = len(a); n, k = layout(N, len(data), b)
    w = ((marker << (8*len(data))) + int.from_bytes(data, 'big')) * k
    out = []
    for _ in range(n): out.append(chr(a[w % N])); w //= N
    assert w == 0
    return ''.join(reversed(out))
sc = lambda c: p["script"].get(c)
three = lambda c: 0x800 <= c <= 0xFFFF
EC = ('Ethiopic', 'Canadian_Aboriginal')
INDIC = ('Devanagari', 'Bengali', 'Gurmukhi', 'Gujarati', 'Oriya', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Sinhala')
DEV_EXT = range(0xA8E0, 0xA900)  # Devanagari Extended: macOS 15 draws none of U+A8F2-A8F7, U+A8FB
variants = {
 'current': ('today\'s alphabet (1 to 3 bytes of UTF-8)', lambda c: (sc(c) in ('Latin','Greek','Cyrillic') and c < 0x800) or sc(c) in EC or 0x30 <= c <= 0x39),
 'ec': ('Ethiopic, Canadian syllabics', lambda c: three(c) and sc(c) in EC),
 'vai': ('Ethiopic, Canadian syllabics, Vai', lambda c: three(c) and sc(c) in EC + ('Vai',)),
 'indic': ('Ethiopic, Canadian syllabics, 10 Indic scripts', lambda c: three(c) and sc(c) in EC + INDIC and c not in DEV_EXT),
 'indic-no-kannada': ('Ethiopic, Canadian syllabics, 9 Indic scripts (no Kannada)', lambda c: three(c) and sc(c) in EC + tuple(s for s in INDIC if s != 'Kannada') and c not in DEV_EXT),
 'vai-indic': ('Ethiopic, Canadian syllabics, Vai, 10 Indic scripts', lambda c: three(c) and sc(c) in EC + ('Vai',) + INDIC and c not in DEV_EXT),
}
fontjs = Path('/workspace/sigil/fonttest.html').read_text(encoding='utf-8')
fontjs = fontjs[fontjs.index('const c = document.createElement'):fontjs.index('</script>')]
index = []
for slug, (title, ok) in variants.items():
    a = pipeline(ok); N = len(a)
    widths = collections.Counter(len(chr(c).encode()) for c in a)
    rows = []
    for L in (16, 24, 32, 64):
        n0, k0 = layout(N, L, 0); n3, k3 = layout(N, L, 3)
        R = N**n0 >> (8*L); bmax = int(math.floor(math.log2(R / least_k(N))))
        rows.append((8*L, n0, k0, bmax, n3, k3))
    print(f"{slug}: N={N:,} widths={dict(sorted(widths.items()))}")
    for bits, n0, k0, bmax, n3, k3 in rows:
        print(f"   {bits}-bit: {n0} chars, K {k0:,}; marker bits that fit in {n0}: {bmax}; with 3 marker bits: {n3} chars, K {k3:,}")
    samples = [(f'{l}', encode(a, hashlib.sha256(l.encode()).digest())) for l in ('one', 'two', 'three')]
    samples.append(('BLAKE3 of nothing (32 bytes)', encode(a, bytes.fromhex('af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'))))
    samples.append(('16 bytes', encode(a, hashlib.sha256(b'sixteen').digest()[:16])))
    samples.append(('64 bytes', encode(a, hashlib.sha512(b'sixty-four').digest())))
    per = ', '.join(f"{s.replace('_Aboriginal','')} {n}" for s, n in collections.Counter(sc(c) for c in a).most_common())
    alpha = ''.join(map(chr, a))
    table = ''.join(f'<tr><td>{b}-bit</td><td>{n0}</td><td>{bmax}</td><td>{n3}</td></tr>' for b, n0, k0, bmax, n3, k3 in rows)
    page = f'''<!doctype html><html lang="en" translate="no"><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sigil candidate: {html.escape(title)}</title>
<body class="notranslate" style="font-family:sans-serif;font-size:18px;max-width:46em;margin:1em auto;padding:0 0.6em">
<p><a href="index.html">all candidates</a></p>
<h3>{html.escape(title)}: {N:,} characters</h3>
<p>{html.escape(per)}. UTF-8 bytes a character: {", ".join(f"{k}: {v:,}" for k, v in sorted(widths.items()))}.</p>
<h4>Does this device draw every character?</h4>
<pre id="out" style="white-space:pre-wrap">measuring...</pre>
<h4>Sample sigils (256-bit unless marked; 3 marker bits)</h4>
<div style="font-size:28px;line-height:1.6;word-break:break-all">{''.join(f'<div><span style="font-size:14px;color:#888">{html.escape(l)}</span><br>{s}</div>' for l, s in samples)}</div>
<h4>Characters for common sizes</h4>
<table style="border-collapse:collapse" cellpadding="4"><tr><th>data</th><th>characters</th><th>marker bits that fit</th><th>characters with 3 marker bits</th></tr>{table}</table>
<h4>The whole alphabet</h4>
<p style="font-size:24px;word-break:break-all">{alpha}</p>
<script>
const ALPHABET = "{alpha}";
{fontjs}</script>
'''
    Path(f'/tmp/cand/{slug}.html').write_text(page, encoding='utf-8')
    index.append((slug, title, N, rows[2][1], rows[2][4]))
links = ''.join(f'<li><a href="{s}.html">{html.escape(t)}</a>: {N:,} characters; a 256-bit hash in {n0} (with 3 marker bits, {n3})</li>' for s, t, N, n0, n3 in index)
Path('/tmp/cand/index.html').write_text(f'''<!doctype html><html lang="en" translate="no"><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sigil: candidate alphabets</title><body class="notranslate" style="font-family:sans-serif;font-size:18px;max-width:46em;margin:1em auto;padding:0 0.6em">
<h3>Sigil: candidate alphabets</h3><p>Each page checks whether this device draws every character, and shows sample sigils. If your browser offers to translate a page, decline: translation replaces sigils with question marks.</p><ul>{links}</ul>''', encoding='utf-8')
