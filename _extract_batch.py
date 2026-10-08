# -*- coding: utf-8 -*-
# 提取第一批 8 个风格的官方 CSV 数据 + 现有样张 token，供精修子代理使用
import csv, json, re, sys
sys.path.insert(0, '.')
import generator as G

BATCH = ['Glassmorphism', 'Neubrutalism', 'Skeuomorphism', 'Spatial UI (VisionOS)',
         'Dark Mode (OLED)', 'Vaporwave', 'Pixel Art', 'Fluent 2']

rows = {r['Style Category']: r for r in csv.DictReader(
    open(G.SRC, encoding='utf-8')) if r['Status'] != 'deprecated'}

out = {}
for name in BATCH:
    r = rows[name]
    s = G.make_skin(r)
    fh, fb, fq = G.pick_fonts(r['Keywords'] + ' ' + r['Style Category'])
    out[name] = {
        'csv': {k: r[k].strip() for k in
                ('Type', 'Keywords', 'AI Prompt Keywords', 'Primary Colors',
                 'Effects & Animation', 'CSS/Technical Keywords',
                 'Implementation Checklist', 'Best For', 'Status')},
        'tokens': {
            'primary': s['primary'], 'secondary': s['secondary'], 'accent': s['accent'],
            'bg': s['bg'], 'fg': s['fg'], 'radius': s['radius'],
            'font_head': fh, 'font_body': fb,
        },
    }

json.dump(out, open('_batch1_styles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('dumped', len(out), 'styles to _batch1_styles.json')
for n in BATCH:
    print('-', n, '| file will be:', n[:20])
