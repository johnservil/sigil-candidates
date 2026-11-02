import sys, collections, math
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
R = dict((name, test) for name, test in A.rules(p))
names = [n for n, _ in A.rules(p)]
keep_rules = [n for n in names if not n.startswith('assigned by Unicode 5.2') and not n.startswith('a lowercase letter') and not n.startswith('its uppercase') and not n.startswith('Latin, Greek')]
pool = [c for c in range(0x800, 0x10000)]
for n in keep_rules: pool = [c for c in pool if R[n](c)]
pool = [c for c in pool if p['category'][c] == 'Lo' and p['bidi'][c] == 'L']
classes = collections.defaultdict(list)
for c in pool: classes[p["skeleton"].get(c, (c,))].append(c)
kept = set(min(cs) for cs in classes.values())
while True:
    sp = A.sequence_look_alikes(kept, p["skeleton"])
    if not sp: break
    counts = collections.Counter(x for whole, pieces in sp.items() for x in {whole} | {c for c in pieces if c >= 0x80})
    kept.discard(max(counts, key=lambda c: (counts[c], -c)))
by = collections.Counter(p['script'][c] for c in kept)
ages = collections.defaultdict(list)
for c in kept: ages[p['script'][c]].append(p['age'][c])
print(f"pool: {len(kept):,} characters in {len(by)} scripts (3-byte, caseless Lo, every other rule, look-alikes removed)")
for s, n in by.most_common():
    a = sorted(ages[s]); print(f"  {s:22} {n:5}  Unicode {'.'.join(map(str, a[0]))}-{'.'.join(map(str, a[-1]))}")
import json; json.dump(sorted(kept), open('/tmp/cand/pool.json', 'w'))
