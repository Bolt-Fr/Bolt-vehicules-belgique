import csv, json, base64
from collections import Counter

CAT_ORDER = ['Comfort', 'Premium', 'Electric Comfort', 'XL', 'Van']
ZONES = {'BRU', 'FLA', 'WAL'}   # Bruxelles, Flandre, Wallonie

rows, seen, problems = [], set(), []
with open('vehicles.csv', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for n, row in enumerate(reader, start=2):
        if len(row) < 4:
            continue
        c, b, m, z = (x.strip() for x in row[:4])
        if not c or not b or not m:
            continue
        zones = [x.strip() for x in z.split(';') if x.strip()]
        if c not in CAT_ORDER:
            problems.append('ligne %d : catégorie inconnue "%s"' % (n, c))
        if not zones or any(x not in ZONES for x in zones):
            problems.append('ligne %d : zones invalides "%s" (BRU;FLA;WAL)' % (n, z))
        key = (c, b.lower(), m.lower(), ';'.join(sorted(zones)))
        if key in seen:
            continue
        seen.add(key)
        rows.append((c, b, m, ';'.join(zones)))

if problems:
    raise SystemExit('Erreurs dans vehicles.csv :\n' + '\n'.join(problems))

rows.sort(key=lambda r: (CAT_ORDER.index(r[0]), r[1], r[2]))
raw_js = ',\n'.join(json.dumps(list(r), ensure_ascii=False) for r in rows)
logo_b64 = base64.b64encode(open('logo.png', 'rb').read()).decode()

html = open('template.html', encoding='utf-8').read()
html = html.replace('/*ROWS*/', raw_js).replace('/*LOGO_B64*/', logo_b64)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('index.html generated successfully')
for z in sorted(ZONES):
    cnt = Counter(r[0] for r in rows if z in r[3].split(';'))
    print(' ', z, {c: cnt[c] for c in CAT_ORDER if cnt[c]})
