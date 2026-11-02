import sys, json, collections
from pathlib import Path
sys.path.insert(0, '/workspace/sigil/alphabet'); import alphabet as A
p = A.properties(Path('/tmp/ucd'))
pool = json.load(open('/tmp/cand/pool.json'))
pool = [c for c in pool if p['script'][c] not in ('Common', 'Inherited')]   # a letter of a named script
by = collections.defaultdict(list)
for c in pool: by[p['script'][c]].append(c)
def select(drawn):
    """Scripts with font evidence, the largest first (the fewest fonts), ties to the
    oldest first letter, until 2,048; then the 2,048 oldest letters, ties to the lowest code point."""
    order = sorted((s for s in by if drawn is None or s in drawn), key=lambda s: (-len(by[s]), min(p['age'][c] for c in by[s]), s))
    chosen, total = [], 0
    for s in order:
        if total >= 2048: break
        chosen.append(s); total += len(by[s])
    letters = [c for s in chosen for c in by[s]]
    if len(letters) < 2048: return chosen, None, len(letters)
    keep = sorted(sorted(letters, key=lambda c: (p['age'][c], c))[:2048])
    return chosen, keep, len(letters)
mac_seen = {'Ethiopic', 'Canadian_Aboriginal', 'Vai', 'Tifinagh', 'Georgian', 'Devanagari', 'Bengali', 'Gurmukhi', 'Gujarati', 'Oriya', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Sinhala'}
for label, drawn in (('no font evidence (every script)', None), ("scripts the Mac has drawn so far", mac_seen)):
    chosen, keep, total = select(drawn)
    print(f"\n{label}: {len(chosen)} scripts, {total:,} letters before the trim")
    print('  ' + ', '.join(f"{s.replace('_Aboriginal','')} {len(by[s])}" for s in chosen))
    if keep:
        cut = collections.Counter(p['script'][c] for c in set(c for s in chosen for c in by[s]) - set(keep))
        print('  trimmed by age:', dict(cut))
        json.dump(keep, open(f"/tmp/cand/select-{'all' if drawn is None else 'mac'}.json", 'w'))
    else:
        print('  short of 2,048')
