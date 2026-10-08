# -*- coding: utf-8 -*-
import csv, json, sys
sys.path.insert(0, '.')
import generator as G

BATCH = ['Y2K Aesthetic', 'Vintage Analog / Retro Film', 'Motion-Driven Design',
         'Micro-Interactions', 'Parallax Storytelling', 'Gen-Z Chaos Maximalism',
         'Dimensional Layering', 'Minimalist Monochrome']
rows = {r['Style Category']: r for r in csv.DictReader(open(G.SRC, encoding='utf-8')) if r['Status'] != 'deprecated'}
missing = [n for n in BATCH if n not in rows]
assert not missing, missing

out = {}
for name in BATCH:
    r = rows[name]
    s = G.make_skin(r)
    fh, fb, fq = G.pick_fonts(r['Keywords'] + ' ' + r['Style Category'])
    out[name] = {
        'csv': {k: r[k].strip() for k in ('Type', 'Keywords', 'AI Prompt Keywords', 'Primary Colors',
                 'Effects & Animation', 'CSS/Technical Keywords', 'Implementation Checklist', 'Best For', 'Status')},
        'tokens': {'primary': s['primary'], 'secondary': s['secondary'], 'accent': s['accent'],
                   'bg': s['bg'], 'fg': s['fg'], 'radius': s['radius'], 'font_head': fh, 'font_body': fb},
        'file': G.slug(name) + '.html',
    }
json.dump(out, open('_batch4_styles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    print('%-32s -> %s' % (k, v['file']))
