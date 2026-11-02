import sys, json, re, collections
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
iss = json.load(open('/tmp/cand/issues.json'))
pool = [c for c in json.load(open('/tmp/cand/pool.json')) if p['script'][c] not in ('Common', 'Inherited')]
# The look-alike rules ran over the whole pool there; G3 now runs within the scripts taken,
# so start from the letters before any look-alike rule.
R = dict(A.rules(p)); names = [n for n, _ in A.rules(p)]
keep_rules = [n for n in names if not n.startswith('assigned by Unicode 5.2') and not n.startswith('a lowercase letter') and not n.startswith('its uppercase') and not n.startswith('Latin, Greek')]
raw = list(range(0x800, 0x10000))
for n in keep_rules: raw = [c for c in raw if R[n](c)]
raw = [c for c in raw if p['category'][c] == 'Lo' and p['bidi'][c] == 'L' and p['script'][c] not in ('Common', 'Inherited')]
tested = set(pool)
missing = {}
platforms = []
for i in sorted(iss, key=lambda i: i['number']):
    body = i['body']; ua = body.split('\n')[1]
    miss = set()
    for line in body.split('\n'):
        m = re.match(r'(\S+): (\d+)/(\d+)(?: missing (.*))?$', line.strip())
        if m and m.group(4):
            for r in m.group(4).split():
                a, _, b = r.partition('-'); a = int(a, 16); b = int(b or a, 16) if b else a
                miss |= set(range(a, b + 1))
    name = ('iOS' if 'iPhone' in ua else 'macOS' if 'Macintosh' in ua else 'Linux') + ' ' + ('Firefox' if 'Firefox' in ua else 'Brave' if 'Brave' in ua else 'Safari' if 'Version/' in ua else 'Chromium')
    if i['user']['login'] == 'zookoatshieldedlabs': name += ' (second account)'
    platforms.append((i['number'], name, ua, len(miss)))
    missing[i['number']] = miss
for n, name, ua, k in platforms: print(f"#{n} {name}: {k} of {len(tested):,} letters missing")
everywhere = {c for c in tested if not any(c in m for m in missing.values())}
untested = set(raw) - tested
print(f"drawn on every platform: {len(everywhere):,} of {len(tested):,} tested")
by_missing = collections.Counter(p['script'][c] for c in tested - everywhere)
print('letters some platform lacks, by script:', dict(by_missing.most_common()))
json.dump({'platforms': platforms, 'missing': {str(k): sorted(v) for k, v in missing.items()}}, open('/tmp/cand/fonts.json', 'w'))
# Selection, as RULES.md orders it: G1 fonts, G2 fewest scripts, G3 look-alikes within the letters taken, G4 oldest first.
ok = [c for c in raw if c in everywhere]   # untested letters (removed earlier as look-alikes) count as undrawn
by = collections.defaultdict(list)
for c in ok: by[p['script'][c]].append(c)
order = sorted(by, key=lambda s: (-len(by[s]), min(p['age'][c] for c in by[s]), s))
def lookalikes(letters):
    classes = collections.defaultdict(list)
    for c in letters: classes[p["skeleton"].get(c, (c,))].append(c)
    kept = set(min(cs) for cs in classes.values())
    while True:
        sp = A.sequence_look_alikes(kept, p["skeleton"])
        if not sp: break
        counts = collections.Counter(x for whole, pieces in sp.items() for x in {whole} | {c for c in pieces if c >= 0x80})
        kept.discard(max(counts, key=lambda c: (counts[c], -c)))
    return kept
chosen = []
for s in order:
    chosen.append(s)
    kept = lookalikes([c for t in chosen for c in by[t]])
    if len(kept) >= 2048: break
final = sorted(sorted(kept, key=lambda c: (p['age'][c], c))[:2048])
print(f"\nselection: {len(chosen)} scripts; {len(kept):,} letters after look-alikes; trimmed by age to {len(final):,}")
print('  scripts taken (letters drawn everywhere):', ', '.join(f"{s.replace('_Aboriginal','')} {len(by[s])}" for s in chosen))
print('  in the alphabet:', dict(collections.Counter(p['script'][c].replace('_Aboriginal','') for c in final).most_common()))
cut = collections.Counter(p['script'][c] for c in kept - set(final))
print('  trimmed by age:', dict(cut), ' newest kept: Unicode', '.'.join(map(str, max(p['age'][c] for c in final))))
json.dump(final, open('/tmp/cand/final.json', 'w'))
