# -*- coding: utf-8 -*-
"""风格样张生成器（数据驱动版）。

数据源全部来自 ui-ux-pro-max 官方库：
  styles.csv      —— 色板 / 效果 / CSS 关键词 / 官方提示词 / 检查清单
  typography.csv  —— 官方字体配对（按 Mood 关键词匹配）

本脚本只做「翻译」：把官方字段转成 CSS；不自行发明配色与参数。
CSV 更新后直接重跑: python generator.py
"""
import csv, re, html, os, colorsys, hashlib, json
import content_styles

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = r'E:\sklls\ui-ux-pro-max-skill\.claude\skills\ui-ux-pro-max\data\styles.csv'
SRC_TYPO = r'E:\sklls\ui-ux-pro-max-skill\.claude\skills\ui-ux-pro-max\data\typography.csv'
SRC_PRODUCTS = r'E:\sklls\ui-ux-pro-max-skill\.claude\skills\ui-ux-pro-max\data\products.csv'
SRC_COLORS = r'E:\sklls\ui-ux-pro-max-skill\.claude\skills\ui-ux-pro-max\data\colors.csv'
OUT_DIR = os.path.join(BASE, 'demos')
CATALOG = os.path.join(BASE, 'style-catalog.html')
OUT_PDIR = os.path.join(BASE, 'product-demos')
PCATALOG = os.path.join(BASE, 'product-catalog.html')
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- 颜色工具 ----------
def yiq(hx):
    hx = hx.lstrip('#')
    if len(hx) == 3: hx = ''.join(c*2 for c in hx)
    r, g, b = int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16)
    return (r*299 + g*587 + b*114) // 1000

def rgba(hx, a):
    hx = hx.lstrip('#')
    if len(hx) == 3: hx = ''.join(c*2 for c in hx)
    return 'rgba(%d,%d,%d,%s)' % (int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16), a)

def rotate_hue(hx, deg):
    hx = hx.lstrip('#')
    if len(hx) == 3: hx = ''.join(c*2 for c in hx)
    r, g, b = [int(hx[i:i+2],16)/255 for i in (0,2,4)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb((h + deg/360.0) % 1.0, l, s)
    return '#%02x%02x%02x' % (round(r*255), round(g*255), round(b*255))

def hue_seed(name):
    return int(hashlib.md5(name.encode('utf-8')).hexdigest()[:4], 16) % 300 + 30

def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'style'

# ---------- 官方字体配对 ----------
TYPO_ROWS = list(csv.DictReader(open(SRC_TYPO, encoding='utf-8')))

def pick_fonts(kw):
    """按风格关键词与官方配对的 Mood/Best For 词重合度选择，全来自 typography.csv。"""
    k = set(re.findall(r'[a-z]+', kw.lower()))
    best, score = TYPO_ROWS[0], 0
    for t in TYPO_ROWS:
        tw = set(re.findall(r'[a-z]+', (t.get('Mood/Style Keywords','') + ' ' + t.get('Best For','')).lower()))
        s = len(k & tw)
        if s > score:
            best, score = t, s
    heading, body = best['Heading Font'], best['Body Font']
    imp = best.get('CSS Import', '')
    m = re.search(r'family=([^\'&]+(?:&family=[^\'&]+)*)', imp)
    q = m.group(1) if m else 'family=Inter:wght@400;600;800'
    return heading, body, q

# ---------- 官方色板 ----------
# 无 hex 的风格：把官方色板文字里的颜色词映射到前端标准色（翻译，非创作）
COLOR_WORDS = {
    'electric blue':'#0080FF','blue':'#2563EB','navy':'#1E3A8A','indigo':'#4F46E5',
    'orange':'#EA580C','vermillion':'#DC2626','pink':'#EC4899','hot pink':'#EC4899',
    'magenta':'#DB2777','teal':'#0D9488','green':'#059669','emerald':'#059669',
    'purple':'#7C3AED','violet':'#8B5CF6','lavender':'#8B5CF6','gold':'#B08A3E',
    'amber':'#B45309','yellow':'#FFCE5C','red':'#DC2626','crimson':'#DC2626',
    'cyan':'#06B6D4','neon':'#22D3EE','mint':'#34D399','coral':'#F97316',
    'black':'#111111','monochrome':'#111111','white':'#F5F5F5','grey':'#64748B',
    'gray':'#64748B','beige':'#D6CDBA','brown':'#92400E','earth':'#9A6B4F',
    'pastel':'#C4B5FD','duotone':'#7C3AED','warm':'#EA580C','cool':'#3B82F6',
}

def colors_from_csv(r):
    """色板唯一来源：styles.csv Primary Colors 字段。"""
    text = r['Primary Colors']
    hexes = re.findall(r'#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?\b', text)
    if hexes:
        pr = hexes[0]
        se = hexes[1] if len(hexes) > 1 else rotate_hue(pr, 40)
        ac = hexes[2] if len(hexes) > 2 else rotate_hue(pr, 180)
        src = 'hex'
    else:
        # 颜色词按官方文本出现顺序提取
        low = (text + ' ' + r['Keywords'] + ' ' + r['Style Category']).lower()
        found = []
        for w, hx in COLOR_WORDS.items():
            if re.search(r'\b' + re.escape(w) + r'\b', low) and hx not in found:
                found.append(hx)
        found = found or ['#2563EB']
        pr = found[0]
        se = found[1] if len(found) > 1 else rotate_hue(pr, 40)
        ac = found[2] if len(found) > 2 else rotate_hue(pr, 180)
        src = 'word'
    dark_bg = bool(re.search(r'\b(dark|black|oled|night)\b', (text + ' ' + r['Keywords']).lower()))
    return pr, se, ac, dark_bg, src

# ---------- 官方 CSS 关键词解析 ----------
def parse_css_kw(r):
    """从 CSS/Technical Keywords 提取官方原文值；只解析写明的内容。"""
    kw = r['CSS/Technical Keywords']
    out = {}
    m = re.search(r'border-radius:\s*([\d.]+(?:px|rem|%))', kw)
    if m: out['radius'] = m.group(1)
    m = re.search(r'box-shadow:\s*([0-9][^;]+?)(?:;|$)', kw)
    if m: out['shadow'] = m.group(1).strip().rstrip(',')
    out['gradient'] = bool(re.search(r'gradient', kw, re.I))
    out['blur'] = bool(re.search(r'blur|backdrop', kw, re.I))
    out['clip'] = bool(re.search(r'clip-path', kw))
    out['anim'] = bool(re.search(r'animation|@keyframes', kw))
    out['blend'] = bool(re.search(r'blend-mode', kw))
    out['morph'] = bool(re.search(r'morph|fluid', kw))
    out['grid'] = bool(re.search(r'\bgrid\b|grid-based', kw))
    return out

# ---------- 皮肤组装 ----------
def base_skin():
    return {
        'family': 'modern', 'radius': '14px', 'btn_radius': '10px',
        'border': '1px solid VAR_BORDER', 'shadow': '0 6px 20px VAR_SHADOW',
        'hover_shadow': '0 12px 30px VAR_SHADOW',
        'transition': '200ms ease', 'body_extra': '', 'hero_deco': '',
        'btn_extra': '', 'title_extra': '', 'card_extra': '', 'bg_mode': 'light',
        'grid_pattern': '', 'page_extra': '', 'body_font_size': '',
    }

def C(s, bg, fg, muted, card, border, primary, secondary, accent):
    s.update(bg=bg, fg=fg, muted_fg=muted, card=card, border_c=border,
             primary=primary, secondary=secondary, accent=accent,
             on_primary='#fff' if yiq(primary) < 150 else '#111')

def apply_colors(s, r):
    """统一入口：色板只来自 CSV；底色深浅由官方 dark 词判定。"""
    pr, se, ac, dark, _src = colors_from_csv(r)
    if dark or s.get('bg_mode') == 'dark':
        s['bg_mode'] = 'dark'
        C(s, '#0D0F16', '#EEF1F7', 'rgba(238,241,247,.68)', '#161923',
          'rgba(255,255,255,.14)', pr, se, ac)
        if yiq(pr) > 160: s['on_primary'] = '#10121A'
    else:
        C(s, '#F8FAFC', '#0F172A', '#475569', '#FFFFFF',
          rgba(pr, '.28'), pr, se, ac)


# ---------- 精确风格→族映射（官方档案逐条核对，优先于关键词检测） ----------
STYLE_FAMILY_EXACT = {
    'Minimalism & Swiss Style': 'swiss', 'Swiss Modernism 2.0': 'swiss',
    'Minimalist Monochrome': 'swiss', 'Flat Design': 'swiss', 'Flat Design Mobile (Touch-First)': 'swiss',
    'Exaggerated Minimalism': 'exaggerated',
    'AI-Native UI': 'modern', 'SaaS Mobile (High-Tech Boutique)': 'modern',
    'Voice-First Multimodal': 'voice', 'Zero Interface': 'zero',
    'Motion-Driven': 'micro', 'Micro-interactions': 'micro',
    'Data-Dense Dashboard': 'data', 'Heat Map & Heatmap Style': 'data', 'Executive Dashboard': 'data',
    'Real-Time Monitoring': 'data', 'Drill-Down Analytics': 'data', 'Comparative Analysis Dashboard': 'data',
    'Predictive Analytics': 'data', 'User Behavior Analytics': 'data', 'Financial Dashboard': 'data',
    'Sales Intelligence Dashboard': 'data',
    'Bento Box Grid': 'bento',
    'E-Ink / Paper': 'paper', 'Editorial Grid / Magazine': 'paper', 'Vintage Analog / Retro Film': 'paper',
    'Academia (Scholarly Mobile)': 'paper',
    'Anti-Polish / Raw Aesthetic': 'antipolish',
    'Bold Typography (Mobile Poster)': 'kinetic',
    'Sketch Hand-Drawn (Mobile)': 'sketch',
    'Glassmorphism': 'glass', 'Liquid Glass': 'glass', 'Spatial UI (VisionOS)': 'glass',
    'Modern Dark (Cinema Mobile)': 'dark',
    'Bitcoin DeFi (Mobile)': 'defi',
    'Brutalism': 'brutal', 'Neubrutalism': 'brutal', 'Kinetic Brutalism (Mobile)': 'brutal',
    'Neo Brutalism (Mobile)': 'brutal',
    'Cyberpunk UI': 'cyber', 'HUD / Sci-Fi FUI': 'cyber', 'Retro-Futurism': 'cyber',
    'Terminal CLI (Mobile)': 'cyber', 'Cyberpunk Mobile HUD': 'cyber',
    'Accessible & Ethical': 'a11y', 'Inclusive Design': 'a11y',
    'Spectrum 2': 'spectrum', 'Adobe Spectrum': 'spectrum',
    'Claymorphism': 'clay', 'Claymorphism (Mobile)': 'clay', 'Tactile Digital / Deformable UI': 'clay',
    'Y2K Aesthetic': 'vaporwave', 'Vaporwave': 'vaporwave', 'Chromatic Aberration / RGB Split': 'vaporwave',
    'Neumorphism': 'neumorph', 'Neumorphism (Mobile)': 'neumorph',
    '3D & Hyperrealism': '3d', '3D Product Preview': '3d', 'Dimensional Layering': '3d',
    'Skeuomorphism': 'skeuo',
    'Vibrant & Block-based': 'vibrant', 'Material 3 Expressive (Mobile)': 'm3',
    'Dark Mode (OLED)': 'dark', 'Parallax Storytelling': 'parallax',
    'Aurora UI': 'aurora', 'Gradient Mesh / Aurora Evolved': 'aurora',
    'Kinetic Typography': 'kinetic',
    'Organic Biophilic': 'organic', 'Nature Distilled': 'distilled', 'Biomimetic / Organic 2.0': 'biomimetic',
    'Bauhaus (包豪斯)': 'bauhaus', 'Fluent 2': 'fluent', 'Shopify Polaris': 'polaris',
    'Soft UI Evolution': 'soft', 'Gen Z Chaos / Maximalism': 'chaos',
    'Interactive Cursor Design': 'cursor',
    'Terminal CLI (Mobile)': 'cyber',
}

def detect_family(r):
    exact = STYLE_FAMILY_EXACT.get(r['Style Category'])
    if exact:
        return exact
    kw = (r['Keywords'] + ' ' + r['CSS/Technical Keywords'] + ' ' + r['Style Category']).lower()
    checks = [
        ('neumorph', ['neumorph']),
        ('clay', ['clay']),
        ('glass', ['glass']),
        ('aurora', ['aurora', 'gradient mesh']),
        ('cyber', ['cyber', 'hud', 'sci-fi']),
        ('vaporwave', ['vaporwave', 'y2k', 'chromatic']),
        ('memphis', ['memphis']),
        ('brutal', ['brutal']),
        ('pixel', ['pixel']),
        ('paper', ['e-ink', 'paper', 'editorial', 'magazine', 'academia', 'vintage', 'analog']),
        ('dark', ['dark mode', 'cinema', 'oled']),
        ('data', ['dashboard', 'analytics', 'heatmap', 'monitor', 'financial', 'executive',
                  'funnel', 'drill', 'comparative', 'predictive', 'behavior', 'sales intelligence']),
        ('swiss', ['swiss', 'minimal', 'monochrome']),
        ('a11y', ['accessible', 'inclusive', 'ethical']),
        ('skeuo', ['skeuomorph']),
        ('chaos', ['maximal', 'chaos', 'gen z']),
        ('kinetic', ['kinetic']),
        ('distilled', ['nature distilled', 'distilled']),
        ('biomimetic', ['biomimetic', 'organic 2.0', 'cellular']),
        ('organic', ['organic', 'biophilic', 'nature']),
        ('3d', ['3d', 'hyperreal', 'dimensional']),
        ('vibrant', ['block-based', 'duotone', 'vibrant']),
        ('micro', ['micro-interaction', 'motion-driven', 'motion design']),
        ('soft', ['soft ui']),
        ('bauhaus', ['bauhaus']),
        ('m3', ['material 3', 'material design']),
        ('fluent', ['fluent']),
        ('polaris', ['polaris']),
        ('spectrum', ['spectrum']),
        ('zero', ['zero interface', 'minimal chrome']),
        ('voice', ['voice', 'multimodal']),
        ('antipolish', ['anti-polish', 'raw aesthetic']),
        ('parallax', ['parallax']),
        ('cursor', ['cursor']),
    ]
    for fam, words in checks:
        if any(w in kw for w in words):
            return fam
    return 'modern'

# 族翻译层：把官方效果关键词译为 CSS（仅当官方档案提到对应特征）
def skin_family(s, fam, r, parsed):
    kw = (r['Keywords'] + ' ' + r['CSS/Technical Keywords']).lower()
    if fam == 'neumorph':
        s.update(border='none', radius=parsed.get('radius', '18px'), btn_radius='14px',
                 shadow='-7px -7px 14px rgba(255,255,255,.9), 7px 7px 14px rgba(0,0,0,.14)',
                 hover_shadow='inset -4px -4px 10px rgba(255,255,255,.9), inset 4px 4px 10px rgba(0,0,0,.12)')
        s['bg'] = '#ECEAF2'; s['card'] = '#ECEAF2'; s['border_c'] = 'transparent'
    elif fam == 'clay':
        s.update(radius=parsed.get('radius', '26px'), btn_radius='16px',
                 border='2px solid rgba(255,255,255,.65)',
                 shadow='inset 0 -6px 12px rgba(0,0,0,.07), inset 0 6px 12px rgba(255,255,255,.75), 0 14px 28px rgba(0,0,0,.16)')
    elif fam == 'glass':
        s.update(card_extra='backdrop-filter: blur(18px) saturate(1.3); background: rgba(255,255,255,.06);',
                 radius=parsed.get('radius', '18px'))
        s['body_extra'] = ('background-image: radial-gradient(600px 400px at 85% -10%, {p}, transparent 65%),'
                           ' radial-gradient(520px 380px at -10% 30%, {s}, transparent 65%);'
                           ' background-attachment: fixed;').format(p=rgba(s['primary'], .25),
                                                                    s=rgba(s['secondary'], .2))
    elif fam == 'aurora' and parsed['gradient']:
        s.update(title_extra='background: linear-gradient(100deg, var(--primary), var(--secondary) 50%, var(--accent)); -webkit-background-clip: text; background-clip: text; color: transparent;',
                 btn_extra='background: linear-gradient(120deg, var(--primary), var(--secondary) 50%, var(--accent)); background-size: 200% 200%; animation: gradflow 10s ease infinite;')
        s['body_extra'] = ('background-image: radial-gradient(56vw 56vw at 8%% -12%%, %(p)s, transparent 62%%),'
                           ' radial-gradient(50vw 50vw at 96%% -4%%, %(s)s, transparent 62%%);'
                           ' background-attachment: fixed;') % {'p': rgba(s.get('primary','#7C3AED'), .28),
                                                                 's': rgba(s.get('secondary','#06B6D4'), .22)}
    elif fam == 'cyber':
        s.update(radius=parsed.get('radius', '4px'), btn_radius='2px',
                 title_extra='text-shadow: 0 0 18px ' + rgba(s.get('primary','#22D3EE'), '.6') + ';',
                 btn_extra='text-transform: uppercase; letter-spacing: .12em; box-shadow: 0 0 18px ' + rgba(s.get('primary','#22D3EE'), '.4') + ';')
        if 'scan' in kw or 'repeating' in kw:
            s['body_extra'] = 'background-image: repeating-linear-gradient(0deg, ' + rgba(s.get('primary','#22D3EE'), '.04') + ' 0 1px, transparent 1px 3px);'
    elif fam == 'vaporwave':
        s.update(btn_radius='999px',
                 title_extra='background: linear-gradient(100deg, var(--primary), var(--secondary) 45%, var(--accent)); -webkit-background-clip: text; background-clip: text; color: transparent;')
    elif fam == 'memphis':
        s.update(border='3px solid var(--fg)', btn_radius='999px',
                 shadow='8px 8px 0 var(--accent)', hover_shadow='11px 11px 0 var(--secondary)',
                 transition='180ms ease')
        s['body_extra'] = 'background-image: radial-gradient(' + rgba(s.get('fg','#16161D'), '.1') + ' 1.5px, transparent 1.5px); background-size: 22px 22px;'
        s['hero_deco'] = ('<span style="position:absolute;top:-16px;left:46%;width:0;height:0;border-left:30px solid transparent;'
                          'border-right:30px solid transparent;border-bottom:52px solid var(--accent);transform:rotate(14deg)" aria-hidden="true"></span>')
    elif fam == 'brutal':
        s.update(radius=parsed.get('radius', '0px'), btn_radius='0px',
                 border='3px solid var(--fg)',
                 shadow='6px 6px 0 var(--fg)', hover_shadow='9px 9px 0 var(--fg)', transition='0ms')
    elif fam == 'pixel':
        s.update(radius='0px', btn_radius='0px', border='3px solid var(--fg)',
                 shadow='5px 5px 0 var(--fg)', hover_shadow='8px 8px 0 var(--fg)')
    elif fam == 'paper':
        s.update(radius='6px', btn_radius='4px', shadow='none',
                 hover_shadow='0 8px 18px rgba(60,50,30,.12)', transition='220ms ease')
        s.update(bg='#FAF7F0', card='#FFFDF8', muted_fg='#6B6355', border_c='#D8D2C4')
    elif fam == 'swiss':
        s.update(radius='4px', btn_radius='2px', shadow='none',
                 hover_shadow='0 8px 20px rgba(0,0,0,.09)')
        if parsed['grid']:
            s['grid_pattern'] = ('background-image: linear-gradient(' + rgba('#141414', '.045') + ' 1px, transparent 1px),'
                                 ' linear-gradient(90deg, ' + rgba('#141414', '.045') + ' 1px, transparent 1px); background-size: 72px 72px;')
    elif fam == 'data':
        s.update(radius=parsed.get('radius', '10px'), btn_radius='8px', transition='180ms ease')
    elif fam == 'a11y':
        s.update(radius='6px', btn_radius='6px', border='2.5px solid var(--fg)',
                 shadow='none', hover_shadow='none', transition='120ms ease',
                 body_font_size='font-size: 17.5px;',
                 page_extra='a:focus-visible, button:focus-visible { outline: 5px solid #B500FF; outline-offset: 4px; } .card h3 { font-size: 21px; } nav a { text-decoration: underline; }')
    elif fam == 'skeuo':
        s.update(radius='12px', btn_radius='10px',
                 shadow='inset 0 1px 0 rgba(255,255,255,.5), inset 0 -2px 4px rgba(90,60,20,.25), 0 10px 22px rgba(90,60,20,.35)',
                 hover_shadow='inset 0 1px 0 rgba(255,255,255,.5), inset 0 -1px 2px rgba(90,60,20,.2), 0 14px 30px rgba(90,60,20,.45)',
                 card_extra='background: linear-gradient(180deg, rgba(255,255,255,.5), rgba(0,0,0,.06));')
    elif fam == 'chaos':
        s.update(border='2.5px dashed var(--fg)', shadow='6px 8px 0 var(--accent)',
                 hover_shadow='10px 12px 0 var(--secondary)', transition='160ms ease',
                 page_extra='.card:nth-child(1){transform:rotate(-1.6deg)}.card:nth-child(2){transform:rotate(1.2deg);border-style:solid}.card:nth-child(3){transform:rotate(-.8deg)} .card:hover{transform:rotate(0) translateY(-6px)} h1{transform:rotate(-1deg)}')
    elif fam == 'kinetic':
        s.update(title_extra='font-size: clamp(44px, 8vw, 96px)!important; line-height: 1!important; text-transform: uppercase;',
                 page_extra='.hl { -webkit-text-stroke: 2.5px var(--fg); color: transparent; animation: fill 6s ease infinite; } @keyframes fill { 0%,100%{color:transparent} 45%,60%{color:var(--primary)} }')
    elif fam == 'exaggerated':
        # 官方：oversized typography（clamp 3rem-12rem）、font-weight 900、极端留白
        s.update(radius='2px', btn_radius='2px', border='none', shadow='none', hover_shadow='none',
                 title_extra='font-size: clamp(44px, 11vw, 130px)!important; line-height: .96!important; font-weight: 900!important; letter-spacing: -.03em!important;',
                 page_extra='.hero { padding: 16vh 0 12vh; } .sub { font-size: 15px; max-width: 380px; margin-left: 0; margin-right: auto; text-align: left; } .cta-row { justify-content: flex-start; } .hero { text-align: left; } .doc-meta { justify-content: flex-start; }')
    elif fam == 'sketch':
        # 官方：wobbly borderRadius 每角不同、手绘虚线边框
        s.update(radius='15px 25px 20px 10px', btn_radius='14px 22px 16px 10px',
                 border='2px dashed var(--fg)',
                 shadow='3px 4px 0 ' + rgba(s.get('primary', '#4A5568'), '.18'),
                 hover_shadow='5px 6px 0 ' + rgba(s.get('primary', '#4A5568'), '.26'),
                 card_extra='border-radius: 18px 26px 22px 12px;')
    elif fam == 'defi':
        # 官方：deep void + dark matter 表面 + Bitcoin 橙/金渐变
        s['bg_mode'] = 'dark'
        s.update(radius='14px', btn_radius='10px',
                 body_extra='background-image: radial-gradient(52vw 40vw at 88% -8%, rgba(247,147,26,.2), transparent 62%), radial-gradient(40vw 34vw at -6% 34%, rgba(247,147,26,.1), transparent 60%); background-attachment: fixed;',
                 title_extra='background: linear-gradient(96deg, #F7931A, #FFD84D 55%, #F7931A); -webkit-background-clip: text; background-clip: text; color: transparent;',
                 btn_extra='background: linear-gradient(120deg, #F7931A, #FFB347); color: #131007; font-weight: 700;')
    elif fam == 'distilled':
        # 官方：muted earthy / grain 纹理 / handmade warmth / ease-out；无 blob 无绿色
        s.update(radius='18px 24px 20px 26px', btn_radius='14px',
                 transition='ease-out 240ms',
                 shadow='0 14px 34px rgba(160,110,70,.16)', hover_shadow='0 20px 44px rgba(160,110,70,.24)',
                 body_extra="background-image: url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/><feColorMatrix type='saturate' values='0'/><feComponentTransfer><feFuncA type='linear' slope='0.055'/></feComponentTransfer></filter><rect width='140' height='140' filter='url(%23n)'/></svg>\");",
                 page_extra='.card { background: linear-gradient(180deg, rgba(255,255,255,.35), rgba(255,255,255,0)) , var(--card); }')
    elif fam == 'biomimetic':
        # 官方：呼吸动画 / 细胞 clip-path / 生成感；荧光生物色
        s['bg_mode'] = 'dark'
        s.update(radius='22px', btn_radius='999px',
                 hero_deco=('<span style="position:absolute;top:-26px;right:8%;width:130px;height:130px;'
                            'background:rgba(0,255,65,.14);border-radius:44% 56% 58% 42%/52% 46% 54% 48%" aria-hidden="true"></span>'
                            '<span style="position:absolute;bottom:-18px;left:4%;width:90px;height:90px;'
                            'background:rgba(255,153,153,.16);clip-path:polygon(18% 4%,60% 0%,96% 30%,88% 74%,52% 98%,12% 82%,0% 40%)" aria-hidden="true"></span>'),
                 page_extra=('@keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }\n'
                             '.card-icon { animation: breathe 5.5s ease-in-out infinite; }\n'
                             '.hero > div[style] > span { animation: breathe 7s ease-in-out infinite; }'))
    elif fam == 'organic':
        # 官方：圆角 16-24 varied、SVG blob、自然柔影（苔绿系）
        s.update(radius='20px 26px 18px 28px', btn_radius='999px',
                 card_extra='border-radius: 22px 30px 20px 32px;',
                 hero_deco='<span style="position:absolute;top:-30px;left:6%;width:150px;height:150px;' + rgba(s.get('primary','#3E7C4F'), '.22') + ';border-radius:58% 42% 55% 45%/49% 56% 44% 51%" aria-hidden="true"></span>')
    elif fam == '3d':
        s.update(radius='16px', btn_radius='12px',
                 shadow='0 2px 0 rgba(20,22,40,.1), 0 10px 0 rgba(20,22,40,.18), 0 22px 30px rgba(20,22,40,.25)',
                 hover_shadow='0 2px 0 rgba(20,22,40,.1), 0 14px 0 rgba(20,22,40,.2), 0 30px 40px rgba(20,22,40,.3)')
    elif fam == 'vibrant':
        s.update(radius='8px', btn_radius='6px', border='none',
                 shadow='0 10px 24px rgba(0,0,0,.22)', hover_shadow='0 16px 34px rgba(0,0,0,.3)',
                 btn_extra='text-transform: uppercase; font-weight: 800;')
    elif fam == 'micro':
        s.update(btn_radius='999px',
                 page_extra='@keyframes pop { 0%{transform:scale(1)} 40%{transform:scale(1.18)} 100%{transform:scale(1)} } .card:hover .card-icon { animation: pop .45s ease; }')
    elif fam == 'soft':
        s.update(radius='24px', btn_radius='18px', border='none',
                 shadow='0 18px 40px rgba(0,0,0,.14)', hover_shadow='0 26px 52px rgba(0,0,0,.2)')
    elif fam == 'bauhaus':
        s.update(radius='0px', btn_radius='0px', border='2.5px solid var(--fg)',
                 shadow='7px 7px 0 var(--fg)', hover_shadow='10px 10px 0 var(--fg)', transition='0ms',
                 page_extra='.grid3 .card:nth-child(1) .card-icon{border-radius:50%} .grid3 .card:nth-child(3) .card-icon{clip-path:polygon(50% 0,100% 100%,0 100%);border-radius:0}',
                 hero_deco='<span style="position:absolute;top:-24px;right:12%;width:64px;height:64px;border-radius:50%;background:var(--primary);border:2.5px solid var(--fg)" aria-hidden="true"></span><span style="position:absolute;bottom:-14px;left:4%;width:0;height:0;border-left:34px solid transparent;border-right:34px solid transparent;border-bottom:58px solid var(--accent);transform:rotate(-10deg)" aria-hidden="true"></span>')
    elif fam == 'm3':
        s.update(radius='28px', btn_radius='999px', border='none',
                 card_extra='background: ' + rgba('#6750A4', '.13') + ';')
    elif fam == 'fluent':
        s.update(radius='8px', btn_radius='6px',
                 shadow='0 8px 16px rgba(0,0,0,.14), 0 0 1px rgba(0,0,0,.2)',
                 hover_shadow='0 14px 28px rgba(0,0,0,.2)')
    elif fam == 'polaris':
        s.update(radius='12px', btn_radius='10px',
                 shadow='0 4px 12px rgba(0,0,0,.08)', hover_shadow='0 10px 24px rgba(0,0,0,.14)')
    elif fam == 'spectrum':
        s.update(radius='4px', btn_radius='4px',
                 shadow='0 1px 4px rgba(0,0,0,.12)', hover_shadow='0 6px 16px rgba(0,0,0,.18)')
    elif fam == 'zero':
        s.update(border='none', shadow='none', hover_shadow='none',
                 page_extra='.hero { padding: 22vh 0 40px; } .card { border: none; box-shadow: none; background: transparent; } .card-icon { background: ' + rgba('#111111', '.08') + '; color: var(--fg); } .tag { background: transparent; border: none; color: var(--muted); }')
    elif fam == 'voice':
        s.update(btn_radius='999px',
                 page_extra='.card-icon { border-radius: 50%; animation: listen 1.8s ease-in-out infinite; } @keyframes listen { 0%,100%{box-shadow:0 0 0 0 ' + rgba('#3B7CB8', '.35') + '} 50%{box-shadow:0 0 0 14px ' + rgba('#3B7CB8', '0') + '} } .wave{display:inline-flex;gap:4px;align-items:center;height:26px;margin-left:10px}.wave i{width:4px;border-radius:3px;background:var(--primary);animation:wavebar 1.2s ease-in-out infinite}.wave i:nth-child(1){height:30%}.wave i:nth-child(2){height:75%;animation-delay:.15s}.wave i:nth-child(3){height:100%;animation-delay:.3s}.wave i:nth-child(4){height:60%;animation-delay:.45s}.wave i:nth-child(5){height:35%;animation-delay:.6s}@keyframes wavebar{0%,100%{transform:scaleY(.4)}50%{transform:scaleY(1)}}')
    elif fam == 'antipolish':
        s.update(radius='0px', btn_radius='0px', border='none', shadow='none',
                 hover_shadow='none', transition='0ms',
                 page_extra='body{font-family:Georgia,"Times New Roman",serif;max-width:760px;margin:0 auto;padding:24px}.topbar{position:static;background:transparent;border-bottom:2px solid #000}.logo-mark{border-radius:0;background:#000}nav a{color:#0000EE;text-decoration:underline}.card{border-top:1px solid #999;border-radius:0;box-shadow:none;padding:16px 0}.card-icon{display:none}.btn{border:2px outset #CCC;background:#E8E8E8;color:#000;border-radius:0}.btn-primary{background:#CCC}')
    elif fam == 'parallax':
        s.update(shadow='0 14px 34px rgba(30,41,59,.18)', hover_shadow='0 22px 48px rgba(30,41,59,.3)',
                 body_extra='background-attachment: fixed; background-image: radial-gradient(40vw 40vw at 15% 12%, ' + rgba(s.get('primary','#0EA5E9'), '.18') + ', transparent 60%), radial-gradient(36vw 36vw at 85% 30%, ' + rgba(s.get('secondary','#F472B6'), '.15') + ', transparent 60%);',
                 page_extra='.hero{animation:floaty 9s ease-in-out infinite}@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}.grid3 .card:nth-child(1){transform:translateY(18px)}.grid3 .card:nth-child(3){transform:translateY(34px)}')
    elif fam == 'cursor':
        s.update(page_extra='.cursor-dot{position:fixed;width:14px;height:14px;border-radius:50%;background:var(--accent);pointer-events:none;z-index:99;transform:translate(-50%,-50%);transition:width .18s ease,height .18s ease;mix-blend-mode:difference}body:hover .cursor-dot{width:34px;height:34px;background:var(--primary)}@media(pointer:coarse){.cursor-dot{display:none}}')

def make_skin(r):
    s = base_skin()
    parsed = parse_css_kw(r)
    fam = detect_family(r)
    s['family'] = fam
    # 1) 色板先行（一律官方 CSV），供族翻译引用
    apply_colors(s, r)
    # 2) 族形状/效果翻译（引用已就位的色板）
    skin_family(s, fam, r, parsed)
    # 3) 官方原文 CSS 值最高优先（覆盖族默认）
    if 'radius' in parsed: s['radius'] = parsed['radius']
    if 'shadow' in parsed:
        s['shadow'] = parsed['shadow']
        s['hover_shadow'] = parsed['shadow']
    # 4) 同为无 hex 的默认族风格做色相去重（避免撞色，色值仍由官方色词推导）
    if fam in ('modern', 'data') and colors_from_csv(r)[4] == 'word':
        d = hue_seed(r['Style Category'])
        s['primary'] = rotate_hue(s['primary'], d % 40)
        s['secondary'] = rotate_hue(s['secondary'], d % 40)
    # 5) 底/字自洽校验：浅底必须深字，深底必须浅字（对比度兜底，
    #    修复官方色板文字含 black/dark 词被误判深底、族翻译又改回浅底的组合）
    if s['fg'].startswith('#') and s['bg'].startswith('#'):
        bg_l, fg_l = yiq(s['bg']), yiq(s['fg'])
        if bg_l > 180 and fg_l > 150:
            s['fg'] = s['primary'] if s['primary'].startswith('#') and yiq(s['primary']) < 120 else '#111827'
            s['muted_fg'] = '#5B6472'
        elif bg_l < 90 and fg_l < 110:
            s['fg'] = '#F3F4F6'
            s['muted_fg'] = 'rgba(243,244,246,.68)'
    return s

# ---------- 官方提示词 ----------
def official_prompt(r):
    """目录页提示词：全部为 styles.csv 官方字段原文，零改写。"""
    zh_note = '（以下数据全部来自 ui-ux-pro-max 官方风格库 styles.csv 原文）'
    lines = [
        '请用「%s」风格，设计实现：〔在这里写下你的页面 / 组件需求〕。%s' % (r['Style Category'], zh_note),
        '',
        '▍官方 AI Prompt Keywords（可直接使用的官方提示词）：',
        r['AI Prompt Keywords'].strip(),
        '',
        '▍官方风格档案：',
        '- Keywords: %s' % r['Keywords'].strip(),
        '- Primary Colors: %s' % r['Primary Colors'].strip(),
        '- Effects & Animation: %s' % r['Effects & Animation'].strip(),
        '- Best For: %s' % r['Best For'].strip(),
        '- Do Not Use For: %s %s' % (r['Do Not Use For'].strip() or '（官方未标注）', ''),
        '- CSS/Technical Keywords: %s' % r['CSS/Technical Keywords'].strip(),
        '- Design System Variables: %s' % r['Design System Variables'].strip(),
        '- Light Mode: %s / Dark Mode: %s / Performance: %s' % (
            r['Light Mode ✓'].strip(), r['Dark Mode ✓'].strip(), r['Performance'].strip()),
        '',
        '▍官方 Implementation Checklist（交付前逐项检查）：',
        r['Implementation Checklist'].strip(),
        '',
        '▍SKILL.md 官方 Pre-Delivery Checklist：',
        '- No emojis as icons (use SVG: Heroicons/Lucide)',
        '- cursor-pointer on all clickable elements',
        '- Hover states with smooth transitions (150-300ms)',
        '- Light mode: text contrast 4.5:1 minimum',
        '- Focus states visible for keyboard nav',
        '- prefers-reduced-motion respected',
        '- Responsive: 375px, 768px, 1024px, 1440px',
    ]
    return '\n'.join(lines)

# ---------- 风格版提示词（只提供风格与 token，主题由用户自定） ----------
def theme_prompt(r, s, t=None):
    return '\n'.join([
        '请以「%s」风格，设计实现：〔在这里写下你的页面需求与主题，主题由你确定〕' % r['Style Category'],
        '',
        '▍本页设计 token（实际使用值，直接可用）：',
        '- 主色 %s / 辅色 %s / 强调 %s' % (s['primary'], s['secondary'], s['accent']),
        '- 底 %s / 正文 %s / 弱文 %s / 卡面 %s' % (s['bg'], s['fg'], s['muted_fg'], s['card']),
        '- 圆角 %s / 按钮圆角 %s' % (s['radius'], s['btn_radius']),
        '',
        '▍官方风格数据（ui-ux-pro-max styles.csv 原文，零改写）：',
        '- AI Prompt Keywords: %s' % r['AI Prompt Keywords'].strip(),
        '- Primary Colors: %s' % r['Primary Colors'].strip(),
        '- Effects & Animation: %s' % r['Effects & Animation'].strip(),
        '- CSS/Technical Keywords: %s' % r['CSS/Technical Keywords'].strip(),
        '- Implementation Checklist: %s' % r['Implementation Checklist'].strip(),
        '',
        '▍动效（只此一次，别加第二处）：',
        '- %s' % FAMILY_MOTION.get(s['family'], '一次入场动效'),
        '',
        '▍必须避开（AI 指纹清单，frontend-design 原则）：',
        '- ALL-CAPS 装饰性眉标（信息行必须有语义：批次号/期号/坐标/档期）',
        '- 按钮尾部箭头 →；中点分隔的 meta 串；逐卡片 fade-in 上升',
        '- 无语义的 01/02/03 编号（内容是真实序列才可用编号）',
        '- 默认 Inter/Roboto 字体；emoji 充当图标（一律内联 SVG）；米白+赤陶 #D97757 默认配色',
        '',
        '▍验收：正文对比度 ≥4.5:1；:focus-visible 焦点环；prefers-reduced-motion 降级；响应式 375/768/1440 无横向滚动',
    ])

PROMPT_ZONE_CSS = '''
.prompt-zone { margin-top: 46px; }
.prompt-zone summary {
  cursor: pointer; list-style: none; width: fit-content;
  font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 600;
  border: 2px dashed var(--border); padding: 8px 18px; border-radius: 8px;
  background: var(--card); color: var(--fg);
}
.prompt-zone summary:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.copy-btn {
  font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 600;
  background: var(--primary); color: var(--on-primary);
  border: none; border-radius: 8px;
  padding: 10px 22px; cursor: pointer; margin: 14px 10px 0 0;
  display: inline-flex; align-items: center; text-decoration: none;
  transition: transform 120ms ease, opacity 120ms ease;
}
.copy-btn:hover { opacity: .88; transform: translateY(-1px); }
.copy-btn:active { transform: translateY(1px); }
.copy-btn:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.prompt {
  font-family: 'IBM Plex Mono', 'Courier New', monospace;
  font-size: 12.5px; line-height: 1.7; white-space: pre-wrap; word-break: break-word;
  background: var(--card); border: 1.5px solid var(--border); border-radius: 10px;
  color: var(--fg);
  padding: 18px 20px; margin-top: 14px; max-height: 320px; overflow-y: auto;
}
'''

COPY_JS = '''<script>
(function() {
  var btns = document.querySelectorAll('.copy-btn[data-target]');
  for (var i = 0; i < btns.length; i++) {
    (function(btn) {
      btn.addEventListener('click', function() {
        var pre = document.getElementById(btn.getAttribute('data-target'));
        if (!pre) return;
        var text = pre.textContent;
        var done = function() { btn.textContent = '已复制'; setTimeout(function() { btn.textContent = '复制提示词'; }, 1600); };
        var fallback = function() {
          var ta = document.createElement('textarea');
          ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta); ta.select();
          try { document.execCommand('copy'); done(); } catch (e) { btn.textContent = '请手动复制'; }
          document.body.removeChild(ta);
        };
        if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(done, fallback); } else fallback();
      });
    })(btns[i]);
  }
})();
</script>'''

def prompt_zone(prompt, pid='pp'):
    return '''<section class="prompt-zone">
  <details>
    <summary>看提示词 / 复刻这个风格</summary>
    <pre class="prompt" id="%s">%s</pre>
    <button class="copy-btn" type="button" data-target="%s">复制提示词</button>
    <a class="copy-btn" href="../style-catalog.html">回风格目录</a>
  </details>
</section>''' % (pid, html.escape(prompt), pid)

# ---------- 布局模板（演示容器；风格数据不含页面布局） ----------
def base_css(s, font_head, font_body, fonts_q, title, css):
    shadow = s['shadow'].replace('VAR_SHADOW', rgba(s['primary'], '.13'))
    hshadow = s['hover_shadow'].replace('VAR_SHADOW', rgba(s['primary'], '.2'))
    border = s['border'].replace('VAR_BORDER', s['border_c'])
    css = css.replace('__BORDER__', border).replace('__SHADOW__', shadow) \
             .replace('__HSHADOW__', hshadow).replace('__CARD_EXTRA__', s['card_extra'])
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<title>__TITLE__</title>
<meta name="description" content="UI 设计提示词库 / 风格样张与官方提示词，复制后交给 AI 复刻同款网页。">
<style>
@import url('https://fonts.googleapis.com/css2?__FONTS__&display=swap');
:root {
  --bg: __BG__; --fg: __FG__; --muted: __MUTED__; --card: __CARD__;
  --border: __BORDERC__; --primary: __PRIMARY__; --secondary: __SECONDARY__;
  --accent: __ACCENT__; --on-primary: __ONPRIMARY__;
  --radius: __RADIUS__; --btn-radius: __BTNADIUS__;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: '__FB__', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg); color: var(--fg); line-height: 1.6;
  __BODYFONTSIZE____BODY_EXTRA__
}
h1, h2, h3, .num { font-family: '__FH__', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
.container { max-width: 1080px; margin: 0 auto; padding: 0 24px; }
.topbar { position: sticky; top: 0; z-index: 10; background: var(--card); border-bottom: __BORDER__; }
.topbar-inner { display: flex; align-items: center; justify-content: space-between; height: 62px; }
.logo { font-weight: 800; font-size: 17px; display: flex; align-items: center; gap: 10px;
  text-decoration: none; color: var(--fg); font-family: '__FH__', sans-serif; }
.logo-mark { width: 32px; height: 32px; border-radius: calc(var(--radius) * .6);
  background: var(--primary); color: var(--on-primary); display: grid; place-items: center; }
nav { display: flex; gap: 22px; }
nav a { color: var(--muted); text-decoration: none; font-size: 14.5px; }
nav a:hover, nav a:focus-visible { color: var(--primary); }
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  font: inherit; font-weight: 600; font-size: 14.5px;
  padding: 11px 22px; border-radius: var(--btn-radius);
  cursor: pointer; text-decoration: none; border: __BORDER__;
  background: var(--card); color: var(--fg);
  transition: transform __TRANS__, box-shadow __TRANS__, background __TRANS__;
}
.btn-primary { background: var(--primary); color: var(--on-primary); border-color: var(--primary); }
.btn-primary:hover { transform: translateY(-2px); __BTNEXTRA__ }
a:focus-visible, button:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.card { background: var(--card); border: __BORDER__; border-radius: var(--radius);
  box-shadow: __SHADOW__; padding: 24px;
  transition: transform __TRANS__, box-shadow __TRANS__; }
.card:hover { transform: translateY(-4px); box-shadow: __HSHADOW__; __CARD_EXTRA__ }
.card-icon { width: 42px; height: 42px; border-radius: calc(var(--radius) * .7);
  background: var(--primary); color: var(--on-primary);
  display: grid; place-items: center; margin-bottom: 14px; }
.card h3 { font-size: 16.5px; margin-bottom: 6px; }
.card p { font-size: 13.5px; color: var(--muted); }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat b { display: block; font-size: 34px; font-weight: 800; color: var(--primary); }
.stat span { font-size: 13px; color: var(--muted); }
footer { border-top: __BORDER__; padding: 26px 0; text-align: center; font-size: 13px; color: var(--muted); }
footer a { color: var(--primary); }
@keyframes gradflow { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
__PAGEEXTRA__
__PAGE_CSS__
</style>
</head>
<body>
__BODY__
</body>
</html>'''.replace('__TITLE__', title) \
   .replace('__FONTS__', fonts_q) \
   .replace('__BG__', s['bg']).replace('__FG__', s['fg']) \
   .replace('__MUTED__', s['muted_fg']).replace('__CARD__', s['card']) \
   .replace('__BORDERC__', s['border_c']) \
   .replace('__PRIMARY__', s['primary']).replace('__SECONDARY__', s['secondary']) \
   .replace('__ACCENT__', s['accent']).replace('__ONPRIMARY__', s['on_primary']) \
   .replace('__RADIUS__', s['radius']).replace('__BTNADIUS__', s['btn_radius']) \
   .replace('__FH__', font_head).replace('__FB__', font_body) \
   .replace('__BODYFONTSIZE__', s['body_font_size']) \
   .replace('__BODY_EXTRA__', s['body_extra']).replace('__BORDER__', border) \
   .replace('__SHADOW__', shadow).replace('__HSHADOW__', hshadow) \
   .replace('__TRANS__', s['transition']).replace('__CARD_EXTRA__', s['card_extra']) \
   .replace('__BTNEXTRA__', s['btn_extra']).replace('__PAGEEXTRA__', s['page_extra']) \
   .replace('__PROMPTCSS__', PROMPT_ZONE_CSS) \
   .replace('__PAGE_CSS__', css)

NAV = '<nav aria-label="主导航"><a href="#features">功能</a><a href="#stats">成效</a><a href="../style-catalog.html">风格目录</a></nav>'
ICON_SEARCH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
ICON_CHAT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
ICON_CHART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>'
BOLT = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m13 2-2 9h6l-9 11 2-9H4Z"/></svg>'

def landing_body(s, t, prompt):
    deco = ('<div style="position:relative">' + s['hero_deco']) if s['hero_deco'] else '<div>'
    cursor_dot = '<span class="cursor-dot" aria-hidden="true"></span>' if s['family'] == 'cursor' else ''
    wave = '<span class="wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>' if s['family'] == 'voice' else ''
    blocks = ''.join('<article class="card"><div class="card-icon">%s</div><h3>%s</h3><p>%s</p></article>' % (ic, b[0], b[1])
                     for ic, b in zip((ICON_SEARCH, ICON_CHAT, ICON_CHART), t['blocks']))
    stats = ''.join('<div class="card stat"><b>%s</b><span>%s</span></div>' % (v, k) for v, k in t['stats'])
    return '''__CURSOR__<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__BRAND__</a>
  __NAV__
  <a class="btn btn-primary" href="#">__CTA1__</a>
</div></header>
<main>
  <section class="hero container">__DECO__
    <p class="doc-meta">__META__</p>
    <h1>__HERO__</h1>__WAVE__
    <p class="sub">__SUB__</p>
    <div class="cta-row"><a class="btn btn-primary" href="#">__CTA1__</a><a class="btn" href="#">__CTA2__</a></div>
  </div></section>
  <section id="features" class="container">
    <h2 class="section-title">__EN__</h2>
    <div class="grid3">__BLOCKS__</div>
  </section>
  <section id="stats" class="container">
    <div class="grid3 stats-row">__STATS__</div>
  </section>
</main>
<footer>__FOOT__ / <a href="../style-catalog.html">返回风格目录</a></footer>
__PROMPTZONE__''' \
    .replace('__CURSOR__', cursor_dot).replace('__WAVE__', wave) \
    .replace('__NAV__', NAV).replace('__DECO__', deco) \
    .replace('__BRAND__', html.escape(t['brand'])) \
    .replace('__META__', html.escape(t['meta'])) \
    .replace('__HERO__', html.escape(t['hero'])) \
    .replace('__SUB__', html.escape(t['sub'])) \
    .replace('__CTA1__', html.escape(t['cta1'])).replace('__CTA2__', html.escape(t['cta2'])) \
    .replace('__EN__', html.escape(t.get('en', ''))) \
    .replace('__BLOCKS__', blocks).replace('__STATS__', stats) \
    .replace('__FOOT__', html.escape(t['foot'])) \
    .replace('__PROMPTZONE__', '')

def landing_css(s):
    return '''.hero { padding: 72px 0 48px; text-align: center; position: relative; }
.doc-meta {
  font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: var(--muted);
  letter-spacing: .04em; margin-bottom: 20px;
  display: inline-flex; gap: 14px; flex-wrap: wrap; justify-content: center;
}
h1 { font-size: clamp(32px, 5vw, 54px); font-weight: 800; line-height: 1.16; margin-bottom: 18px; __TITLE_EXTRA__ }
.hl { color: var(--primary); }
.sub { font-size: 17px; color: var(--muted); max-width: 560px; margin: 0 auto 34px; }
.cta-row { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
.section-title { text-align: center; font-size: 20px; font-weight: 700; margin: 50px 0 30px; letter-spacing: .14em; color: var(--muted); }
.stats-row { margin: 24px 0 72px; }
.stat { text-align: center; }
@media (max-width: 768px) { nav { display: none; } .grid3 { grid-template-columns: 1fr; } }'''

def dashboard_body(s, t, prompt):
    bars1 = ''.join('<i style="height:%d%%%s"></i>' % (h, ' class="hot"' if h > 70 else '')
                    for h in (30, 44, 38, 58, 50, 76, 64))
    bars2 = ''.join('<i style="height:%d%%%s"></i>' % (h, ' class="hot"' if h > 70 else '')
                    for h in (42, 36, 55, 48, 80, 60, 52))
    kpis = ''.join('<div class="card kpi"><span>%s</span><b class="num">%s</b></div>' % (k, v) for v, k in t['stats'])
    kpis += '<div class="card kpi"><span>栏目</span><b class="num" style="font-size:20px;padding-top:8px">%s</b></div>' % html.escape(t.get('en', ''))[:22]
    rows = ''.join('<tr><td><b>%s</b><small>%s</small></td><td>%s</td><td class="num">%s</td><td><span class="pill %s">%s</span></td></tr>' % (
        html.escape(b[0]), html.escape(t['meta'])[:26], html.escape(b[1])[:24], v,
        cls, label) for b, (v, _), cls, label in zip(t['blocks'], t['stats'],
        ('win', 'new', 'risk'), ('在册', '本期', '待核')))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__BRAND__</a>
  __NAV__
  <a class="btn btn-primary" href="#">__CTA1__</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:22px 0 4px">__META__</p>
  <section class="kpis">__KPIS__</section>
  <section class="charts">
    <div class="card chart-card"><h3>__T1__</h3><div class="bars">__BARS1__</div></div>
    <div class="card chart-card"><h3>__T2__</h3><div class="bars alt">__BARS2__</div></div>
  </section>
  <section class="card table-card">
    <h3>__EN__ / 记录</h3>
    <div class="tbl-wrap"><table>
      <thead><tr><th>条目</th><th>说明</th><th>数值</th><th>状态</th></tr></thead>
      <tbody>__ROWS__</tbody>
    </table></div>
  </section>
</main>
<footer>__FOOT__ / <a href="../style-catalog.html">返回风格目录</a></footer>
__PROMPTZONE__''' \
    .replace('__NAV__', NAV) \
    .replace('__BRAND__', html.escape(t['brand'])) \
    .replace('__CTA1__', html.escape(t['cta1'])) \
    .replace('__META__', html.escape(t['meta'])) \
    .replace('__KPIS__', kpis) \
    .replace('__T1__', html.escape(t['blocks'][0][0])) \
    .replace('__T2__', html.escape(t['blocks'][1][0])) \
    .replace('__EN__', html.escape(t.get('en', ''))) \
    .replace('__BARS1__', bars1).replace('__BARS2__', bars2).replace('__ROWS__', rows) \
    .replace('__FOOT__', html.escape(t['foot'])) \
    .replace('__PROMPTZONE__', '')

def dashboard_css(s):
    return '''.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 28px 0; }
.kpi span { font-size: 13px; color: var(--muted); }
.kpi b { display: block; font-size: 30px; font-weight: 800; }
.kpi em { font-style: normal; font-size: 12.5px; }
.up { color: var(--accent); } .down { color: #DC2626; }
.charts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-card h3, .table-card h3 { font-size: 15px; margin-bottom: 16px; }
.bars { display: flex; align-items: flex-end; gap: 8px; height: 150px; }
.bars i { flex: 1; border-radius: 4px 4px 0 0; background: __BARSOFT__; transition: height 400ms ease; }
.bars i.hot { background: var(--primary); }
.bars.alt i.hot { background: var(--accent); }
.table-card { margin-bottom: 40px; }
.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; font-size: 12.5px; color: var(--muted); padding: 10px 14px; border-bottom: 1px solid var(--border); }
td { padding: 12px 14px; border-bottom: 1px solid var(--border); white-space: nowrap; }
td small { display: block; color: var(--muted); font-size: 12px; }
.pill { font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.pill.win { background: rgba(5,150,105,.15); color: #047857; }
.pill.new { background: __BARSOFT__; color: var(--primary); }
.pill.risk { background: rgba(220,38,38,.13); color: #DC2626; }
@media (max-width: 900px) { .kpis { grid-template-columns: repeat(2,1fr); } .charts { grid-template-columns: 1fr; } nav { display: none; } }'''.replace('__BARSOFT__', rgba(s['primary'], '.14'))

def mobile_body(s, t, prompt):
    items = ''.join('<div class="lead"><span class="lead-score num">%s</span><div><b>%s</b><small>%s</small></div><span class="pill %s">%s</span></div>' % (
        html.escape(v)[:6], html.escape(b[0]), html.escape(b[1])[:30], cls, label)
        for b, (v, _k), cls, label in zip(t['blocks'], t['stats'], ('hot', 'warm', 'cold'), ('主推', '在册', '备览')))
    summary = ''.join('<div><b class="num">%s</b><span>%s</span></div>' % (v, k) for v, k in t['stats'])
    return '''<div class="stage">
  <div class="phone">
    <div class="notch" aria-hidden="true"></div>
    <div class="statusbar"><span>9:41</span><span>__EN__</span><span>5G ▮▮▮</span></div>
    <header class="apphead">
      <div><small>__META__</small><h1>__BRAND__</h1></div>
      <span class="avatar" aria-hidden="true">__BOLT__</span>
    </header>
    <div class="summary card">__SUMMARY__</div>
    <div class="tabs" role="tablist" aria-label="内容筛选">
      <button class="tab on" role="tab" aria-selected="true">全部</button>
      <button class="tab" role="tab" aria-selected="false">__B1__</button>
      <button class="tab" role="tab" aria-selected="false">__B2__</button>
    </div>
    <div class="leads">__ITEMS__</div>
    <nav class="tabbar" aria-label="主导航">
      <a class="on" href="#">__S1__<span>__B1__</span></a>
      <a href="#">__S2__<span>__B2__</span></a>
      <a href="#">__S3__<span>__B3__</span></a>
      <a href="#">__AVATAR__<span>我的</span></a>
    </nav>
  </div>
  <p class="stage-note">__FOOT__ / <a href="../style-catalog.html">返回风格目录</a> / <a href="../index.html">八版精修样张</a></p>
</div>
__PROMPTZONE__''' \
    .replace('__EN__', html.escape(t.get('en', ''))[:18]) \
    .replace('__META__', html.escape(t['meta'])[:30]) \
    .replace('__BRAND__', html.escape(t['brand'])) \
    .replace('__SUMMARY__', summary) \
    .replace('__B1__', html.escape(t['blocks'][0][0])[:4]) \
    .replace('__B2__', html.escape(t['blocks'][1][0])[:4]) \
    .replace('__B3__', html.escape(t['blocks'][2][0])[:4]) \
    .replace('__ITEMS__', items) \
    .replace('__FOOT__', html.escape(t['foot'])) \
    .replace('__PROMPTZONE__', '') \
    .replace('__S1__', ICON_SEARCH).replace('__S2__', ICON_CHAT).replace('__S3__', ICON_CHART) \
    .replace('__AVATAR__', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6"/></svg>')

def mobile_css(s):
    return '''.stage { min-height: 100vh; display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 36px 16px; __GRID__ }
.phone { width: 390px; max-width: 100%; height: 780px; background: var(--bg);
  border: __BORDER__; border-radius: 44px; overflow: hidden; position: relative;
  box-shadow: __SHADOW__; display: flex; flex-direction: column; }
.notch { position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  width: 120px; height: 26px; border-radius: 999px; background: var(--fg); opacity: .92; z-index: 2; }
.statusbar { display: flex; justify-content: space-between; padding: 16px 26px 6px; font-size: 12.5px; color: var(--muted); }
.apphead { display: flex; justify-content: space-between; align-items: center; padding: 12px 22px; }
.apphead small { font-size: 12.5px; color: var(--muted); }
.apphead h1 { font-size: 22px; font-weight: 800; }
.avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--primary); color: var(--on-primary); display: grid; place-items: center; }
.summary { display: flex; justify-content: space-around; text-align: center; margin: 4px 18px 14px; padding: 16px; }
.summary b { display: block; font-size: 24px; font-weight: 800; color: var(--primary); }
.summary span { font-size: 11.5px; color: var(--muted); }
.tabs { display: flex; gap: 8px; padding: 0 18px 12px; }
.tab { font: inherit; font-size: 13px; font-weight: 600; padding: 7px 16px;
  border-radius: 999px; border: __BORDER__; background: var(--card); color: var(--muted); cursor: pointer; }
.tab.on { background: var(--primary); color: var(--on-primary); border-color: var(--primary); }
.leads { flex: 1; overflow-y: auto; padding: 0 18px; display: grid; gap: 10px; align-content: start; }
.lead { display: flex; align-items: center; gap: 12px; padding: 13px 14px;
  background: var(--card); border: __BORDER__; border-radius: var(--radius); }
.lead-score { width: 42px; height: 42px; flex: none; display: grid; place-items: center;
  font-weight: 800; font-size: 15px; border-radius: calc(var(--radius) * .7); }
.lead:nth-child(1) .lead-score { background: var(--primary); color: var(--on-primary); }
.lead:nth-child(n+2) .lead-score { background: __BARSOFT__; color: var(--primary); }
.lead b { display: block; font-size: 14.5px; }
.lead small { font-size: 12px; color: var(--muted); }
.lead > div { flex: 1; }
.pill { font-size: 11.5px; font-weight: 600; padding: 3px 10px; border-radius: 999px; }
.pill.hot { background: var(--primary); color: var(--on-primary); }
.pill.warm { background: __BARSOFT__; color: var(--primary); }
.pill.cold { background: rgba(120,120,130,.14); color: var(--muted); }
.tabbar { display: flex; border-top: __BORDER__; background: var(--card); padding: 8px 0 18px; }
.tabbar a { flex: 1; display: grid; place-items: center; gap: 3px; color: var(--muted); text-decoration: none; font-size: 10.5px; }
.tabbar a.on { color: var(--primary); }
.stage-note { margin-top: 18px; font-size: 13px; color: var(--muted); text-align: center; }
.stage-note a { color: var(--primary); }
'''.replace('__BARSOFT__', rgba(s['primary'], '.14')).replace('__GRID__', s['grid_pattern'])

ZH_SHORT = {'General': '', 'Mobile': '（移动端）', 'BI/Analytics': '（BI 分析）',
            'Landing Page': '（落地页）', 'Platform/System': '', 'Platform/Material': ''}
TYPE_ZH = {'General': '通用', 'Mobile': '移动端', 'BI/Analytics': 'BI 分析',
           'Landing Page': '落地页', 'Platform/System': '平台语言', 'Platform/Material': '平台语言'}

# ---------- 跨领域主题池（frontend-design：从主题本身找视觉依据，不全是销售） ----------
# 每主题：brand 品牌名 / sub 英文行 / meta 语义行(替代 ALL-CAPS 眉标) / hero 主标题 /
# sub 副文 / blocks×3 内容块 / stats×3 数据 / cta1,cta2 按钮词 / foot 落款 / metaphor 视觉隐喻(供提示词)
THEMES = {
'onsen': dict(brand='松之本汤', en='Matsumoto Onsen', meta='一泊二食 / 満室 8 间 / 泉质 单纯硫磺 42°C',
  hero='山把风挡在外面，汤把山还给你', sub='百年木造汤宿，一处内汤一处露天。泡完不要赶路，炉上有焙茶。',
  blocks=[('晨汤','六点半烧到七点整，硫磺味最正。冬季加雪见酒一盏。'),('岩风吕','母岩原样凿成，水位随山雨涨落，落款在石头上。'),('炉边夜话','晚饭后炉边焙茶配腌梅干，老板娘讲这座山五十年的事。')][:3],
  stats=[('42°C','泉温常年'),('8间','满室即止'),('1908','汤屋始建')], cta1='查空房', cta2='交通与接驳',
  foot='松之本汤 / 长野山间', metaphor='木造汤宿、硫磺泉、焙茶炉、雪见酒；低饱和暖木色与雾白，圆角如被水磨圆的岩石'),
'bakery': dict(brand='麦芒', en='Wheat Awn Bakery', meta='今日炉次 #264 / 醒面 18 小时 / 07:00 出炉',
  hero='六点半的队伍，等的是同一炉面包', sub='天然酵母长时醒面，只用粉、水、盐和一点耐心。卖完是真的卖完。',
  blocks=[('乡村棍','TK 面粉 + 20% 全麦，皮脆心润，配浓汤或什么都不配。'),('可颂','法国黄油开 27 层，出炉两小时内是它的黄金时段。'),('碱水结','碱水重口，配啤酒刚好。下午四点后第二炉半价。')],
  stats=[('18h','低温醒面'),('27层','可颂开酥'),('07:00','头炉出炉')], cta1='看今日炉单', cta2='预约周六',
  foot='麦芒 / 街角面包房', metaphor='面粉袋、麻布、出炉托盘划痕、黄油纸；奶油白与烤麦棕，圆形与豆形圆角如面团'),
'planetarium': dict(brand='市立天文馆', en='City Planetarium', meta='本周天象 / 木星冲日 / 观测夜 20:00 / 云量 <20%',
  hero='把灯关掉，城市才看得见银河', sub='穹顶直径 23 米，每周五公众观测夜。带一件外套，星星不看天气预报以外的软件。',
  blocks=[('穹顶影院','全天域投影 9,000 颗恒星，讲解员现场开麦，不讲神话只讲轨道。'),('公众观测夜','140mm 折射镜看木星条纹与四颗伽利略卫星，排队制。'),('流星雨专场','英仙座极大值夜场，屋顶开放，垫子自备。')],
  stats=[('23m','穹顶直径'),('9,000','投影恒星'),('140mm','主镜口径')], cta1='订观测夜', cta2='本月天象',
  foot='市立天文馆 / 每周五 20:00', metaphor='深空黑、星图连线、望远镜圆顶；光点与细线是仅有的装饰'),
'expedition': dict(brand='北岭登山协会', en='North Ridge Alpine Club', meta='季度简报 / Q4 / 会内山难零记录 / 第 41 年',
  hero='山上没有 KPI，只有天气和路', sub='三十八条成熟线路、四支梯队、一套谁都必须背的守则。登顶是顺便的。',
  blocks=[('梯队制','按体能分四队，宁慢勿抢，掉队有人回头接。'),('线路库','38 条线路含撤退点与水源标注，全部实走复核。'),('雪线课','每年十二月冰镐制动实操，不通过不上雪线。')],
  stats=[('38条','在册线路'),('41年','协会历史'),('0','季度山难')], cta1='加入梯队', cta2='看线路库',
  foot='北岭登山协会 / 季度简报', metaphor='等高线、地图折痕、登山绳纹与雪线；大地色系与信号橙'),
'speedrun': dict(brand='帧数战神', en='Frame Lords Sr Community', meta='本周纪录 12 条 / 验证录像已归档 / Any% / 100%',
  hero='比快更快，快到规则要重写', sub='速通社区：帧级操作、逐帧验证、公开录像。我们崇拜路线，也崇拜改路线的人。',
  blocks=[('路线库','每关最优路线图解，含两个存档点的帧窗口表。'),('验证组','三人交叉审录像，截帧存证，公示七天。'),('周赛','周四晚 Any% 小时赛，新人组单独计分。')],
  stats=[('12条','本周新纪录'),('3人','交叉验证'),('58:31','当前 Any% WR')], cta1='提交纪录', cta2='看本周榜',
  foot='帧数战神 / 速通社区', metaphor='游戏 HUD、帧计数器、录像时间戳；深底高对比与像素感锐边'),
'drive': dict(brand='国道电台', en='HIGHWAY 318 JOURNAL', meta='第 7 天 / 康定 - 理塘 / 海拔 4,014m / 油量 2/3',
  hero='路书只写两行：天亮出发，天黑投宿', sub='两个人一台车，沿 318 慢慢走。加油靠导航，投宿靠缘分，照片全部直出。',
  blocks=[('折多山口','十月的垭口有雪。下车拍照三分钟，手指就交待了。'),('理塘集市','牦牛肉干按斤称，老板娘多送了一把奶糖。'),('姊妹湖','下午四点逆光，湖面像两块没擦的镜子。')],
  stats=[('4,014m','今日海拔'),('2,175km','累计里程'),('7天','在路天数')], cta1='看全程路书', cta2='装备清单',
  foot='国道电台 / 318 手账', metaphor='公路路书、油表、里程标、直出胶片色；地平线构图与夕阳渐层'),
'market': dict(brand='西环街市', en='Sai Wan Market Daily', meta='今日行情 / 10-08 / 鲜鱼到港 04:30 / 摊位 214 家',
  hero='凌晨四点半的码头，决定你中午的汤', sub='街市每日行情：什么当造、什么涨价、哪档的姜最辣。摊贩的话比广告可信。',
  blocks=[('今日鲜鱼','黄花鱼大造，一字刀鲳涨价两成，买鱼看眼不看价牌。'),('当造蔬果','本地菜心甜到不用焯，苦瓜转白露后变面。'),('摊位榜','213 号档的豆腐每天十点前售罄，不是饥饿营销。')],
  stats=[('214家','在市摊位'),('04:30','渔获到港'),('±20%','日价波幅')], cta1='看今日行情', cta2='摊位地图',
  foot='西环街市 / 每日行情', metaphor='街市招牌、价签、红白蓝帆布、霓虹档名；高饱和撞色与块状分区'),
'livehouse': dict(brand='地下一层', en='Basement Live', meta='本周演出 4 场 / 场地容 260 人 / 20:30 开门 21:00 开演',
  hero='声音大一点，世界就小一点', sub='老防空洞改的场子，隔音是水泥的，耳朵是自己的。演出不直播，来现场。',
  blocks=[('周四 / 后摇','三支本地新队，最后一支压轴 40 分钟不说话。'),('周六 / 硬核','全场开火车，护场人员在两侧，眼镜收好。'),('OpenMic','每月末新人开放麦，设备免费用，冷场也是经历。')],
  stats=[('260人','场地容量'),('4场','本周演出'),('21:00','准时开演')], cta1='本周演出', cta2='场地守则',
  foot='地下一层 livehouse', metaphor='演出海报钉墙、荧光棒、音量分贝；粗黑边、大字报与硬阴影'),
'radio': dict(brand='午夜调频', en='MIDNIGHT FM 89.3', meta='今夜节目 23:00-01:00 / 主持人 老麦 / 点播线 6220 3141',
  hero='两点前睡着的，都不算失眠', sub='深夜电台：点播、读信、放歌。城市关灯之后的声音都在这个频段。',
  blocks=[('读信环节','今晚三封：一封道歉的、一封告别的、一封查无此人的。'),('点播榜','《晚安》连续七周第一，点歌人每次都说同一句话。'),('老麦的话','凌晨一点之后的话别当真，但今晚这句你记住。')],
  stats=[('89.3','调频兆赫'),('02:00','节目终了'),('7周','点播冠军')], cta1='今晚节目单', cta2='写一封信',
  foot='午夜调频 89.3 / 23:00', metaphor='电台频谱、调频刻度盘、深夜黑与信号橙；等宽字体与波形线'),
'cinema': dict(brand='星光露天场', en='Starlit Open Air', meta='本季片单 / 胶片放映 / 天黑开演(约 19:20) / 雨映',
  hero='天一黑，白墙就是银幕', sub='老社区的天台露天场，胶片机还是 1994 年那台。蚊子是免费的 3D 效果。',
  blocks=[('本周 / 修复老片','4K 修复版，划痕修掉了一半，留了一半。'),('午夜场','恐怖片连映，自带外套，场方提供驱蚊水。'),('放映员','王师傅守这台机器二十九年，换本比换气还熟。')],
  stats=[('1994','放映机年份'),('19:20','今日开演'),('29年','放映员在岗')], cta1='本季片单', cta2='天台路线',
  foot='星光露天场 / 天黑开演', metaphor='胶片齿孔、放映光锥、幕布白与夜色；纯黑底与高对比光'),
'bookstore': dict(brand='两页书屋', en='Two Pages Books', meta='十月书单 / 上新 37 种 / 营业 12:00-22:00 / 周一休',
  hero='书店不大，够你走神一下午', sub='独立小书店：选书不追榜，分区看心情。坐下看书不赶人，咖啡另算。',
  blocks=[('本月主题架','"写坏天气的人"——16 本关于雨、雾和心软的小说与非虚构。'),('二手角','以书换书，折旧按心情算，绝版书不外借。'),('深夜自习','22 点前灯全亮，最后一小时只留书架灯。')],
  stats=[('37种','本月上新'),('16本','主题架'),('9年','开店年头')], cta1='看十月书单', cta2='到店路线',
  foot='两页书屋 / 周一休', metaphor='书脊、索引卡、纸页毛边与藏书票；纸色底与衬线标题、细线分隔'),
'newsroom': dict(brand='数说编辑部', en='Data Desk', meta='数据专栏 / 第 58 期 / 样本 N=12,406 / 方法附文末',
  hero='把数字问到哑口无言', sub='数据新闻专栏：一个问题、一组数据、一条结论。所有原始数据可下载复核。',
  blocks=[('本期问题','地铁早高峰到底挤在哪三站？我们数了 30 天的客流断面。'),('方法','口径与清洗规则全部公开，欢迎用同一数据推翻我们。'),('下期预告','垃圾分类三年后，湿垃圾真的去发电了吗？')],
  stats=[('12,406','样本量'),('30天','观测窗口'),('58期','专栏期数')], cta1='读本期', cta2='下载数据',
  foot='数说编辑部 / 每周三刊出', metaphor='报纸版面、图表框线、脚注与勘误表；黑白灰加一个信号红'),
'gallery': dict(brand='江畔美术馆', en='Riverside Art Museum', meta='特展 / 展期 11.02-01.15 / 展厅 2F / 全馆禁三脚架',
  hero='好作品不需要导览词帮忙', sub='特展只有一个主张：让画自己说话。展签不超过四十个字，图录厚过展墙。',
  blocks=[('主展厅','23 件布面与纸本，按年代不按流派，走错也是对的。'),('纸上作品厅','低照度展出，每 90 天轮换一次，见一次少一次。'),('公共教育','每周六策展人带看一小时，只讲问题不给答案。')],
  stats=[('23件','在展作品'),('40字','展签上限'),('90天','纸本轮换')], cta1='购特展票', cta2='看展览图录',
  foot='江畔美术馆 / 特展', metaphor='画廊白墙、展签、聚光灯锥与克莱因蓝主视觉；大留白与网格挂线'),
'adoption': dict(brand='带它回家', en='Adoption Week', meta='领养周 / 在册 46 只 / 全部疫苗驱虫 / 面谈制',
  hero='不买陪伴，领养它', sub='城市流浪动物领养平台：全部实名领养、定期回访。冲动的人我们劝退，想清楚的人我们排队。',
  blocks=[('领养流程','申请、家访、面谈、试领两周，任何一步反悔都不丢人。'),('回访制','领养后三个月内两次回访，之后随时可求助，不追责。'),('助养','暂时带不回家的，可以认领月费，照片月更。')],
  stats=[('46只','在册待领'),('2,318','历年领养'),('100%','疫苗驱虫')], cta1='看在册名单', cta2='申请领养',
  foot='带它回家 / 领养周', metaphor='宠物档案卡、领养贴纸与爪印；高可读大字号与高对比配色（无障碍优先）'),
'repair': dict(brand='陈记修理', en='Chan Repair Shop', meta='取件单 #2214 / 修伞/修表/磨刀 / 周三店休',
  hero='修不好的不多，不划算的不少', sub='四十年修理铺：能修的告诉你价，不能修的直接说。这行当赚的是直话直说。',
  blocks=[('修伞','钢骨断一根换一根，伞面破的自己选布，工费明码。'),('修表','机械表洗油 260 起，零件停产的表先问再拆。'),('磨刀','剪子菜刀都磨，立等可取，钝得离谱的加十块。')],
  stats=[('40年','开店年头'),('#2214','今日取件号'),('260起','洗油工费')], cta1='价目表', cta2='到店导航',
  foot='陈记修理 / 周三店休', metaphor='修理价目牌、油渍工作台、老式收据与工具墙；拟物质感与实物旋钮'),
'hotpot': dict(brand='深夜关东煮', en='Midnight Oden', meta='今夜汤底 第 9 年 / 营业至 02:00 / 剩 6 个座',
  hero='汤滚着，夜就没结束', sub='路口的关东煮车，一辆车一口锅九年。萝卜永远最后一个给你留着。',
  blocks=[('汤底','昆布加鲣鱼，九年没断火，每天补汤不换汤。'),('今日串','牛筋炖到筷子夹不起来，鸡蛋限购两枚。'),('老板的话','吃不完别硬撑，明晚汤还在，你也得在。')],
  stats=[('9年','汤底年头'),('02:00','收摊时间'),('6座','店内余位')], cta1='看今日串', cta2='来找车',
  foot='深夜关东煮 / 路口第三盏灯', metaphor='深夜街头摊车、蒸汽、霓虹菜单与价签；暖橘红与夜色、手写体价牌'),
'chess': dict(brand='弈园棋社', en='Yiyuan Chess Club', meta='秋季联赛 / 第 6 轮 / 慢棋 90+30 / 直播间 3 号',
  hero='想三步，落一子', sub='老棋社每周联赛：棋钟不等人，复盘不吵架。赢棋请茶，输棋也请。',
  blocks=[('本轮焦点','头名之争：飞相局对兵底炮，中盘弃马抢先。'),('复盘室','对局结束直接进复盘室，棋盘摆着，谁都能插话。'),('少儿班','周六上午启蒙班，先学输棋再学赢棋。')],
  stats=[('90+30','棋钟时制'),('6轮','联赛进度'),('1962','棋社始创')], cta1='看本轮棋谱', cta2='报名入社',
  foot='弈园棋社 / 秋季联赛', metaphor='棋盘格、棋谱记录纸、棋钟数字与对局批注；方格与纵横线'),
'teamountain': dict(brand='云上茶山', en='Cloud Tea Estate', meta='秋茶季 / 头采 10-02 / 海拔 1,200m / 手工萎凋',
  hero='茶的味道，山说了算', sub='高山茶园四季手记：清明前抢芽，霜降后养树。喝茶人喝到的是那一年的天气。',
  blocks=[('头采秋茶','10 月 2 日开面采，做青偏轻，花香在前汤感在后。'),('做青间','夜里两点翻叶四次，看青做青，不按表办事。'),('养园','霜降停采封园，让茶树睡满一个冬天。')],
  stats=[('1,200m','园地海拔'),('10-02','秋茶头采'),('4次','夜翻青叶')], cta1='订今年秋茶', cta2='看山场图',
  foot='云上茶山 / 季节手记', metaphor='茶山等高线、竹筛萎凋、布巾与山岚；苔绿与陶土色的有机圆角'),
'sailing': dict(brand='白帆会', en='White Sail Club', meta='周赛 / 今日风 东南 4 级 / 13:00 鸣笛 / 视距 8 海里',
  hero='风不认人，只认帆', sub='帆船俱乐部：无风摇桨，有风升帆。海上的规矩只有一条——船比面子重要。',
  blocks=[('今日航线','三角绕标 2 圈，侧顺风段长，压舷别偷懒。'),('安全例会','开船前十分钟点名查救生衣，新人先当配重。'),('夜航训练','每月一次月光航，只靠星与罗经。')],
  stats=[('4级','今日风力和'),('8海里','视距'),('13:00','鸣笛开赛')], cta1='看出航表', cta2='新手体验',
  foot='白帆会 / 帆船俱乐部', metaphor='海图等深线、船帆弧线、罗经刻度与信号旗；海蓝层次与白帆留白'),
'ferry': dict(brand='市轮渡 3 号线', en='CITY FERRY LINE 3', meta='班次表 / 06:30-23:00 / 每 20 分钟 / 全程 12 分钟',
  hero='过江最快的，一直是最慢的这条', sub='轮渡 3 号线：六十年航线没改过。桥修了三座，赶时间的都走了，江还是给剩下的人。',
  blocks=[('班次','早高峰加密到 12 分钟一班，末班 23:00，风雨照开。'),('票价','两块钱二十年没涨，自行车免费，电动车一块。'),('顶层甲板','看日落最好的位置不要钱，带件外套。')],
  stats=[('20min','班次间隔'),('2元','票价'),('12min','过江用时')], cta1='查实时班次', cta2='航线图',
  foot='市轮渡 3 号线 / 六十年航线', metaphor='船票、时刻表、江面与甲板栏杆；交通系统式的清晰层级与扁平色块'),
'hanfu': dict(brand='云想衣裳', en='Yunxiang Atelier', meta='秋冬新款 / 马面裙定制 / 排单至 12 月中 / 可改不可退',
  hero='衣裳有形制，穿法随你', sub='汉服工坊：按出土形制打版，布料随时代走。忠于版，不困于古。',
  blocks=[('马面裙','缠枝纹织金，四对褶清晰，行走不散。'),('圆领袍','窄袖改良，通勤能穿，地铁不挂门。'),('定制流程','量体、选料、白坯试身、成衣，两次可改。')],
  stats=[('12月中','排单至'),('4对褶','马面规'),('2次','免费修改')], cta1='看秋冬新款', cta2='量体预约',
  foot='云想衣裳 / 汉服工坊', metaphor='织锦纹样、盘扣曲线与衣褶垂坠；柔和的大圆角与传统色'),
'printshop': dict(brand='黑桥版画社', en='Black Bridge Press', meta='第 9 期开放工坊 / 木刻/铜版/丝网 / 周六全天',
  hero='每一张，都不一样', sub='版画工坊：手起刀落，油墨上纸。机器印一万张一模一样，手印一万张一万种活。',
  blocks=[('木刻班','单色起步，刻坏三块板算入门，工具自备可租。'),('铜版班','腐蚀间排期紧，防护规则背不熟不让进。'),('限量编号','每版限量编号，毁版公开，绝无加印。')],
  stats=[('9期','工坊届数'),('30张','每版上限'),('1/30','编号起售')], cta1='报周六班', cta2='看版画目录',
  foot='黑桥版画社 / 手印限量', metaphor='油墨滚筒、刻刀痕、版画机与编号铅笔字；三原色几何构成'),
'archive': dict(brand='城市声档', en='City Sound Archive', meta='档案编号 SA-2026 / 已收录 1,842 条 / CC 授权',
  hero='这座城市的耳朵，借你一副', sub='城市声音档案：早市叫卖、末班地铁、桥洞回声。全部条目可免费用于创作。',
  blocks=[('新入档','菜市场卷帘门的开合声，凌晨四点四十，收音距离 2 米。'),('夜班主题包','36 条夜的声音：末班公交、急诊走廊、便利店门铃。'),('投稿','手机即可投稿，注明时间地点，审核后编号入档。')],
  stats=[('1,842','在档条目'),('36条','夜班主题'),('2m','标准收音距')], cta1='听最新入档', cta2='投稿声音',
  foot='城市声档 / 公共档案', metaphor='声波纹、录音电平表、档案编目卡；暗底光点与波形线'),
}

# 族 → 主题映射（同族风格共享主题：不同风格渲染同一主题 = 纯风格对比）
FAMILY_THEME = {
 'neumorph': ['onsen','hanfu'], 'clay': ['bakery','onsen'],
 'distilled': ['bakery','onsen'], 'biomimetic': ['archive','planetarium'],
 'glass': ['planetarium','sailing','onsen'], 'aurora': ['expedition','planetarium'],
 'cyber': ['radio','speedrun','archive'], 'vaporwave': ['drive','radio'],
 'memphis': ['market','printshop'], 'brutal': ['livehouse','hotpot','chess'],
 'pixel': ['speedrun','chess'], 'paper': ['bookstore','gallery','teamountain'],
 'dark': ['cinema','radio'], 'swiss': ['gallery','bookstore','printshop'],
 'a11y': ['adoption','ferry'], 'skeuo': ['repair','onsen'],
 'chaos': ['hotpot','market'], 'kinetic': ['chess','livehouse'],
 'organic': ['teamountain','onsen'], '3d': ['sailing','planetarium'],
 'vibrant': ['market','hotpot'], 'micro': ['ferry','speedrun'],
 'soft': ['hanfu','bakery'], 'bauhaus': ['printshop','gallery'],
 'm3': ['bakery','hanfu'], 'fluent': ['ferry','newsroom'],
 'polaris': ['bookstore','bakery'], 'spectrum': ['printshop','gallery'],
 'zero': ['radio','archive'], 'voice': ['archive','radio'],
 'antipolish': ['repair','ferry'], 'parallax': ['expedition','teamountain'],
 'cursor': ['gallery','speedrun'], 'modern': ['newsroom'],
}
# data（BI）族内部轮换，避免 13 个仪表盘一个主题
DATA_CYCLE = ['newsroom', 'ferry', 'market', 'expedition', 'sailing', 'archive']

# 族的一次亮相动效说明（写入提示词；frontend-design：一次编排好的亮相）
FAMILY_MOTION = {
 'neumorph': '开关/按钮的内凹按压反馈（150ms），无入场动画', 'clay': '卡片 hover 轻浮起（材质动效）',
 'glass': '无入场动画，材质本身即视觉（毛玻璃+光斑为静态）', 'aurora': '渐变光斑 8-12s 缓慢流动（氛围）',
 'cyber': '扫描线一次扫过 + 标题辉光', 'vaporwave': '渐变文字一次流光', 'memphis': '色块/盖章式一次砸落',
 'brutal': '瞬时位移（无平滑过渡即风格）', 'pixel': '无（锐利静态）', 'paper': '无入场，hover 微阴影',
 'dark': '无入场，纯黑沉浸', 'data': '图表条形一次生长', 'swiss': '无入场，网格即秩序',
 'a11y': '无装饰动效（可访问性优先）', 'skeuo': '按钮按压物理感', 'chaos': '卡片旋转归位一次',
 'kinetic': '标题描边-填充循环（字即动效）', 'organic': '有机形状轻微呼吸', '3d': '层叠阴影一次落定',
 'distilled': '无入场动画；grain 颗粒纹理常驻 + ease-out 缓动（手作静态感）',
 'biomimetic': '呼吸脉冲（scale 1→1.05 慢循环，官方 breathing）',
 'vibrant': '色块 hover 换色（瞬时）', 'micro': '图标一次弹跳（pop）', 'soft': '阴影柔化过渡',
 'bauhaus': '几何形状瞬时定位', 'm3': '状态层涟漪一次', 'fluent': '阴影深度过渡（8px→16px）',
 'polaris': '无入场，微阴影过渡', 'spectrum': '无入场，1px 阴影过渡', 'zero': '无动效（零界面）',
 'voice': '声波条持续律动（波形=主题部件）', 'antipolish': '无任何动效', 'parallax': 'hero 一次浮动 + 背景错位',
 'cursor': '自定义光标点跟随', 'modern': '一次淡入',
}

def theme_for(r, fam, idx):
    if fam == 'data':
        return THEMES[DATA_CYCLE[idx % len(DATA_CYCLE)]], DATA_CYCLE[idx % len(DATA_CYCLE)]
    key = FAMILY_THEME.get(fam, 'newsroom')
    return THEMES[key], key
ZH_NAMES = {
 'Minimalism & Swiss Style':'极简主义 / 瑞士风格','Neumorphism':'新拟态（软 UI）','Glassmorphism':'玻璃拟态',
 'Brutalism':'粗野主义','3D & Hyperrealism':'3D 超写实','Vibrant & Block-based':'高饱和色块',
 'Dark Mode (OLED)':'深色模式（OLED 纯黑）','Accessible & Ethical':'无障碍 / 伦理设计','Claymorphism':'黏土拟态',
 'Aurora UI':'极光 UI','Retro-Futurism':'复古未来主义','Flat Design':'扁平设计','Skeuomorphism':'拟物化',
 'Liquid Glass':'液态玻璃','Motion-Driven':'动效驱动','Micro-interactions':'微交互','Inclusive Design':'包容性设计',
 'Zero Interface':'零界面','Soft UI Evolution':'Soft UI 演进','Data-Dense Dashboard':'数据密集仪表盘',
 'Neubrutalism':'新粗野主义','Bento Box Grid':'便当盒网格','Y2K Aesthetic':'Y2K 千禧风','Cyberpunk UI':'赛博朋克',
 'Organic Biophilic':'有机亲自然','AI-Native UI':'AI 原生界面','Memphis Design':'孟菲斯设计',
 'Dimensional Layering':'维度分层','Exaggerated Minimalism':'夸张极简','Kinetic Typography':'动态字排',
 'Parallax Storytelling':'视差叙事','HUD / Sci-Fi FUI':'HUD 科幻界面','Pixel Art':'像素风',
 'Spatial UI (VisionOS)':'空间界面（VisionOS）','E-Ink / Paper':'电子墨水 / 纸感','Gen Z Chaos / Maximalism':'Z 世代极繁主义',
 'Biomimetic / Organic 2.0':'仿生有机 2.0','Anti-Polish / Raw Aesthetic':'反抛光粗粝风',
 'Tactile Digital / Deformable UI':'触感可形变 UI','Nature Distilled':'自然提纯','Interactive Cursor Design':'交互光标设计',
 'Voice-First Multimodal':'语音优先多模态','3D Product Preview':'3D 产品预览','Editorial Grid / Magazine':'杂志编辑网格',
 'Vintage Analog / Retro Film':'复古胶片','Bauhaus (包豪斯)':'包豪斯','Material 3 Expressive (Mobile)':'Material 3 表现版',
 'Fluent 2':'Fluent 2（微软）','Shopify Polaris':'Polaris（Shopify）','Adobe Spectrum':'Spectrum（Adobe）',
 'Heat Map & Heatmap Style':'热力图风格','Executive Dashboard':'高管驾驶舱','Real-Time Monitoring':'实时监控大屏',
 'Drill-Down Analytics':'下钻分析','Comparative Analysis Dashboard':'对比分析仪表盘','Predictive Analytics':'预测分析',
 'User Behavior Analytics':'用户行为分析','Financial Dashboard':'财务仪表盘','Sales Intelligence Dashboard':'销售智能仪表盘',
 'Vaporwave':'蒸汽波','Swiss Modernism 2.0':'瑞士现代主义 2.0','Gradient Mesh / Aurora Evolved':'渐变网格（极光演进）',
 'Chromatic Aberration / RGB Split':'色差 RGB 分离','Minimalist Monochrome':'极简单色（移动）',
 'Modern Dark (Cinema Mobile)':'影院深色（移动）','SaaS Mobile (High-Tech Boutique)':'精品 SaaS（移动）',
 'Terminal CLI (Mobile)':'终端 CLI 风（移动）','Kinetic Brutalism (Mobile)':'动效粗野（移动）',
 'Flat Design Mobile (Touch-First)':'扁平触控（移动）','Neo Brutalism (Mobile)':'新粗野（移动）',
 'Bold Typography (Mobile Poster)':'海报粗字排（移动）','Academia (Scholarly Mobile)':'学术书卷（移动）',
 'Cyberpunk Mobile HUD':'赛博 HUD（移动）','Bitcoin DeFi (Mobile)':'加密 DeFi（移动）',
 'Claymorphism (Mobile)':'黏土拟态（移动）','Enterprise SaaS (Mobile)':'企业 SaaS（移动）',
 'Sketch Hand-Drawn (Mobile)':'手绘素描（移动）','Neumorphism (Mobile)':'新拟态（移动）','Spectrum 2':'Spectrum 2（Adobe）',
}

# ---------- 产品类型样板：products.csv + colors.csv 官方推荐组合 ----------
def load_styles_by_name():
    return {r['Style Category']: r for r in csv.DictReader(open(SRC, encoding='utf-8'))}

def load_products():
    prods = list(csv.DictReader(open(SRC_PRODUCTS, encoding='utf-8')))
    cols = {r['Product Type']: r for r in csv.DictReader(open(SRC_COLORS, encoding='utf-8'))}
    return [(p, cols[p['Product Type']]) for p in prods if p['Product Type'] in cols]

def product_skin(p, styles_by_name):
    first = p['Primary Style Recommendation'].split('+')[0].strip()
    row = styles_by_name.get(first)
    if row is None:
        for name, r in styles_by_name.items():
            if first.lower() in name.lower() or name.lower() in first.lower():
                row = r; break
    return (make_skin(row) if row else base_skin()), row

def apply_product_colors(s, col):
    """色板唯一来源：colors.csv 官方 token。"""
    bg, fg = col['Background'], col['Foreground']
    dark = yiq(bg) < 80
    s['bg_mode'] = 'dark' if dark else 'light'
    C(s, bg, fg, col['Muted Foreground'], col['Card'], col['Border'],
      col['Primary'], col['Secondary'], col['Accent'])
    s['on_primary'] = col['On Primary']

def product_theme(p, col):
    return dict(
        brand=p['Product Type'], en=p['Product Type'],
        meta=p['Keywords'].strip(),
        hero=p['Product Type'],
        sub='%s —— %s' % (p['Color Palette Focus'].strip(), p['Key Considerations'].strip()),
        blocks=[
            ('主推风格', 'Primary: %s；Secondary: %s。' % (p['Primary Style Recommendation'].strip(), p['Secondary Styles'].strip())),
            ('落地结构', 'Pattern: %s。%s' % (p['Landing Page Pattern'].strip(),
                ('Dashboard: ' + p['Dashboard Style (if applicable)'].strip()) if p['Dashboard Style (if applicable)'].strip() else '')),
            ('关键考量', p['Key Considerations'].strip()),
        ],
        stats=[(col['Primary'], 'Primary'), (col['Secondary'], 'Secondary'), (col['Accent'], 'Accent')],
        cta1='查看官方色板', cta2='设计系统检索',
        foot='官方推荐组合 No.%s' % p['No'],
        metaphor='%s；色板方向：%s' % (p['Keywords'].strip()[:80], p['Color Palette Focus'].strip()),
    )

def product_prompt(p, col, layout=None):
    return '\n'.join([
        '请为「%s」产品做 UI 设计，严格按 ui-ux-pro-max 官方推荐组合执行：〔在这里写下你的页面需求〕' % p['Product Type'],
        '',
        '▍页面布局：%s成品页（复刻本样张的整体形态）' % (LAYOUT_ZH.get(layout, '定价页') if layout else '定价页'),
        '',
        '▍官方推荐（products.csv 原文，零改写）：',
        '- Primary Style Recommendation: %s' % p['Primary Style Recommendation'].strip(),
        '- Secondary Styles: %s' % p['Secondary Styles'].strip(),
        '- Landing Page Pattern: %s' % p['Landing Page Pattern'].strip(),
        '- Dashboard Style: %s' % (p['Dashboard Style (if applicable)'].strip() or '（不适用）'),
        '- Color Palette Focus: %s' % p['Color Palette Focus'].strip(),
        '- Key Considerations: %s' % p['Key Considerations'].strip(),
        '',
        '▍官方色板（colors.csv 原文，直接使用）：',
        '- Primary %s（文字 %s）/ Secondary %s / Accent %s（文字 %s）' % (col['Primary'], col['On Primary'], col['Secondary'], col['Accent'], col['On Accent']),
        '- Background %s / Foreground %s / Card %s / Border %s / Muted 文字 %s / Ring %s' % (col['Background'], col['Foreground'], col['Card'], col['Border'], col['Muted Foreground'], col['Ring']),
        '- %s' % col.get('Notes', '').strip(),
        '',
        '▍必须避开（AI 指纹清单，frontend-design 原则）：',
        '- ALL-CAPS 装饰性眉标（信息行须有语义）；按钮尾部箭头 →；中点分隔 meta 串',
        '- 逐卡片 fade-in 上升；无语义 01/02/03 编号；默认 Inter/Roboto；emoji 图标',
        '',
        '▍验收：正文对比度 ≥4.5:1；:focus-visible；prefers-reduced-motion；响应式 375/768/1440 无横向滚动',
    ])

# ---------- 产品成品模板：8 种页面布局（与风格页的 hero+三卡 形态彻底区分） ----------
LAYOUT_RULES_PRE = [
    (['membership', 'community', 'forum', 'q&a', 'confession'], 'community'),
    (['freelancer', 'portfolio', 'personal', 'resume', 'cv builder', 'link-in-bio', 'creator economy'], 'profile'),
    (['remote work', 'collaboration', 'event management', 'project'], 'kanban'),
]
LAYOUT_RULES = LAYOUT_RULES_PRE + [
    (['dashboard', 'analytics', 'monitoring', 'crm', 'inventory', 'rpa', 'fleet', 'iot', 'status page', 'logistics', 'charging', 'smart home'], 'dashboard'),
    (['ecommerce', ' e-commerce', 'shop', 'store', 'retail', 'marketplace', 'classifieds', 'luxury', 'florist', 'pharmacy', 'drug', 'grocery', 'dealership', 'subscription box', 'brewery', 'winery', 'auction', 'gift', 'wishlist', 'digital products', 'nft', 'web3'], 'shop'),
    (['restaurant', 'food service', 'bakery', 'cafe', 'food delivery', 'catering', 'recipe', 'cooking'], 'menu'),
    (['podcast', 'music streaming', 'video streaming', 'ott', 'cinema', 'theater', 'music creation', 'beat maker', 'generative art', 'meme', 'sticker'], 'media'),
    (['clinic', 'dental', 'veterinary', 'medical', 'spa', 'wellness service', 'salon', 'beauty', 'hotel', 'hospitality', 'travel', 'tourism', 'wedding', 'event planning', 'coworking', 'childcare', 'daycare', 'senior care', 'elderly', 'telemedicine', 'home service', 'plumber', 'electrician', 'fitness', 'gym', 'yoga', 'meditation', 'booking', 'appointment', 'mental health'], 'booking'),
    (['real estate', 'property', 'job board', 'recruitment', 'directory', 'listing', 'review platform', 'parking', 'transit guide', 'local events', 'hyperlocal', 'rental'], 'listing'),
    (['news', 'magazine', 'blog', 'knowledge base', 'documentation', 'academic', 'journal', 'scholarly', 'wiki', 'encyclopedia', 'changelog', 'release notes', 'conference', 'symposium', 'open source', 'forum', 'q&a', 'community platform', 'newsletter', 'church', 'non-profit', 'charity', 'government', 'portal', 'university', 'research'], 'article'),
    (['saas', 'b2b', 'productivity', 'developer', 'vpn', 'privacy', 'cybersecurity', 'no-code', 'low-code', 'e-signature', 'feature flag', 'api', 'ide', 'billing', 'invoice', 'password', 'email client', 'file manager', 'translator', 'calculator', 'calendar', 'scheduling', 'notes', 'resume', 'survey', 'form builder', 'lms', 'e-learning', 'online course', 'bootcamp', 'language learning', 'insurance', 'banking', 'fintech', 'crypto', 'legal', 'marketing agency', 'creative agency', 'photography studio', 'architecture', 'interior', 'construction', 'biotech', 'aerospace', 'space tech', 'quantum', 'energy', 'climate', 'agriculture', 'farm'], 'pricing'),
]
LAYOUT_ZH = {'dashboard': '仪表盘', 'shop': '商店页', 'menu': '菜单页', 'media': '媒体页',
             'booking': '预约页', 'listing': '列表页', 'article': '文章页', 'pricing': '定价页', 'phone': '手机 App', 'community': '社区论坛', 'profile': '个人主页', 'kanban': '任务看板'}

def classify_layout(p):
    text = (p['Product Type'] + ' ' + p['Keywords']).lower()
    for kws, name in LAYOUT_RULES:
        if any(k in text for k in kws):
            return name
    if 'app' in text or 'tracker' in text or 'game' in text:
        return 'phone'
    return 'article'

SHARED_LAYOUT_CSS = '''
.promo-bar { background: var(--primary); color: var(--on-primary); text-align: center;
  padding: 9px 16px; font-size: 13.5px; font-weight: 600; }
.chips-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 22px 0 18px; }
.fchip { font: inherit; font-size: 13px; font-weight: 600; padding: 7px 16px;
  border-radius: 999px; border: 1.5px solid var(--border); background: var(--card);
  color: var(--muted); cursor: pointer; }
.fchip.on { background: var(--primary); color: var(--on-primary); border-color: var(--primary); }
.fchip:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.section-h { font-size: 16px; font-weight: 800; margin: 30px 0 14px;
  display: flex; align-items: baseline; gap: 10px; }
.section-h small { font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  color: var(--muted); font-weight: 400; letter-spacing: .1em; }
'''

def shop_body(p, col):
    goods = ''.join('<article class="g-card"><div class="g-img" aria-hidden="true"></div>'
        '<h3>%s</h3><p class="g-price">¥%s</p>'
        '<button class="g-add" type="button" aria-label="加入购物车：%s"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></button></article>'
        % (n, pr, n) for n, pr in
        [('手工陶瓷杯', '128'), ('帆布托特包', '98'), ('大豆香薰蜡烛', '158'),
         ('美利奴羊毛袜', '76'), ('车线装笔记本', '58'), ('黄铜书立', '188'),
         ('手冲滤架', '216'), ('亚麻桌布', '168')])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">购物车 (3)</a>
</div></header>
<div class="promo-bar">限时：全场满 ¥199 免运费 / 新客首单 9 折</div>
<main class="container">
  <div class="chips-row" role="group" aria-label="商品筛选">
    <button class="fchip on" type="button">全部</button><button class="fchip" type="button">新品</button>
    <button class="fchip" type="button">热卖</button><button class="fchip" type="button">生活杂货</button><button class="fchip" type="button">文具</button>
  </div>
  <h2 class="section-h">本周选品 <small>WEEKLY PICKS</small></h2>
  <div class="g-grid">__GOODS__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV) \
    .replace('__GOODS__', goods).replace('__NO__', p['No']).replace('__BOLT__', BOLT)

SHOP_CSS = SHARED_LAYOUT_CSS + '''
.g-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-bottom: 50px; }
.g-card { background: var(--card); border: __BORDER__; border-radius: var(--radius);
  box-shadow: __SHADOW__; padding: 14px; position: relative; }
.g-img { height: 120px; border-radius: calc(var(--radius) * .7);
  background: linear-gradient(135deg, var(--secondary), var(--primary)); opacity: .85; margin-bottom: 12px; }
.g-card h3 { font-size: 14.5px; margin-bottom: 4px; }
.g-price { font-family: 'IBM Plex Mono', monospace; font-size: 15px; font-weight: 600; color: var(--primary); }
.g-add { position: absolute; right: 14px; bottom: 14px; width: 34px; height: 34px;
  border-radius: 50%; border: none; background: var(--primary); color: var(--on-primary);
  display: grid; place-items: center; cursor: pointer; }
.g-add:hover { opacity: .85; }
@media (max-width: 900px) { .g-grid { grid-template-columns: repeat(2, 1fr); } }
'''

def pricing_body(p, col):
    feats = lambda fs: ''.join('<li%s>%s %s</li>' % (' class="off"' if off else '',
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>' if not off else
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>', f) for f, off in fs)
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">免费开始</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:center;margin:44px 0 6px">按月订阅 / 随时取消 / 学生半价</p>
  <h1 class="pr-h">选择适合你的方案</h1>
  <div class="pr-grid">
    <section class="card pr-tier">
      <h3>基础</h3><p class="pr-price">¥0<span>/月</span></p>
      <ul class="pr-feats">__F1__</ul>
      <a class="btn" href="#">直接开始</a>
    </section>
    <section class="card pr-tier hot">
      <span class="pr-badge">最多人选</span>
      <h3>专业</h3><p class="pr-price">¥39<span>/月</span></p>
      <ul class="pr-feats">__F2__</ul>
      <a class="btn btn-primary" href="#">开始 14 天试用</a>
    </section>
    <section class="card pr-tier">
      <h3>团队</h3><p class="pr-price">¥99<span>/月</span></p>
      <ul class="pr-feats">__F3__</ul>
      <a class="btn" href="#">联系开通</a>
    </section>
  </div>
  <section class="pr-faq">
    <h2 class="section-h">常见问题 <small>FAQ</small></h2>
    <details><summary>可以随时换方案或取消吗？</summary><p>可以，升级立即生效，降级与取消在当前计费周期结束时生效，不收违约金。</p></details>
    <details><summary>发票怎么开？</summary><p>支持增值税普通发票与专票，在账单中心自助申请，1-3 个工作日开出。</p></details>
  </section>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__F1__', feats([('核心功能', 0), ('2 个成员席位', 0), ('社区支持', 0), ('高级分析', 1), ('优先支持', 1), ('SLA 保障', 1)])) \
    .replace('__F2__', feats([('基础全部功能', 0), ('20 个成员席位', 0), ('高级分析', 0), ('优先支持', 0), ('SLA 保障', 1), ('私有部署', 1)])) \
    .replace('__F3__', feats([('专业全部功能', 0), ('席位不限', 0), ('高级分析', 0), ('优先支持', 0), ('SLA 保障', 0), ('私有部署', 0)])) \
    .replace('__BOLT__', BOLT)

PRICING_CSS = SHARED_LAYOUT_CSS + '''
.pr-h { text-align: center; font-size: clamp(26px, 4vw, 38px); font-weight: 800; margin-bottom: 30px; }
.pr-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: start; }
.pr-tier { position: relative; }
.pr-tier.hot { border: 2.5px solid var(--primary); transform: translateY(-8px); }
.pr-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: var(--primary); color: var(--on-primary); font-size: 11.5px; font-weight: 700;
  padding: 3px 12px; border-radius: 999px; white-space: nowrap; }
.pr-tier h3 { font-size: 16px; }
.pr-price { font-family: 'IBM Plex Mono', monospace; font-size: 34px; font-weight: 600; margin: 10px 0 14px; }
.pr-price span { font-size: 13px; color: var(--muted); }
.pr-feats { list-style: none; margin-bottom: 18px; }
.pr-feats li { display: flex; align-items: center; gap: 8px; font-size: 13.5px; padding: 6px 0; }
.pr-feats li.off { color: var(--muted); opacity: .65; }
.pr-faq { margin: 40px 0 60px; max-width: 640px; }
.pr-faq details { border-bottom: 1px solid var(--border); padding: 12px 4px; }
.pr-faq summary { cursor: pointer; font-weight: 600; font-size: 14.5px; }
.pr-faq p { font-size: 13.5px; color: var(--muted); margin-top: 8px; }
@media (max-width: 860px) { .pr-grid { grid-template-columns: 1fr; } .pr-tier.hot { transform: none; } }
'''

def menu_body(p, col):
    items = ''.join('<div class="m-item"><div class="m-name"><b>%s</b><small>%s</small></div>'
        '<span class="m-dots" aria-hidden="true"></span><span class="m-price">¥%s</span></div>' % (n, d, pr) for n, d, pr in [
        ('手冲 / 耶加雪菲', '柑橘与花香，浅焙', '32'), ('澳白', '双份浓缩，奶厚 5mm', '28'),
        ('冷萃 / 冰博克', '冷藏 16 小时，奶香浓', '34'), ('煎茶拿铁', '石川县煎茶，微甜', '30'),
        ('可颂', '法国黄油 27 层', '22'), ('碱水结', '碱水重口，配啤酒刚好', '18'),
        ('巴斯克蛋糕', '焦壳流心，每日限量', '32'), ('肉桂卷', '现烤出炉 11:00 / 16:00', '24')])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">订位</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:30px 0 4px">今日营业 08:00 – 22:00 / 最后点单 21:30 / 周一店休</p>
  <h1 class="mn-h">__PT__</h1>
  <p class="mn-sub">豆子每周二到店，烘焙度按批次微调；菜单随季节换三分之一。</p>
  <h2 class="section-h">本季饮品 <small>DRINKS</small></h2>
  <div class="m-list">__I1__</div>
  <h2 class="section-h">现烤烘焙 <small>BAKERY</small></h2>
  <div class="m-list">__I2__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__I1__', items[:items.index('<h2')] if False else ''.join(items.split('</div>')[:4]).replace('</div>', '</div>')) \
    .replace('__I2__', '') \
    .replace('__BOLT__', BOLT)

MENU_CSS = SHARED_LAYOUT_CSS + '''
.mn-h { font-size: clamp(28px, 4.4vw, 40px); font-weight: 800; margin-bottom: 8px; }
.mn-sub { font-size: 14.5px; color: var(--muted); margin-bottom: 8px; }
.m-list { max-width: 640px; }
.m-item { display: flex; align-items: baseline; gap: 10px; padding: 12px 0;
  border-bottom: 1px dotted var(--border); }
.m-name b { font-size: 15.5px; }
.m-name small { display: block; font-size: 12.5px; color: var(--muted); }
.m-dots { flex: 1; border-bottom: 2px dotted var(--border); transform: translateY(-4px); }
.m-price { font-family: 'IBM Plex Mono', monospace; font-weight: 600; }
'''

def media_body(p, col):
    eps = ''.join('<div class="ep"><span class="ep-no">%02d</span><div class="ep-info"><b>%s</b><small>%s</small></div>'
        '<span class="ep-dur">%s</span>'
        '<button class="ep-play" type="button" aria-label="播放：%s"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button></div>'
        % (i, t, d, dur, t) for i, (t, d, dur) in enumerate([
            ('为什么我们仍在听播客', '通勤、做饭、失眠的时候', '48:21'),
            ('和一个守灯塔的人聊了聊', '孤独是种手艺', '62:03'),
            ('城市里的野生声音', '凌晨四点的码头与早市', '39:44'),
            ('关于慢的十种实践', '越慢越准', '55:17'),
            ('老歌的三秒钟', '前奏决定一切', '44:08'),
            ('季节性友谊', '有些朋友是夏天的', '51:32')], 1))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">订阅</a>
</div></header>
<main class="container">
  <section class="cover card">
    <div class="cover-art" aria-hidden="true"></div>
    <div class="cover-info">
      <p class="doc-meta" style="justify-content:flex-start;margin-bottom:10px">第 3 季 / 每周三更新 / 已更新 62 期</p>
      <h1>耳边风景</h1>
      <p class="cover-sub">关于城市、手艺与慢生活的对话式节目。主播两位，嘉宾不定，片头曲是主播自己弹的。</p>
      <div class="cta-row2"><a class="btn btn-primary" href="#">订阅收听</a><a class="btn" href="#">全部剧集</a></div>
    </div>
  </section>
  <h2 class="section-h">全部剧集 <small>EPISODES</small></h2>
  <div class="ep-list">__EPS__</div>
</main>
<div class="player" role="region" aria-label="播放器">
  <span class="pl-art" aria-hidden="true"></span>
  <div class="pl-info"><b>06 / 季节性友谊</b>
    <div class="pl-bar" role="img" aria-label="播放进度 35%"><i style="width:35%"></i></div></div>
  <span class="pl-time">18:02 / 51:32</span>
  <button class="ep-play big" type="button" aria-label="暂停"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg></button>
</div>
<footer style="padding-bottom:86px">__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__EPS__', eps).replace('__BOLT__', BOLT)

MEDIA_CSS = SHARED_LAYOUT_CSS + '''
.cover { display: grid; grid-template-columns: 300px 1fr; gap: 28px; padding: 28px; margin-top: 30px; }
.cover-art { border-radius: calc(var(--radius) * .8); min-height: 260px;
  background: conic-gradient(from 220deg, var(--primary), var(--secondary), var(--accent), var(--primary)); opacity: .9; }
.cover-info h1 { font-size: clamp(26px, 3.6vw, 36px); margin-bottom: 10px; }
.cover-sub { font-size: 14.5px; color: var(--muted); max-width: 420px; margin-bottom: 20px; }
.cta-row2 { display: flex; gap: 12px; flex-wrap: wrap; }
.ep-list { margin-bottom: 46px; }
.ep { display: flex; align-items: center; gap: 16px; padding: 13px 14px;
  border-bottom: 1px solid var(--border); }
.ep:hover { background: var(--card); }
.ep-no { font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: var(--muted); width: 26px; }
.ep-info b { font-size: 15px; display: block; }
.ep-info small { font-size: 12.5px; color: var(--muted); }
.ep-dur { margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: var(--muted); }
.ep-play { width: 38px; height: 38px; border-radius: 50%; border: none; flex: none;
  background: var(--primary); color: var(--on-primary); display: grid; place-items: center; cursor: pointer; }
.ep-play.big { width: 44px; height: 44px; }
.player { position: fixed; left: 0; right: 0; bottom: 0; z-index: 20;
  display: flex; align-items: center; gap: 16px; padding: 12px 26px;
  background: var(--card); border-top: __BORDER__; box-shadow: 0 -8px 30px rgba(0,0,0,.12); }
.pl-art { width: 42px; height: 42px; border-radius: calc(var(--radius) * .5);
  background: linear-gradient(135deg, var(--secondary), var(--primary)); }
.pl-info { flex: 1; }
.pl-info b { font-size: 13.5px; }
.pl-bar { height: 6px; border-radius: 3px; background: var(--muted); margin-top: 6px; max-width: 520px; }
.pl-bar i { display: block; height: 100%; border-radius: 3px; background: var(--primary); }
.pl-time { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--muted); }
@media (max-width: 860px) { .cover { grid-template-columns: 1fr; } .cover-art { min-height: 180px; } }
'''

def booking_body(p, col):
    svcs = ''.join('<label class="svc card"><input type="radio" name="svc" aria-label="%s"><span class="svc-dot" aria-hidden="true"></span><b>%s</b><small>%s / ¥%s</small></label>'
        % (n, n, d, pr) for n, d, pr in [
        ('初次到访 / 60 分钟', '含评估与方案沟通', '198'),
        ('标准护理 / 45 分钟', '常规项目', '158'),
        ('深度疗程 / 90 分钟', '含专项与随访', '328')])
    slots = ''.join('<button class="fchip%s" type="button">%s</button>' % (' on' if i == 1 else '', t)
        for i, t in enumerate(['今天 14:00', '今天 15:00', '今天 16:00', '明天 10:00', '明天 11:30']))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">登录</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:34px 0 6px">线上预约 / 到店签到 / 提前 2 小时可改期</p>
  <h1 class="bk-h">预约一个时段</h1>
  <h2 class="section-h">选择项目 <small>SERVICE</small></h2>
  <div class="svc-row">__SVCS__</div>
  <h2 class="section-h">选择时段 <small>TIME SLOT</small></h2>
  <div class="chips-row">__SLOTS__</div>
  <h2 class="section-h">你的信息 <small>CONTACT</small></h2>
  <form class="bk-form card" onsubmit="return false">
    <label>姓名<input type="text" placeholder="怎么称呼你" required></label>
    <label>手机号<input type="tel" placeholder="用于到店确认" required></label>
    <label>备注<textarea rows="3" placeholder="过敏史、偏好或想聊的（选填）"></textarea></label>
    <button class="btn btn-primary" type="submit">确认预约</button>
  </form>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__SVCS__', svcs).replace('__SLOTS__', slots).replace('__BOLT__', BOLT)

BOOKING_CSS = SHARED_LAYOUT_CSS + '''
.bk-h { font-size: clamp(26px, 4vw, 38px); font-weight: 800; margin-bottom: 6px; }
.svc-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.svc { display: flex; flex-direction: column; gap: 6px; cursor: pointer; }
.svc input { position: absolute; opacity: 0; }
.svc-dot { width: 20px; height: 20px; border-radius: 50%; border: 2.5px solid var(--border); }
.svc input:checked ~ .svc-dot { border-color: var(--primary);
  box-shadow: inset 0 0 0 4.5px var(--primary); }
.svc b { font-size: 15.5px; }
.svc small { font-size: 13px; color: var(--muted); }
.svc input:focus-visible ~ .svc-dot { outline: 3px solid var(--accent); outline-offset: 2px; }
.bk-form { display: grid; gap: 14px; max-width: 480px; margin-bottom: 56px; }
.bk-form label { display: grid; gap: 6px; font-size: 13.5px; font-weight: 600; }
.bk-form input, .bk-form textarea { font: inherit; font-weight: 400; padding: 11px 14px;
  border-radius: calc(var(--btn-radius)); border: 1.5px solid var(--border);
  background: var(--bg); color: var(--fg); }
.bk-form input:focus, .bk-form textarea:focus { outline: 3px solid var(--primary); outline-offset: 1px; }
@media (max-width: 860px) { .svc-row { grid-template-columns: 1fr; } }
'''

def listing_body(p, col):
    results = ''.join('<article class="r-card card"><div class="r-img" aria-hidden="true"></div>'
        '<div class="r-info"><div class="r-top"><b>%s</b><span class="r-score">%s</span></div>'
        '<small>%s</small><div class="r-tags">%s</div></div>'
        '<div class="r-side"><span class="r-price">¥%s<span>/晚</span></span><a class="btn btn-primary" href="#">查看</a></div></article>'
        % (n, sc, loc, ''.join('<span class="r-tag">%s</span>' % t for t in tags), pr) for
        n, sc, loc, tags, pr in [
        ('临江loft / 落地窗', '4.9', '滨江西路 / 距地铁 300m', ['整套', '可做饭'], '368'),
        ('老宅木屋 / 带院', '4.8', '旧城南锣 / 巷子里', ['整套', '有院'], '428'),
        ('设计师公寓', '4.7', 'CBD 东侧 / 楼下即商圈', ['独卫', '电梯'], '318'),
        ('山顶观景房', '4.9', '北岭半山 / 观星绝佳', ['含早', '接送'], '528')])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">发布房源</a>
</div></header>
<main class="container">
  <form class="search-row" onsubmit="return false" role="search">
    <input type="search" placeholder="目的地、房源名或关键词…" aria-label="搜索">
    <input type="date" value="2026-10-20" aria-label="入住日期">
    <input type="date" value="2026-10-22" aria-label="离店日期">
    <button class="btn btn-primary" type="submit">搜索</button>
  </form>
  <div class="chips-row" role="group" aria-label="筛选">
    <button class="fchip on" type="button">推荐</button><button class="fchip" type="button">价格 ↑</button>
    <button class="fchip" type="button">评分优先</button><button class="fchip" type="button">整套</button><button class="fchip" type="button">可做饭</button>
  </div>
  <p class="doc-meta" style="justify-content:flex-start;margin-bottom:14px">共 214 条结果 / 显示 1-4</p>
  <div class="r-list">__RESULTS__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__RESULTS__', results).replace('__BOLT__', BOLT)

LISTING_CSS = SHARED_LAYOUT_CSS + '''
.search-row { display: grid; grid-template-columns: 1fr 150px 150px auto; gap: 10px; margin-top: 30px; }
.search-row input { font: inherit; font-size: 14px; padding: 11px 14px;
  border: 1.5px solid var(--border); border-radius: calc(var(--btn-radius));
  background: var(--card); color: var(--fg); }
.search-row input:focus { outline: 3px solid var(--primary); outline-offset: 1px; }
.r-list { display: grid; gap: 14px; margin-bottom: 56px; }
.r-card { display: grid; grid-template-columns: 150px 1fr auto; gap: 18px; align-items: center; }
.r-img { height: 104px; border-radius: calc(var(--radius) * .6);
  background: linear-gradient(135deg, var(--secondary), var(--primary)); opacity: .85; }
.r-top { display: flex; align-items: baseline; gap: 10px; }
.r-top b { font-size: 15.5px; }
.r-score { font-family: 'IBM Plex Mono', monospace; font-weight: 600; color: var(--accent); }
.r-info small { color: var(--muted); font-size: 12.5px; }
.r-tags { margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap; }
.r-tag { font-size: 11.5px; border: 1.5px solid var(--border); border-radius: 999px; padding: 1px 10px; color: var(--muted); }
.r-side { text-align: right; display: grid; gap: 8px; justify-items: end; }
.r-price { font-family: 'IBM Plex Mono', monospace; font-size: 20px; font-weight: 600; }
.r-price span { font-size: 12px; color: var(--muted); }
@media (max-width: 860px) { .search-row { grid-template-columns: 1fr; } .r-card { grid-template-columns: 1fr; } }
'''

def article_body(p, col):
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">订阅更新</a>
</div></header>
<main class="container">
  <article class="art">
    <p class="doc-meta" style="justify-content:flex-start;margin:38px 0 8px">2026-10-08 / 长读 / 约 9 分钟 / 作者 台风眼</p>
    <h1 class="art-h">慢下来之后，城市开始向你显影</h1>
    <p class="art-sub">当我们不再赶时间，街道的细节才逐一浮现：门牌的字迹、修鞋摊的胶水味、傍晚六点的光。</p>
    <p>通勤者看到的城市是线条：两点之间的最短路径。而步行者看到的是表面：墙皮的年代、招牌的层次、树影在下午四点斜过巷口的精确角度。</p>
    <blockquote>速度不只节省时间，它也删掉内容。你走得越快，看见的越少。</blockquote>
    <p>过去三个月，我们沿着老城区的六条街做了慢速行走记录。结论出乎意料：让人愿意停下来的不是"景点"，而是连续的、可以阅读的沿街面——有橱窗、有台阶、有可以坐的边角。</p>
    <p>这份记录后来变成了一份给街区的小建议，附在文末，欢迎取用。</p>
  </article>
  <section class="rel">
    <h2 class="section-h">继续读 <small>READ NEXT</small></h2>
    <div class="rel-list">
      <a href="#" class="rel-item card"><b>门牌考：一条街的名字史</b><small>12 分钟 / 考据</small></a>
      <a href="#" class="rel-item card"><b>修鞋摊观察笔记</b><small>7 分钟 / 田野</small></a>
      <a href="#" class="rel-item card"><b>傍晚六点的光线地图</b><small>9 分钟 / 摄影</small></a>
    </div>
  </section>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__BOLT__', BOLT)

ARTICLE_CSS = SHARED_LAYOUT_CSS + '''
.art { max-width: 680px; }
.art-h { font-size: clamp(28px, 4.4vw, 42px); font-weight: 800; line-height: 1.25; margin-bottom: 10px; }
.art-sub { font-size: 16.5px; color: var(--muted); margin-bottom: 24px; }
.art p { font-size: 16px; margin-bottom: 18px; }
.art blockquote { border-left: 4px solid var(--primary); padding: 6px 0 6px 18px;
  font-size: 17px; font-weight: 600; margin: 26px 0; color: var(--primary); }
.rel { margin: 30px 0 60px; }
.rel-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.rel-item { text-decoration: none; color: inherit; }
.rel-item b { font-size: 14.5px; display: block; margin-bottom: 6px; }
.rel-item small { font-size: 12px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }
.rel-item:hover { transform: translateY(-3px); }
@media (max-width: 860px) { .rel-list { grid-template-columns: 1fr; } }
'''



def community_body(p, col):
    boards = ''.join('<a href="#" class="bd-row card"><span class="bd-ico" aria-hidden="true">'
        '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>'
        '<div class="bd-info"><b>%s</b><small>%s</small></div>'
        '<div class="bd-meta"><span>%s 主题</span><span>最新 %s</span></div></a>' % (n, d, cnt, last) for
        n, d, cnt, last in [('新人报到', '先读版规再发帖', '2.1k', '3 分钟前'),
        ('项目互助', '卡住了就来问', '8.7k', '12 分钟前'), ('周五线上局', '语音房常开', '634', '1 小时前'),
        ('二手闲置', '社群内自循环', '1.4k', '2 小时前'), ('公告与投票', '规则在这里定', '89', '昨天')])
    hot = ''.join('<a href="#" class="ht-row"><span class="ht-tag">%s</span><b>%s</b><span class="ht-meta">%s 回复 / %s</span></a>'
        % (t, ttl, rep, tm) for t, ttl, rep, tm in [('置顶', '社区公约 v3：关于友善与不杠', '214', '置顶'),
        ('热', '第一次自己做完了整个项目，来交作业', '96', '40 分钟前'), ('讨论', '你们都在用什么做笔记', '183', '2 小时前'),
        ('求助', '这个报错卡了我两天，救命', '31', '3 小时前')])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">发主题</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:30px 0 6px">注册成员 12,408 / 本周新主题 341 / 全站友善度 98%</p>
  <h1 class="cm-h">__PT__</h1>
  <div class="cm-grid">
    <section>
      <h2 class="section-h">板块 <small>BOARDS</small></h2>
      <div class="bd-list">__BOARDS__</div>
    </section>
    <section>
      <h2 class="section-h">今日热帖 <small>TRENDING</small></h2>
      <div class="ht-list card">__HOT__</div>
      <div class="cm-side card"><b>社区守则</b><p>先搜索再提问；给人答案时给原因；不接受任何人身攻击。三次警告后静默一周。</p></div>
    </section>
  </div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__BOARDS__', boards).replace('__HOT__', hot).replace('__BOLT__', BOLT)

COMMUNITY_CSS = SHARED_LAYOUT_CSS + """
.cm-h { font-size: clamp(26px, 4vw, 38px); font-weight: 800; margin-bottom: 20px; }
.cm-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; margin-bottom: 56px; }
.bd-list { display: grid; gap: 10px; }
.bd-row { display: flex; align-items: center; gap: 14px; text-decoration: none; color: inherit; padding: 14px 16px; }
.bd-ico { width: 40px; height: 40px; flex: none; border-radius: calc(var(--radius) * .6);
  background: var(--muted); color: var(--fg); display: grid; place-items: center; }
.bd-info { flex: 1; }
.bd-info b { font-size: 15px; display: block; }
.bd-info small { font-size: 12.5px; color: var(--muted); }
.bd-meta { display: grid; gap: 2px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; color: var(--muted); }
.ht-list { display: grid; margin-bottom: 16px; }
.ht-row { display: flex; align-items: baseline; gap: 10px; padding: 11px 16px;
  border-bottom: 1px solid var(--border); text-decoration: none; color: inherit; }
.ht-row:last-child { border-bottom: none; }
.ht-tag { font-size: 10.5px; font-weight: 700; padding: 1px 8px; border-radius: 3px;
  background: var(--accent); color: #fff; flex: none; }
.ht-row b { font-size: 13.5px; font-weight: 600; }
.ht-meta { margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--muted); white-space: nowrap; }
.cm-side b { font-size: 14px; }
.cm-side p { font-size: 13px; color: var(--muted); margin-top: 6px; }
@media (max-width: 900px) { .cm-grid { grid-template-columns: 1fr; } }
"""

def profile_body(p, col):
    works = ''.join('<a href="#" class="pw card"><div class="pw-img" aria-hidden="true"></div><b>%s</b><small>%s</small></a>'
        % (n, t) for n, t in [('山雾民宿 / 全案', '品牌 / 空间'), ('拾光胶片 / 小程序', '产品设计'),
        ('城市字体计划', '实验项目'), ('独立咖啡馆 / VI', '视觉识别')])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">联系合作</a>
</div></header>
<main class="container">
  <section class="pf-head card">
    <div class="pf-avatar" aria-hidden="true"></div>
    <div class="pf-info">
      <p class="doc-meta" style="justify-content:flex-start;margin-bottom:8px">接单中 / 回复 &lt; 12h / 时区 GMT+8</p>
      <h1>阿雀 <small>独立设计师</small></h1>
      <p class="pf-bio">做品牌与产品六年，喜欢小而确定的项目：一家店、一个 app、一次认真的改版。目前正在排 12 月档期。</p>
      <div class="pf-tags"><span>品牌识别</span><span>产品设计</span><span>插画</span><span>洽谈到落地</span></div>
      <div class="pf-nums"><div><b>86</b><span>项目交付</span></div><div><b>4.9</b><span>客户评分</span></div><div><b>6年</b><span>独立执业</span></div></div>
    </div>
  </section>
  <h2 class="section-h">精选作品 <small>SELECTED WORK</small></h2>
  <div class="pw-grid">__WORKS__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__WORKS__', works).replace('__BOLT__', BOLT)

PROFILE_CSS = SHARED_LAYOUT_CSS + """
.pf-head { display: grid; grid-template-columns: 130px 1fr; gap: 26px; padding: 28px; margin-top: 30px; }
.pf-avatar { border-radius: 50%; background: conic-gradient(from 200deg, var(--primary), var(--secondary), var(--accent), var(--primary)); }
.pf-info h1 { font-size: clamp(26px, 3.6vw, 36px); margin-bottom: 10px; }
.pf-info h1 small { font-size: 15px; color: var(--muted); font-weight: 500; margin-left: 10px; }
.pf-bio { font-size: 14.5px; color: var(--muted); max-width: 520px; margin-bottom: 14px; }
.pf-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.pf-tags span { font-size: 12px; border: 1.5px solid var(--border); border-radius: 999px; padding: 3px 12px; }
.pf-nums { display: flex; gap: 34px; }
.pf-nums b { font-family: 'IBM Plex Mono', monospace; font-size: 24px; display: block; color: var(--primary); }
.pf-nums span { font-size: 12px; color: var(--muted); }
.pw-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 56px; }
.pw { text-decoration: none; color: inherit; }
.pw-img { height: 110px; border-radius: calc(var(--radius) * .6); margin-bottom: 10px;
  background: linear-gradient(135deg, var(--secondary), var(--primary)); opacity: .85; }
.pw b { font-size: 14px; display: block; }
.pw small { font-size: 12px; color: var(--muted); }
@media (max-width: 980px) { .pw-grid { grid-template-columns: repeat(2, 1fr); } .pf-head { grid-template-columns: 1fr; } }
"""

def kanban_body(p, col):
    cols = [
        ('待处理', 'TODO', [('客户访谈纪要整理', '标签：研究 / 今天'), ('Q4 落地页文案 v2', '标签：文案 / 周四'), ('报销单', '标签：行政 / 周五')]),
        ('进行中', 'DOING', [('导航改版可用性测试', '设计 / 6 人访谈 / 明天'), ('API 文档补齐', '开发 / 周四')]),
        ('已发布', 'DONE', [('注册流短信验证', '已上线 / 10-02'), ('数据看板 v1', '已上线 / 09-28'), ('客服话术库', '已上线 / 09-20')]),
    ]
    col_html = ''.join('<section class="kb-col"><h3 class="kb-h">%s <small>%s / %d</small></h3>%s</section>'
        % (name, en, len(items), ''.join('<article class="kb-card card"><b>%s</b><small>%s</small></article>' % it for it in items))
        for name, en, items in cols)
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">新建任务</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:30px 0 6px">本周迭代 / 10-06 → 10-12 / 负责人 4 人 / 站会每天 10:00</p>
  <h1 class="kb-title">迭代看板</h1>
  <div class="kb-grid">__COLS__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__COLS__', col_html).replace('__BOLT__', BOLT)

KANBAN_CSS = SHARED_LAYOUT_CSS + """
.kb-title { font-size: clamp(26px, 4vw, 36px); font-weight: 800; margin-bottom: 22px; }
.kb-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 56px; align-items: start; }
.kb-h { font-size: 14px; font-weight: 800; letter-spacing: .08em; padding: 4px 2px 10px;
  display: flex; justify-content: space-between; align-items: baseline; }
.kb-h small { font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; color: var(--muted); font-weight: 400; }
.kb-col { display: grid; gap: 10px; }
.kb-card { padding: 14px 16px; }
.kb-card b { font-size: 14px; display: block; margin-bottom: 4px; }
.kb-card small { font-size: 12px; color: var(--muted); }
@media (max-width: 900px) { .kb-grid { grid-template-columns: 1fr; } }
"""



# ---------- 变体层：同布局按产品轮换文案，避免"只换色" ----------
PRICING_TIERS = [
    [('基础', '起步', '个人'), ('专业', '成长', '工作室'), ('团队', '规模', '企业')],
]
PRICING_PRICE = [('¥0', '¥39', '¥99'), ('¥0', '¥29', '¥79'), ('¥0', '¥49', '¥129')]
PRICING_FEAT_POOL = {
    'dev': ['核心功能', '私有仓库', 'CI 流水线', '成员席位', 'API 限额', '审计日志', '专属支持', 'SLA 保障', '私有部署'],
    'fin': ['账户接入', '自动对账', '风控规则', '专属客户经理', 'API 对接', '多币种', 'SLA 保障', '合规导出', '私有部署'],
    'edu': ['入门课程', '全部课程', '学员席位', '作业批改', '证书颁发', '学情分析', '督学服务', '直播课时', '私有部署'],
    'mkt': ['基础工具', '项目数扩容', '品牌工作区', '数据报表', 'A/B 测试', '代理协作', '投放接口', '优先支持', '私有部署'],
    'gen': ['核心功能', '成员席位', '高级分析', '自定义域', '优先支持', '审计日志', 'SLA 保障', '开放 API', '私有部署'],
}

def _feat_pool(p):
    t = (p['Product Type'] + ' ' + p['Keywords']).lower()
    if any(k in t for k in ['developer', 'ide', 'api', 'coding', 'no-code', 'open source', 'devtool', 'hosting']):
        return PRICING_FEAT_POOL['dev']
    if any(k in t for k in ['bank', 'fin', 'insur', 'pay', 'billing', 'invoice', 'crypto', 'legal', 'account']):
        return PRICING_FEAT_POOL['fin']
    if any(k in t for k in ['course', 'learn', 'educat', 'lms', 'bootcamp', 'study', 'school', 'academic']):
        return PRICING_FEAT_POOL['edu']
    if any(k in t for k in ['market', 'agency', 'seo', 'brand', 'social', 'content', 'newsletter', 'testimonial']):
        return PRICING_FEAT_POOL['mkt']
    return PRICING_FEAT_POOL['gen']

def pricing_body(p, col):  # noqa: F811
    v = int(p['No']) % 3
    tiers = PRICING_TIERS[0][v] if False else [PRICING_TIERS[0][0][v], PRICING_TIERS[0][1][v], PRICING_TIERS[0][2][v]]
    prices = PRICING_PRICE[v]
    pool = _feat_pool(p)
    def feats(n_on):
        return ''.join('<li%s>%s %s</li>' % (' class="off"' if i >= n_on else '',
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>' if i < n_on else
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>', f)
            for i, f in enumerate(pool[:6]))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">免费开始</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:center;margin:44px 0 6px">按月订阅 / 随时取消 / 年付省两个月</p>
  <h1 class="pr-h">选择适合你的方案</h1>
  <div class="pr-grid">
    <section class="card pr-tier">
      <h3>__T1__</h3><p class="pr-price">__P1__<span>/月</span></p>
      <ul class="pr-feats">__F1__</ul>
      <a class="btn" href="#">直接开始</a>
    </section>
    <section class="card pr-tier hot">
      <span class="pr-badge">最多人选</span>
      <h3>__T2__</h3><p class="pr-price">__P2__<span>/月</span></p>
      <ul class="pr-feats">__F2__</ul>
      <a class="btn btn-primary" href="#">开始 14 天试用</a>
    </section>
    <section class="card pr-tier">
      <h3>__T3__</h3><p class="pr-price">__P3__<span>/月</span></p>
      <ul class="pr-feats">__F3__</ul>
      <a class="btn" href="#">联系开通</a>
    </section>
  </div>
  <section class="pr-faq">
    <h2 class="section-h">常见问题 <small>FAQ</small></h2>
    <details><summary>可以随时换方案或取消吗？</summary><p>可以，升级立即生效，降级与取消在当前计费周期结束时生效，不收违约金。</p></details>
    <details><summary>发票怎么开？</summary><p>支持增值税普通发票与专票，在账单中心自助申请，1-3 个工作日开出。</p></details>
  </section>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__T1__', tiers[0]).replace('__T2__', tiers[1]).replace('__T3__', tiers[2]) \
    .replace('__P1__', prices[0]).replace('__P2__', prices[1]).replace('__P3__', prices[2]) \
    .replace('__F1__', feats(2)).replace('__F2__', feats(4)).replace('__F3__', feats(6)) \
    .replace('__BOLT__', BOLT)

ARTICLES = [
    dict(tag='2026-10-08 / 长读 / 约 9 分钟 / 作者 台风眼',
         h='慢下来之后，城市开始向你显影',
         sub='当我们不再赶时间，街道的细节才逐一浮现：门牌的字迹、修鞋摊的胶水味、傍晚六点的光。',
         ps=['通勤者看到的城市是线条：两点之间的最短路径。而步行者看到的是表面：墙皮的年代、招牌的层次、树影在下午四点斜过巷口的精确角度。',
             '过去三个月，我们沿着老城区的六条街做了慢速行走记录。结论出乎意料：让人愿意停下来的不是"景点"，而是连续的、可以阅读的沿街面。',
             '这份记录后来变成了一份给街区的小建议，附在文末，欢迎取用。'],
         q='速度不只节省时间，它也删掉内容。你走得越快，看见的越少。',
         rel=[('门牌考：一条街的名字史', '12 分钟 / 考据'), ('修鞋摊观察笔记', '7 分钟 / 田野'), ('傍晚六点的光线地图', '9 分钟 / 摄影')]),
    dict(tag='2026-10-02 / 实操 / 约 6 分钟 / 作者 一杯冰美式',
         h='我们把周报砍掉了一半，效率反而上来了',
         sub='一次为期六周的实验：去掉所有"汇报感"的字段，只留三个问题。团队的反悔率是零。',
         ps=['周报的问题不在"周"，在"报"。一旦写作对象变成上级，内容就会自动表演勤奋。',
             '新格式只有三问：本周最重要的结果是什么、哪里卡住了、下周要动哪件事。写完不超过十分钟，读完不超过两分钟。',
             '六周后回头看，会议少了三成，而进度的透明度反而更高——因为大家终于写的是事实。'],
         q='汇报的目的是同步事实，不是证明忙碌。',
         rel=[('我们如何开一个 25 分钟的会', '5 分钟 / 效率'), ('文档模板的三条军规', '8 分钟 / 方法'), ('异步协作的第一年', '14 分钟 / 长读')]),
    dict(tag='2026-09-25 / 随笔 / 约 5 分钟 / 作者 夜航西飞',
         h='凌晨四点的电台，救过多少个睡不着的人',
         sub='主持人老麦守了十九年午夜档。他说这行的门槛很低：愿意在别人都睡着的时刻醒着。',
         ps=['午夜电台的听众画像很模糊：加班回家的、喂奶的、刚吵完架的、单纯失眠的。他们有一个共同点——不想被问候"您好"。',
             '老麦的节目没有固定歌单，只有一条规则：一点以后不放快歌。读信环节最受欢迎，读的多是没人回的信。',
             '有天一个听众打进来说，考研二战失败，在楼顶。老麦放了首很老的歌，然后念了节目开播第一天的日记。那个人后来每年寄一张明信片。'],
         q='深夜的声音不需要解决方案，只需要在场。',
         rel=[('声音档案：城市的午夜频率', '10 分钟 / 记录'), ('做电台的第九年', '11 分钟 / 访谈'), ('一份给失眠者的歌单', '6 分钟 / 歌单')]),
]

def article_body(p, col):  # noqa: F811
    a = ARTICLES[int(p['No']) % len(ARTICLES)]
    ps = ''.join('<p>%s</p>' % x for x in a['ps'])
    rel = ''.join('<a href="#" class="rel-item card"><b>%s</b><small>%s</small></a>' % r for r in a['rel'])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">订阅更新</a>
</div></header>
<main class="container">
  <article class="art">
    <p class="doc-meta" style="justify-content:flex-start;margin:38px 0 8px">__TAG__</p>
    <h1 class="art-h">__H__</h1>
    <p class="art-sub">__SUB__</p>
    __PS__
    <blockquote>__Q__</blockquote>
    __TAIL__
  </article>
  <section class="rel">
    <h2 class="section-h">继续读 <small>READ NEXT</small></h2>
    <div class="rel-list">__REL__</div>
  </section>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__TAG__', a['tag']).replace('__H__', a['h']).replace('__SUB__', a['sub']) \
    .replace('__PS__', ps).replace('__Q__', a['q']) \
    .replace('__TAIL__', ps.split('</p>')[0] + '</p>' if False else '<p>全文完。</p>') \
    .replace('__REL__', rel).replace('__BOLT__', BOLT)

BOOKING_SETS = [
    [('初次到访 / 60 分钟', '含评估与方案沟通', '198'), ('标准护理 / 45 分钟', '常规项目', '158'), ('深度疗程 / 90 分钟', '含专项与随访', '328')],
    [('首次咨询 / 50 分钟', '含现状评估', '300'), ('常规咨询 / 45 分钟', '按疗程进行', '240'), ('联合咨询 / 80 分钟', '两位咨询师同行', '460')],
]

def booking_body(p, col):  # noqa: F811
    svcs = ''.join('<label class="svc card"><input type="radio" name="svc" aria-label="%s"><span class="svc-dot" aria-hidden="true"></span><b>%s</b><small>%s / ¥%s</small></label>'
        % (n, n, d, pr) for n, d, pr in BOOKING_SETS[int(p['No']) % 2])
    slots = ''.join('<button class="fchip%s" type="button">%s</button>' % (' on' if i == 1 else '', t)
        for i, t in enumerate(['今天 14:00', '今天 15:00', '今天 16:00', '明天 10:00', '明天 11:30']))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">登录</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:34px 0 6px">线上预约 / 到店签到 / 提前 2 小时可改期</p>
  <h1 class="bk-h">预约一个时段</h1>
  <h2 class="section-h">选择项目 <small>SERVICE</small></h2>
  <div class="svc-row">__SVCS__</div>
  <h2 class="section-h">选择时段 <small>TIME SLOT</small></h2>
  <div class="chips-row">__SLOTS__</div>
  <h2 class="section-h">你的信息 <small>CONTACT</small></h2>
  <form class="bk-form card" onsubmit="return false">
    <label>姓名<input type="text" placeholder="怎么称呼你" required></label>
    <label>手机号<input type="tel" placeholder="用于到店确认" required></label>
    <label>备注<textarea rows="3" placeholder="过敏史、偏好或想聊的（选填）"></textarea></label>
    <button class="btn btn-primary" type="submit">确认预约</button>
  </form>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__SVCS__', svcs).replace('__SLOTS__', slots).replace('__BOLT__', BOLT)

SHOP_SETS = [
    [('手工陶瓷杯', '128'), ('帆布托特包', '98'), ('大豆香薰蜡烛', '158'), ('美利奴羊毛袜', '76'),
     ('车线装笔记本', '58'), ('黄铜书立', '188'), ('手冲滤架', '216'), ('亚麻桌布', '168')],
    ['生活杂货', '文具', '新品', '热卖'],
]
SHOP_SETS_B = [
    [('机械键盘 / 68 键', '399'), ('金属笔筒', '89'), ('显示器支架', '259'), ('降噪耳塞', '129'),
     ('桌垫 / 植鞣革', '179'), ('理线器套装', '59'), ('桌面小夜灯', '99'), ('升降笔记本架', '189')],
    ['数码桌面', '办公', '新品', '热卖'],
]

def shop_body(p, col):  # noqa: F811
    goods_set, cats = (SHOP_SETS, SHOP_SETS_B)[int(p['No']) % 2][0], (SHOP_SETS, SHOP_SETS_B)[int(p['No']) % 2][1]
    goods = ''.join('<article class="g-card"><div class="g-img" aria-hidden="true"></div>'
        '<h3>%s</h3><p class="g-price">¥%s</p>'
        '<button class="g-add" type="button" aria-label="加入购物车：%s"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></button></article>'
        % (n, pr, n) for n, pr in goods_set)
    chips = ''.join('<button class="fchip%s" type="button">%s</button>' % (' on' if i == 0 else '', t)
                    for i, t in enumerate(['全部'] + cats))
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">购物车 (3)</a>
</div></header>
<div class="promo-bar">限时：全场满 ¥199 免运费 / 新客首单 9 折</div>
<main class="container">
  <div class="chips-row" role="group" aria-label="商品筛选">__CHIPS__</div>
  <h2 class="section-h">本周选品 <small>WEEKLY PICKS</small></h2>
  <div class="g-grid">__GOODS__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__CHIPS__', chips).replace('__GOODS__', goods).replace('__BOLT__', BOLT)

PRODUCT_LAYOUTS = {
    'shop': (shop_body, lambda: SHOP_CSS), 'pricing': (pricing_body, lambda: PRICING_CSS),
    'menu': (menu_body, lambda: MENU_CSS), 'media': (media_body, lambda: MEDIA_CSS),
    'booking': (booking_body, lambda: BOOKING_CSS),
    'listing': (listing_body, lambda: LISTING_CSS), 'article': (article_body, lambda: ARTICLE_CSS),
    'community': (community_body, lambda: COMMUNITY_CSS),
    'profile': (profile_body, lambda: PROFILE_CSS),
    'kanban': (kanban_body, lambda: KANBAN_CSS),
}

def app_theme_for(p):
    """phone/dashboard 布局复用现有模板所需的主题 dict。"""
    return dict(brand=p['Product Type'], en=p['Product Type'],
        meta=p['Keywords'].strip()[:60] or 'OFFICIAL COMBO',
        hero=p['Product Type'], sub=p['Key Considerations'].strip(),
        blocks=[('记录', '一键记录，自动归档与同步。'), ('提醒', '按时提醒，不打扰也不遗漏。'), ('统计', '趋势一目了然，支持导出。')],
        stats=[('4.8', '应用评分'), ('10M+', '累计下载'), ('免费', '核心功能')],
        cta1='立即开始', cta2='了解更多',
        foot='官方推荐组合 No.%s' % p['No'],
        metaphor='通用应用骨架：记录 / 提醒 / 统计')

def menu_body_fix(p, col):
    items = [('手冲 / 耶加雪菲', '柑橘与花香，浅焙', '32'), ('澳白', '双份浓缩，奶厚 5mm', '28'),
             ('冷萃 / 冰博克', '冷藏 16 小时，奶香浓', '34'), ('煎茶拿铁', '石川县煎茶，微甜', '30'),
             ('可颂', '法国黄油 27 层', '22'), ('碱水结', '碱水重口，配啤酒刚好', '18'),
             ('巴斯克蛋糕', '焦壳流心，每日限量', '32'), ('肉桂卷', '现烤出炉 11:00 / 16:00', '24')]
    def render(lst):
        return ''.join('<div class="m-item"><div class="m-name"><b>%s</b><small>%s</small></div>'
                       '<span class="m-dots" aria-hidden="true"></span><span class="m-price">¥%s</span></div>' % it for it in lst)
    return menu_body.__wrapped__(p, col) if hasattr(menu_body, '__wrapped__') else _menu_render(p, col, render(items[:4]), render(items[4:]))

def _menu_render(p, col, i1, i2):
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>__PT__</a>
  __NAV__
  <a class="btn btn-primary" href="#">订位</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:30px 0 4px">今日营业 08:00 – 22:00 / 最后点单 21:30 / 周一店休</p>
  <h1 class="mn-h">__PT__</h1>
  <p class="mn-sub">豆子每周二到店，烘焙度按批次微调；菜单随季节换三分之一。</p>
  <h2 class="section-h">本季饮品 <small>DRINKS</small></h2>
  <div class="m-list">__I1__</div>
  <h2 class="section-h">现烤烘焙 <small>BAKERY</small></h2>
  <div class="m-list">__I2__</div>
</main>
<footer>__PT__ 成品模板 / 官方推荐组合 No.__NO__ / <a href="../style-catalog.html">返回目录</a></footer>''' \
    .replace('__PT__', html.escape(p['Product Type'])).replace('__NAV__', NAV).replace('__NO__', p['No']) \
    .replace('__I1__', i1).replace('__I2__', i2).replace('__BOLT__', BOLT)

# 用修复版替换 menu_body
def menu_body(p, col):  # noqa: F811
    items = [('手冲 / 耶加雪菲', '柑橘与花香，浅焙', '32'), ('澳白', '双份浓缩，奶厚 5mm', '28'),
             ('冷萃 / 冰博克', '冷藏 16 小时，奶香浓', '34'), ('煎茶拿铁', '石川县煎茶，微甜', '30'),
             ('可颂', '法国黄油 27 层', '22'), ('碱水结', '碱水重口，配啤酒刚好', '18'),
             ('巴斯克蛋糕', '焦壳流心，每日限量', '32'), ('肉桂卷', '现烤出炉 11:00 / 16:00', '24')]
    def render(lst):
        return ''.join('<div class="m-item"><div class="m-name"><b>%s</b><small>%s</small></div>'
                       '<span class="m-dots" aria-hidden="true"></span><span class="m-price">¥%s</span></div>' % it for it in lst)
    return _menu_render(p, col, render(items[:4]), render(items[4:]))

# ---------- 产品样板独有形态：设计规格单（Spec Sheet） ----------
TOKENS = [('Primary', '主色'), ('On Primary', '主色文字'), ('Secondary', '辅色'),
          ('Accent', '强调色'), ('Background', '页面底'), ('Foreground', '正文'),
          ('Card', '卡面'), ('Muted', '弱化面'), ('Border', '边框'), ('Ring', '焦点环')]

def product_spec_body(p, col):
    toks = ''.join(
        '<div class="tok"><span class="chip" style="background:%s;%s"></span>'
        '<span class="tok-name">%s <em>%s</em></span><code>%s</code></div>' % (
            col[k], ('border:1.5px solid var(--border)' if (not re.match(r'^#[0-9A-Fa-f]{3,8}$', col[k], re.I)) or yiq(col[k]) > 235 or col[k].upper() == '#FFFFFF' else ''),
            k, zh, col[k]) for k, zh in TOKENS)
    recs = ''.join('<dt>%s</dt><dd>%s</dd>' % (dt, html.escape(dd)) for dt, dd in [
        ('主推风格', p['Primary Style Recommendation'].strip()),
        ('次选风格', p['Secondary Styles'].strip()),
        ('落地结构', p['Landing Page Pattern'].strip()),
        ('仪表盘风格', p['Dashboard Style (if applicable)'].strip() or '—'),
        ('色板方向', p['Color Palette Focus'].strip()),
        ('关键考量', p['Key Considerations'].strip()),
    ])
    return '''<header class="topbar"><div class="container topbar-inner">
  <a class="logo" href="#"><span class="logo-mark">__BOLT__</span>No.__NO__ / __PT__</a>
  __NAV__
  <a class="btn btn-primary" href="../style-catalog.html">返回风格目录</a>
</div></header>
<main class="container">
  <p class="doc-meta" style="justify-content:flex-start;margin:30px 0 6px">__KW__</p>
  <h1 class="spec-title">__PT__</h1>
  <p class="spec-sub">__FOCUS__ —— __KC__</p>
  <div class="spec-grid">
    <section class="spec-card">
      <h2 class="spec-h">官方色板 <span class="spec-en">colors.csv</span></h2>
      <div class="tok-list">__TOKENS__</div>
      <p class="spec-note">__NOTES__</p>
    </section>
    <section class="spec-card">
      <h2 class="spec-h">官方推荐 <span class="spec-en">products.csv</span></h2>
      <dl class="recs">__RECS__</dl>
    </section>
  </div>
  <section class="spec-card comp-card">
    <h2 class="spec-h">色板组件预览 <span class="spec-en">live tokens</span></h2>
    <div class="comp-row">
      <button class="btn btn-primary" type="button">主按钮</button>
      <button class="btn" type="button">次按钮</button>
      <span class="pill-demo">标签 Label</span>
      <span class="pill-demo alt">成功 92%</span>
      <input class="input-demo" type="text" placeholder="输入框占位文本" aria-label="组件预览输入框">
      <div class="bar-demo" role="img" aria-label="进度条约 70%"><i style="width:70%"></i></div>
      <span class="switch-demo" role="img" aria-label="开关开"><i></i></span>
    </div>
  </section>
</main>
<footer>官方推荐组合 No.__NO__ / ui-ux-pro-max products.csv + colors.csv 原文 / <a href="../style-catalog.html">返回风格目录</a></footer>''' \
    .replace('__NO__', p['No']).replace('__PT__', html.escape(p['Product Type'])) \
    .replace('__NAV__', NAV) \
    .replace('__KW__', html.escape(p['Keywords'].strip())) \
    .replace('__FOCUS__', html.escape(p['Color Palette Focus'].strip())) \
    .replace('__KC__', html.escape(p['Key Considerations'].strip())) \
    .replace('__TOKENS__', toks).replace('__RECS__', recs) \
    .replace('__NOTES__', html.escape(col.get('Notes', '').strip())) \
    .replace('__BOLT__', BOLT)

def product_spec_css():
    return '''.spec-title { font-size: clamp(30px, 4.6vw, 46px); font-weight: 800; line-height: 1.15; margin-bottom: 10px; }
.spec-sub { font-size: 15px; color: var(--muted); margin-bottom: 26px; max-width: 640px; }
.spec-grid { display: grid; grid-template-columns: 1.15fr 1fr; gap: 20px; margin-bottom: 20px; }
.spec-card { background: var(--card); border: __BORDER__; border-radius: var(--radius);
  box-shadow: __SHADOW__; padding: 24px; }
.spec-h { font-size: 15px; font-weight: 800; letter-spacing: .06em; margin-bottom: 16px;
  border-bottom: 2px solid var(--border); padding-bottom: 8px; }
.spec-en { font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; color: var(--muted);
  font-weight: 400; letter-spacing: .1em; margin-left: 8px; }
.tok { display: flex; align-items: center; gap: 12px; padding: 7px 0;
  border-bottom: 1px dotted var(--border); }
.tok:last-of-type { border-bottom: none; }
.tok .chip { width: 44px; height: 32px; border-radius: calc(var(--radius) * .5); flex: none; }
.tok-name { font-size: 13px; font-weight: 600; }
.tok-name em { font-style: normal; color: var(--muted); font-size: 11.5px; margin-left: 4px; }
.tok code { margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--muted); }
.spec-note { margin-top: 12px; font-size: 12px; color: var(--muted);
  font-family: 'IBM Plex Mono', monospace; }
.recs { display: grid; gap: 2px; }
.recs dt { font-size: 11.5px; color: var(--muted); letter-spacing: .14em; margin-top: 12px; }
.recs dt:first-child { margin-top: 0; }
.recs dd { font-size: 14.5px; font-weight: 600; line-height: 1.5; }
.recs dt:first-child + dd { font-size: 19px; font-weight: 800; color: var(--primary); }
.comp-card { margin-bottom: 40px; }
.comp-row { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }
.pill-demo { font-size: 12.5px; font-weight: 600; padding: 4px 14px; border-radius: 999px;
  background: var(--secondary); color: var(--fg); border: 1.5px solid var(--border); }
.pill-demo.alt { background: var(--accent); color: #fff; border-color: transparent; }
.input-demo { font: inherit; font-size: 13.5px; padding: 10px 14px; border-radius: calc(var(--btn-radius));
  border: 1.5px solid var(--border); background: var(--bg); color: var(--fg); min-width: 190px; }
.input-demo:focus { outline: 3px solid var(--ring, var(--primary)); outline-offset: 1px; }
.bar-demo { width: 170px; height: 10px; border-radius: 999px; background: var(--muted); overflow: hidden; }
.bar-demo i { display: block; height: 100%; background: var(--primary); border-radius: 999px; }
.switch-demo { width: 46px; height: 26px; border-radius: 999px; background: var(--primary);
  display: inline-flex; align-items: center; padding: 3px; }
.switch-demo i { width: 20px; height: 20px; border-radius: 50%; background: #fff; margin-left: auto; }
.doc-meta { font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: var(--muted);
  display: flex; gap: 14px; flex-wrap: wrap; }
@media (max-width: 860px) { .spec-grid { grid-template-columns: 1fr; } }
@media (max-width: 768px) { nav { display: none; } }'''



# ---------- 落地页结构样板：landing.csv 官方结构 → 真实成品页 ----------
SRC_LANDING = r'E:\sklls\ui-ux-pro-max-skill\.claude\skills\ui-ux-pro-max\data\landing.csv'
OUT_LDIR = os.path.join(BASE, 'pattern-demos')

FAMILY_REP = {
    'swiss': 'Minimalism & Swiss Style', 'brutal': 'Brutalism', 'glass': 'Glassmorphism',
    'paper': 'Vintage Analog / Retro Film', 'aurora': 'Aurora UI', 'memphis': 'Memphis Design',
    'neumorph': 'Neumorphism', 'organic': 'Organic Biophilic', 'cyber': 'Cyberpunk UI',
    'vaporwave': 'Vaporwave', '3d': '3D & Hyperrealism', 'data': 'Data-Dense Dashboard',
    'kinetic': 'Kinetic Typography', 'm3': 'Material 3 Expressive (Mobile)', 'bauhaus': 'Bauhaus (包豪斯)',
    'soft': 'Soft UI Evolution', 'clay': 'Claymorphism', 'skeuo': 'Skeuomorphism',
    'a11y': 'Accessible & Ethical', 'dark': 'Dark Mode (OLED)', 'pixel': 'Pixel Art',
    'micro': 'Micro-interactions', 'vibrant': 'Vibrant & Block-based',
    'chaos': 'Gen Z Chaos / Maximalism', 'fluent': 'Fluent 2',
}
FAM_CYCLE = ['swiss', 'brutal', 'glass', 'paper', 'aurora', 'memphis', 'neumorph', 'organic',
             'cyber', 'vaporwave', '3d', 'data', 'kinetic', 'm3', 'bauhaus', 'soft',
             'clay', 'skeuo', 'a11y', 'dark', 'pixel', 'micro', 'vibrant', 'chaos', 'fluent']

def load_landing():
    return list(csv.DictReader(open(SRC_LANDING, encoding='utf-8')))

SECTION_KEYS = [
    ('hero', 'hero'), ('video', 'video'), ('demo', 'video'), ('mockup', 'video'),
    ('feature', 'features'), ('testimonial', 'testi'), ('social proof', 'testi'), ('review', 'testi'),
    ('logo', 'logos'), ('comparison', 'compare'), ('pricing', 'pricing'), ('faq', 'faq'),
    ('gallery', 'gallery'), ('visual', 'gallery'), ('stat', 'stats'), ('metric', 'stats'),
    ('number', 'stats'), ('newsletter', 'newsletter'), ('email', 'newsletter'), ('signup', 'newsletter'),
    ('capture', 'newsletter'), ('chapter', 'story'), ('storytelling', 'story'), ('narrative', 'story'),
    ('journey', 'story'), ('timeline', 'story'), ('problem', 'problem'), ('value prop', 'value'),
    ('solution', 'value'), ('cta', 'cta'), ('footer', 'footer'),
]

def parse_sections(order):
    out = []
    for raw in order.split('>'):
        seg = raw.strip().lower()
        seg = re.sub(r'^[\d.\s]+', '', seg)
        if not seg: continue
        hit = 'value'  # 未识别的文本区块按 value 渲染
        for kw, comp in SECTION_KEYS:
            if kw in seg:
                hit = comp; break
        if comp == 'footer' and out and out[-1] == 'footer':
            continue
        out.append(hit if hit != 'footer' else 'footer')
    # 尾部若无 cta/footer，补 footer
    if not out or out[-1] != 'footer':
        out.append('footer')
    return out

TESTI_POOL = [
    ('流程终于跑顺了，交接成本几乎为零', '王琨 / 运营负责人'),
    ('第二周就看到数据变化，团队没人再喊麻烦', '李潇 / 市场总监'),
    ('客服量降了一半，答案反而更标准', '赵砚 / 客服主管'),
]
LOGO_POOL = ['晨钟文化', 'Nordlab', '拾光事务所', '山脊工作室', 'Bluebay', '远见集团']

def _sec(cls, inner, label=None):
    small = ' <small>%s</small>' % label if label else ''
    return '<section class="sec %s"><h2 class="section-h">%s%s</h2>%s</section>' % (cls, SECTION_TITLE.get(cls, cls), small, inner)

SECTION_TITLE = {'features': '核心能力', 'testi': '用户怎么说', 'video': '看看它怎么工作',
                 'stats': '数据说话', 'faq': '常见问题', 'compare': '和过去比一比',
                 'gallery': '一眼看全', 'logos': '他们在用', 'newsletter': '保持联系',
                 'story': '两步开始', 'problem': '你是不是也这样', 'value': '为什么是它'}

def render_section(kind, t, i):
    if kind == 'hero':
        return ('<section class="hero container"><p class="doc-meta">%s</p>'
                '<h1>%s</h1><p class="sub">%s</p>'
                '<div class="cta-row"><a class="btn btn-primary" href="#">%s</a>'
                '<a class="btn" href="#">%s</a></div></section>'
                % (html.escape(t['meta']), html.escape(t['hero']), html.escape(t['sub']),
                   html.escape(t['cta1']), html.escape(t['cta2'])))
    if kind == 'features':
        cards = ''.join('<article class="card"><div class="card-icon">%s</div><h3>%s</h3><p>%s</p></article>'
                        % (ic, html.escape(b[0]), html.escape(b[1]))
                        for ic, b in zip((ICON_SEARCH, ICON_CHAT, ICON_CHART), t['blocks']))
        return '<section class="container">%s</section>' % _sec('features', '<div class="grid3">%s</div>' % cards)
    if kind == 'stats':
        row = ''.join('<div class="card stat"><b>%s</b><span>%s</span></div>' % (html.escape(v), html.escape(k)) for v, k in t['stats'])
        return '<section class="container"><div class="grid3 stats-row">%s</div></section>' % row
    if kind == 'testi':
        ts = ''.join('<figure class="card tst"><div class="tst-ava" aria-hidden="true"></div>'
                     '<blockquote>「%s」</blockquote><figcaption>%s</figcaption></figure>'
                     % (q, who) for (q, who) in TESTI_POOL)
        return '<section class="container">%s</section>' % _sec('testi', '<div class="tst-grid">%s</div>' % ts)
    if kind == 'video':
        return ('<section class="container">%s</section>' % _sec('video',
                '<div class="vd card"><button class="vd-play" type="button" aria-label="播放演示视频">'
                '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>'
                '<span class="vd-dur">02:41 / 无声字幕版</span></div>'))
    if kind == 'faq':
        return ('<section class="container">%s</section>' % _sec('faq',
                '<div class="faq"><details open><summary>多久能上线？</summary><p>标准流程一周：两天接入、三天试跑、两天交接。</p></details>'
                '<details><summary>数据归谁？</summary><p>全部归你，随时可导出，我们不留副本。</p></details>'
                '<details><summary>怎么开始？</summary><p>留个联系方式，我们先看流程再谈方案，不推销。</p></details></div>'))
    if kind == 'compare':
        rows = ''.join('<tr><td>%s</td><td class="cp-us">%s</td><td class="cp-old">%s</td></tr>' % r for r in
                       [('排期', '自动排序', '手工表格'), ('跟进', '按画像提醒', '凭记忆'),
                        ('复盘', '全量留痕', '靠会议记录'), ('上手', '半天', '三周培训')])
        return ('<section class="container">%s</section>' % _sec('compare',
                '<div class="card cp card-pad"><table><thead><tr><th>环节</th><th>现在</th><th>以前</th></tr></thead>'
                '<tbody>%s</tbody></table></div>' % rows))
    if kind == 'gallery':
        gs = ''.join('<div class="gl-i" aria-hidden="true"></div>' for _ in range(4))
        return '<section class="container">%s</section>' % _sec('gallery', '<div class="gl-grid">%s</div>' % gs)
    if kind == 'logos':
        ls = ''.join('<span class="lg">%s</span>' % x for x in LOGO_POOL)
        return '<section class="container"><div class="lg-row">%s</div></section>' % ls
    if kind == 'newsletter':
        return ('<section class="container">%s</section>' % _sec('newsletter',
                '<form class="nl card card-pad" onsubmit="return false">'
                '<input type="email" placeholder="你的邮箱" aria-label="邮箱" required>'
                '<button class="btn btn-primary" type="submit">订阅</button>'
                '<small>每月一封，只讲干货，随时退订。</small></form>'))
    if kind == 'story':
        ch = ''.join('<div class="st-ch card"><span class="st-no">%02d</span><b>%s</b><p>%s</p></div>'
                     % (j + 1, html.escape(t['blocks'][j][0]), html.escape(t['blocks'][j][1]))
                     for j in range(min(2, len(t['blocks']))))
        return '<section class="container">%s</section>' % _sec('story', '<div class="st-grid">%s</div>' % ch)
    if kind == 'problem':
        pts = ''.join('<li>%s</li>' % x for x in ['排期靠吼', '跟进靠记', '复盘靠猜'])
        return ('<section class="container">%s</section>' % _sec('problem',
                '<div class="pb card card-pad"><p class="pb-big">工具换了三套，事情还是那些事情。</p>'
                '<ul class="pb-list">%s</ul></div>' % pts))
    if kind == 'cta':
        return ('<section class="container"><div class="cta-full card card-pad">'
                '<h2>%s</h2><p>%s</p>'
                '<a class="btn btn-primary" href="#">%s</a></div></section>'
                % (html.escape(t['cta1']) + '，现在', html.escape(t['meta']), html.escape(t['cta1'])))
    if kind == 'value':
        b = t['blocks'][i % len(t['blocks'])]
        return ('<section class="container">%s</section>' % _sec('value',
                '<div class="val card card-pad"><b>%s</b><p>%s</p></div>' % (html.escape(b[0]), html.escape(b[1]))))
    if kind == 'footer':
        return ('<footer>%s / 落地页结构样板 / <a href="../style-catalog.html">返回目录</a></footer>' % html.escape(t['foot']))
    return ''

def pattern_page(l, t, s):
    secs = parse_sections(l['Section Order'])
    body_secs = ''.join(render_section(k, t, i) for i, k in enumerate(secs))
    return ('<header class="topbar"><div class="container topbar-inner">'
            '<a class="logo" href="#"><span class="logo-mark">%s</span>%s</a>%s'
            '<a class="btn btn-primary" href="#">%s</a></div></header>'
            '<main>%s</main>') % (
        BOLT, html.escape(t['brand']), NAV, html.escape(t['cta1']), body_secs)

PATTERN_CSS = """
.hero { padding: 72px 0 48px; text-align: center; position: relative; }
.doc-meta { font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: var(--muted);
  display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
h1 { font-size: clamp(32px, 5vw, 54px); font-weight: 800; line-height: 1.16; margin-bottom: 18px; }
.sub { font-size: 17px; color: var(--muted); max-width: 560px; margin: 0 auto 34px; }
.cta-row { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
.sec { margin: 26px 0; }
.section-h { font-size: 16px; font-weight: 800; margin-bottom: 14px;
  display: flex; align-items: baseline; gap: 10px; }
.section-h small { font-family: 'IBM Plex Mono', monospace; font-size: 11px;
  color: var(--muted); font-weight: 400; letter-spacing: .1em; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat { text-align: center; }
.stat b { display: block; font-size: 34px; font-weight: 800; color: var(--primary); }
.stat span { font-size: 13px; color: var(--muted); }
.stats-row { margin: 10px 0; }
.card-pad { padding: 26px; }
.tst-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.tst { padding: 20px; }
.tst-ava { width: 40px; height: 40px; border-radius: 50%; margin-bottom: 12px;
  background: linear-gradient(135deg, var(--secondary), var(--primary)); }
.tst blockquote { font-size: 14px; line-height: 1.7; margin-bottom: 10px; }
.tst figcaption { font-size: 12px; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }
.vd { position: relative; height: 340px; display: grid; place-items: center;
  background: linear-gradient(135deg, var(--secondary), var(--primary)); }
.vd-play { width: 72px; height: 72px; border-radius: 50%; border: none; cursor: pointer;
  background: var(--card); color: var(--fg); display: grid; place-items: center;
  box-shadow: 0 10px 30px rgba(0,0,0,.25); }
.vd-dur { position: absolute; right: 16px; bottom: 12px; font-size: 12px;
  font-family: 'IBM Plex Mono', monospace; color: #fff; }
.faq details { border-bottom: 1px solid var(--border); padding: 12px 4px; }
.faq summary { cursor: pointer; font-weight: 600; font-size: 14.5px; }
.faq p { font-size: 13.5px; color: var(--muted); margin-top: 8px; }
.faq { max-width: 640px; }
.cp table { width: 100%; border-collapse: collapse; font-size: 14px; }
.cp th { text-align: left; font-size: 12.5px; color: var(--muted); padding: 8px 10px; border-bottom: 1px solid var(--border); }
.cp td { padding: 10px; border-bottom: 1px dotted var(--border); }
.cp-us { color: var(--primary); font-weight: 600; }
.cp-old { color: var(--muted); }
.gl-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.gl-i { height: 140px; border-radius: calc(var(--radius) * .7);
  background: linear-gradient(135deg, var(--secondary), var(--primary)); opacity: .85; }
.gl-grid .gl-i:nth-child(2n) { background: linear-gradient(135deg, var(--accent), var(--secondary)); }
.lg-row { display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; opacity: .75; }
.lg { font-weight: 800; font-size: 15px; padding: 8px 18px; border: 1.5px solid var(--border); border-radius: 8px; }
.nl { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; max-width: 560px; }
.nl input { flex: 1; min-width: 200px; font: inherit; padding: 11px 14px;
  border: 1.5px solid var(--border); border-radius: calc(var(--btn-radius));
  background: var(--bg); color: var(--fg); }
.nl input:focus { outline: 3px solid var(--primary); outline-offset: 1px; }
.nl small { width: 100%; font-size: 12px; color: var(--muted); }
.st-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.st-ch { padding: 22px; display: grid; gap: 8px; }
.st-no { font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: var(--primary); font-weight: 600; }
.st-ch b { font-size: 16px; }
.st-ch p { font-size: 13.5px; color: var(--muted); }
.pb-big { font-size: clamp(20px, 3vw, 28px); font-weight: 800; margin-bottom: 14px; }
.pb-list { list-style: none; display: grid; gap: 6px; }
.pb-list li { font-size: 14px; color: var(--muted); }
.pb-list li::before { content: "× "; color: var(--accent); font-weight: 800; }
.val b { font-size: 17px; display: block; margin-bottom: 6px; }
.val p { font-size: 14px; color: var(--muted); }
.val { max-width: 640px; }
.cta-full { text-align: center; margin: 30px 0 60px; }
.cta-full h2 { font-size: clamp(22px, 3.4vw, 32px); margin-bottom: 8px; }
.cta-full p { font-size: 14px; color: var(--muted); margin-bottom: 18px;
  font-family: 'IBM Plex Mono', monospace; }
footer { border-top: __BORDER__; padding: 26px 0; text-align: center; font-size: 13px; color: var(--muted); }
footer a { color: var(--primary); }
@media (max-width: 860px) { .grid3, .tst-grid, .gl-grid, .st-grid { grid-template-columns: 1fr 1fr; } nav { display: none; } }
@media (max-width: 640px) { .grid3, .tst-grid, .gl-grid, .st-grid { grid-template-columns: 1fr; } }
"""

# 分区布局要点：与 render_section 渲染同源，进提示词让 AI 复刻的布局与样张一致
SECTION_HINTS = {
    'hero': '居中大标题 + 一句副题 + 主/次两个按钮；标题上方放一行等宽小字的语义信息行（期号/批次/日期，禁止 ALL-CAPS 装饰眉标）',
    'features': '三栏等宽卡片：内联 SVG 图标 + 卡题 + 两行说明',
    'stats': '三格大数字：数字大而醒目（主色），下配一行小标签',
    'testi': '三栏引用卡：圆形占位头像 + 一句引文 + 署名',
    'video': '视频位卡片：居中播放按钮（内联 SVG 三角）+ 时长标注一行',
    'faq': '折叠问答组（details/summary），默认展开第一条，答案一两句',
    'compare': '对比表：三列（环节 / 现在 / 以前），4 行左右，"现在"列强调',
    'gallery': '四格图位（纯色或渐变占位块），等分一行',
    'logos': '客户名一行文字排（弱化色，不做图片墙）',
    'newsletter': '邮箱输入 + 订阅按钮的横排卡片，附一句承诺小字（频率/退订）',
    'story': '两章编号卡（真实序列才用编号）：两位编号 + 标题 + 两行说明',
    'problem': '痛点卡：一句加粗大痛点 + 三条短列表（每条三五字）',
    'cta': '全宽 CTA 卡：标题 + 一行信息 + 主按钮',
    'value': '单条价值主张卡：一句加粗主张 + 两行说明',
    'footer': '一行版权与返回链接',
}

def pattern_prompt(l, s, fonts):
    secs = parse_sections(l['Section Order'])
    hints = '\n'.join('%d. %s' % (i + 1, SECTION_HINTS.get(k, k)) for i, k in enumerate(secs))
    return '\n'.join([
        '请按「落地页结构：%s」官方模式实现落地页：〔在这里写下你的产品/需求与主题，主题由你确定〕' % l['Pattern Name'],
        '',
        '▍工作法（frontend-design 官方原则）：先列一份 token 计划（色 4-6 个 hex / 字体及角色 / 一句布局概念 / 一条独特性原则），自查哪一项像"任何项目都会生成的默认"，改掉再写码；hero 用你主题里最有特征的一个实物/场景开场，别用"大数字+小标签+渐变强调"的默认套路；大胆只花在一处，其余克制。',
        '',
        '▍官方结构（landing.csv 原文，零改写）：',
        '- Section Order: %s' % l['Section Order'].strip(),
        '- Primary CTA Placement: %s' % l['Primary CTA Placement'].strip(),
        '- Color Strategy: %s' % l['Color Strategy'].strip(),
        '- Recommended Effects: %s' % l['Recommended Effects'].strip(),
        '- Conversion Optimization: %s' % l['Conversion Optimization'].strip(),
        '',
        '▍分区布局要点（与样张同源，逐区落实）：',
        hints,
        '',
        '▍本样板 token（实际使用值，直接可用）：',
        '- 主 %s / 辅 %s / 强调 %s / 底 %s / 圆角 %s' % (s['primary'], s['secondary'], s['accent'], s['bg'], s['radius']),
        '- 标题字体 %s / 正文字体 %s（Google Fonts，中文回退 PingFang SC / Microsoft YaHei）' % fonts,
        '',
        '▍动效：按钮 hover 抬升属常规交互；全页只允许一次亮相动效（建议给 hero 的一个元素），禁止逐区块 fade-in 上升',
        '',
        '▍必须避开（AI 指纹清单，frontend-design 原则）：',
        '- ALL-CAPS 装饰性眉标（信息行必须有语义）；按钮尾部箭头 →；中点分隔 meta 串（A · B · C）',
        '- 无语义 01/02/03 编号（结构分区名须有语义）；默认 Inter/Roboto 字体；emoji 图标（一律内联 SVG）；近黑 #0B0B0B 假装黑色',
        '',
        '▍验收：区块顺序严格按官方 Section Order；正文对比度 ≥4.5:1；:focus-visible 可见焦点；prefers-reduced-motion 降级；响应式 375/768/1440；标题行长 ≤80 字符',
    ])

def _load_json(fname):
    fp = os.path.join(BASE, fname)
    return json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else []

def product_prompt(p):
    pal = ' / '.join('%s %s' % (k, v) for k, v in p['palette'].items() if v.startswith('#'))
    rea = ' / '.join('%s：%s' % (k, v) for k, v in p['reasoning'].items())
    return '\n'.join([
        '请按「%s」官方产品方案实现页面：〔在这里写下你的产品名与需求，产品由你确定〕' % p['name'],
        '',
        '▍工作法（frontend-design 官方原则）：先列 token 计划（色 4-6 个 hex / 字体及角色 / 一句布局概念 / 一条独特性原则），自查是否"任何项目都会生成的默认"，改掉再写码；视觉必须从你的产品主题本身找依据。',
        '',
        '▍官方推荐（products.csv 原文，零改写）：',
        '- Primary Style Recommendation: %s' % p['primary_style'],
        '- Secondary Styles: %s' % p['secondary'],
        '- Landing Page Pattern: %s' % p['pattern'],
        '- Color Palette Focus: %s' % p['palette_focus'],
        '- Keywords: %s' % p['keywords'],
        '',
        '▍官方专属色板（colors.csv，直接可用）：%s' % pal,
        '▍官方推理（ui-reasoning.csv）：%s' % rea,
        '',
        '▍动效：全页只允许一次亮相动效，禁止逐区块 fade-in',
        '▍必须避开（AI 指纹清单）：ALL-CAPS 装饰性眉标；按钮尾部箭头 →；带空格中点分隔 meta 串；无语义 01/02/03 编号；emoji 图标（一律内联 SVG）',
        '▍验收：对比度 ≥4.5:1；:focus-visible；prefers-reduced-motion；响应式 375/768/1440',
    ])

def chart_prompt(c):
    rows = ['%s: %s' % (k, c[k]) for k in (
        'Best Chart Type', 'Secondary Options', 'When to Use', 'When NOT to Use',
        'Data Volume Threshold', 'Color Guidance', 'Accessibility Grade', 'Accessibility Risk',
        'Accessibility Notes', 'A11y Fallback', 'Library Recommendation', 'Interactive Level') if c.get(k)]
    return '\n'.join([
        '请按「%s」图表选型实现数据展示：〔在这里写下你的数据与场景〕' % c['Data Type'],
        '',
        '▍官方选型（charts.csv 原文，零改写）：',
    ] + ['- %s' % r for r in rows] + [
        '',
        '▍实现要求：图表手写内联 SVG（禁图表库）；数字 tabular-nums；不能只靠颜色区分系列（直接标注/线型差异）；数据真实感且口径自洽',
        '▍动效：图表一次生长/描边亮相即可，reduced-motion 降级',
        '▍必须避开（AI 指纹清单）：ALL-CAPS 装饰眉标；按钮尾箭头 →；带空格中点分隔；emoji',
        '▍验收：对比度 ≥4.5:1；:focus-visible；prefers-reduced-motion；响应式 375/768/1440',
    ])

# ---------- Memphis Design 目录页（官方四色 #FF71CE/#FFCE5C/#86CCCA/#6A7BB4） ----------
def build_catalog(manifest, entries, lentries=None, centries=None, pentries=None, chentries=None):
    handmade = {
        'AI-Native UI': 'ai-native.html', 'Liquid Glass': 'liquid-glass.html',
        'Brutalism': 'brutalism.html', 'Flat Design': 'flat-crm.html',
        'Aurora UI': 'aurora.html', 'Neumorphism': 'neumorphism.html',
        'Bento Box Grid': 'bento.html', 'Memphis Design': 'memphis.html',
    }
    cards = []
    cards.append('<div class="layer-head" id="layer-style"><h2>视觉风格</h2><span>79 个 · styles.csv</span></div>')
    for idx, (r, file, t) in enumerate(manifest):
        en = r['Style Category']
        zh = ZH_NAMES.get(en, en)
        prompt = theme_prompt(r, make_skin(r), t)
        hexes = re.findall(r'#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?\b', r['Primary Colors'])[:6]
        sw = ''.join('<i style="background:%s" title="%s"></i>' % (h, h) for h in hexes) \
             or '<em class="noswatch">色板为文字描述，见提示词</em>'
        status = 'active' if r['Status'] == 'active' else 'supp'
        demo_link = '<a class="demo-link" href="%s">查看样张</a>' % file
        search = html.escape((en + ' ' + zh + ' ' + r['Keywords'] + ' ' + r['Best For']).lower())
        cards.append('''<article class="m-card s%s" data-type="%s" data-status="%s" data-search="%s">
  <div class="m-head">
    <div>
      <h2>%s</h2>
      <span class="en">%s</span>
    </div>
    <div class="badges">
      <span class="badge type">%s</span>
      <span class="badge %s">%s</span>
    </div>
  </div>
  <div class="swatch">%s</div>
  <p class="best">%s</p>
  <div class="links">%s</div>
  <details class="prompt-box"><summary>查看提示词</summary>
     <pre class="prompt">%s</pre>
    <button class="copy-btn" type="button">复制提示词</button>
  </details>
  </details>
</article>''' % ('abcd'[idx % 4], html.escape(r['Type']), status, search,
                  html.escape(zh), html.escape(en),
                  html.escape(TYPE_ZH.get(r['Type'], r['Type'])),
                  'b-active' if status == 'active' else 'b-supp',
                  '活跃' if status == 'active' else '补充',
                  sw, html.escape(r['Best For'].strip()),
                  demo_link, html.escape(prompt)))

    # 产品类型卡（第二层：官方推荐组合）
    for p, col, file, layout in entries:
        hexes = [col[k] for k in ('Primary', 'Secondary', 'Accent', 'Background') if col.get(k)]
        sw = ''.join('<i style="background:%s" title="%s"></i>' % (h, h) for h in hexes)
        cards.append('''<article class="m-card s%s" data-type="product" data-status="product" data-search="%s">
  <div class="m-head">
    <div>
      <h2>%s</h2>
      <span class="en">No.%s / %s</span>
    </div>
    <div class="badges"><span class="badge b-prod">%s</span><span class="badge b-active">%s</span></div>
  </div>
  <div class="swatch">%s</div>
  <p class="best">%s</p>
  <div class="links"><a class="demo-link" href="product-demos/%s">查看样张</a></div>
  <details class="prompt-box"><summary>查看提示词</summary>
     <pre class="prompt">%s</pre>
    <button class="copy-btn" type="button">复制提示词</button>
  </details>
  </details>
</article>''' % ('abcd'[int(p['No']) % 4],
                  html.escape((p['Product Type'] + ' ' + p['Keywords'] + ' ' + p['Primary Style Recommendation'] + ' ' + LAYOUT_ZH[layout]).lower()),
                  html.escape(p['Product Type']), p['No'],
                  html.escape(p['Primary Style Recommendation'].split('+')[0].strip()),
                  LAYOUT_ZH[layout],
                  html.escape(p['Primary Style Recommendation'].split('+')[0].strip()),
                  sw, html.escape(p['Keywords'].strip()[:110]),
                  file, html.escape(product_prompt(p, col, layout))))

    # 落地页结构卡（第三层：landing.csv 官方结构）
    cards.append('<div class="layer-head" id="layer-pattern"><h2>落地页结构</h2><span>34 个 · landing.csv</span></div>')
    for l, s, file, fonts in (lentries or []):
        cards.append('''<article class="m-card s%s" data-type="pattern" data-status="pattern" data-search="%s">
  <div class="m-head">
    <div>
      <h2>%s</h2>
      <span class="en">落地页结构 No.%s</span>
    </div>
    <div class="badges"><span class="badge b-pat">落地结构</span></div>
  </div>
  <p class="best">%s</p>
  <div class="links"><a class="demo-link" href="pattern-demos/%s">查看样张</a></div>
  <details class="prompt-box"><summary>查看提示词</summary>
     <pre class="prompt">%s</pre>
    <button class="copy-btn" type="button">复制提示词</button>
  </details>
  </details>
</article>''' % ('abcd'[int(l['No']) % 4],
                  html.escape((l['Pattern Name'] + ' ' + l['Keywords'] + ' 落地页 结构 landing').lower()),
                  html.escape(l['Pattern Name']), l['No'],
                  html.escape(l['Section Order'].strip()[:120]),
                  file, html.escape(pattern_prompt(l, s, fonts))))

    # 内容排版卡（第四层：html-anything 18 种内容排版风格，转写见 content_styles.py）
    cards.append('<div class="layer-head" id="layer-content"><h2>内容排版</h2><span>18 个 · html-anything</span></div>')
    for ci, cs in enumerate(centries or []):
        cards.append('''<article class="m-card s%s" data-type="content" data-status="content" data-search="%s">
  <div class="m-head">
    <div>
      <h2>%s</h2>
      <span class="en">%s / 内容排版</span>
    </div>
    <div class="badges"><span class="badge b-pat">内容排版</span></div>
  </div>
  <p class="best">%s</p>
  <div class="links"><a class="demo-link" href="content-demos/%s.html">查看样张</a></div>
  <details class="prompt-box"><summary>查看提示词</summary>
     <pre class="prompt">%s</pre>
    <button class="copy-btn" type="button">复制提示词</button>
  </details>
  </details>
</article>''' % ('abcd'[ci % 4],
                  html.escape((cs['zh'] + ' ' + cs['en'] + ' ' + cs['use'] + ' 内容 排版 content').lower()),
                  html.escape(cs['zh']), html.escape(cs['en']),
                  html.escape(cs['use'][:110]),
                  cs['id'], html.escape(content_styles.content_prompt(cs))))
    # 产品模板卡（第五层：products.csv 官方推荐，样张手工精修，文件存在才显示）
    cards.append('<div class="layer-head" id="layer-product"><h2>产品类型模板</h2><span>40 个 · products.csv</span></div>')
    for pi, (p, pfile) in enumerate(pentries or []):
        sw = ''.join('<i style="background:%s" title="%s"></i>' % (v, k) for k, v in p['palette'].items() if v.startswith('#'))
        cards.append('<article class="m-card s%s" data-type="product" data-status="product" data-search="%s">'
          '<div class="m-head"><div><h2>%s</h2><span class="en">产品模板 / %s</span></div>'
          '<div class="badges"><span class="badge b-prod">产品</span></div></div>'
          '<div class="swatch">%s</div>'
          '<p class="best">%s</p>'
          '<div class="links"><a class="demo-link" href="product-demos/%s">查看样张</a></div>'
          '<details class="prompt-box"><summary>查看提示词</summary>'
          '  <pre class="prompt">%s</pre>'
          '  <button class="copy-btn" type="button">复制提示词</button></details></article>' % (
          'abcd'[pi % 4],
          html.escape((p['name'] + ' ' + p['keywords'] + ' ' + p['primary_style'] + ' 产品 product').lower()),
          html.escape(p['name']), html.escape(p['primary_style'].split('+')[0].strip()[:22]),
          sw, html.escape('官方推荐：' + p['primary_style'][:100]),
          pfile, html.escape(product_prompt(p))))

    # 图表图鉴卡（第六层：charts.csv 官方选型，样张手工精修，文件存在才显示）
    cards.append('<div class="layer-head" id="layer-chart"><h2>图表图鉴</h2><span>25 个 · charts.csv</span></div>')
    for ci, (c, cfile) in enumerate(chentries or []):
        cards.append('<article class="m-card s%s" data-type="chart" data-status="chart" data-search="%s">'
          '<div class="m-head"><div><h2>%s</h2><span class="en">图表图鉴 / %s</span></div>'
          '<div class="badges"><span class="badge b-pat">图表</span></div></div>'
          '<p class="best">%s</p>'
          '<div class="links"><a class="demo-link" href="chart-demos/%s">查看样张</a></div>'
          '<details class="prompt-box"><summary>查看提示词</summary>'
          '  <pre class="prompt">%s</pre>'
          '  <button class="copy-btn" type="button">复制提示词</button></details></article>' % (
          'abcd'[ci % 4],
          html.escape((c['Data Type'] + ' ' + c['Keywords'] + ' ' + c['Best Chart Type'] + ' 图表 chart').lower()),
          html.escape(c['Data Type']), html.escape(c['Best Chart Type'][:24]),
          html.escape('首选：' + c['Best Chart Type']),
          cfile, html.escape(chart_prompt(c))))

    page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<title>UI 设计提示词库</title>
<meta name="description" content="113 个 UI 设计风格与落地页结构模板：官方提示词、色板、一键复制样张，看中哪个风格就复制提示词交给 AI 复刻网页。">
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Rubik:wght@400;500;600;700&display=swap');

:root {
  --memphis-pink: #FF71CE; --memphis-yellow: #FFCE5C; --memphis-teal: #86CCCA; --memphis-purple: #6A7BB4;
  --ink: #16161D; --bg: #FFFDF6;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Rubik', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  background-image: radial-gradient(rgba(22,22,29,.09) 1.6px, transparent 1.6px);
  background-size: 22px 22px;
  color: var(--ink); line-height: 1.6; padding: 40px 24px;
  overflow-x: hidden;
}
.wrap { max-width: 1180px; margin: 0 auto; position: relative; }

.deco { position: absolute; pointer-events: none; }
.deco-tri { width: 0; height: 0; border-left: 26px solid transparent; border-right: 26px solid transparent; border-bottom: 46px solid var(--memphis-yellow); }
.deco-ring { width: 56px; height: 56px; border-radius: 50%; border: 11px solid var(--memphis-pink); }

.hero { text-align: center; padding: 18px 0 26px; position: relative; }
.hero-tag {
  display: inline-block; font-family: 'Outfit', sans-serif;
  font-weight: 800; font-size: 13px; letter-spacing: .06em;
  background: var(--memphis-purple); color: #fff;
  border: 3px solid var(--ink); border-radius: 999px;
  padding: 5px 16px; margin-bottom: 16px; transform: rotate(-2deg);
  box-shadow: 4px 4px 0 var(--memphis-yellow);
  text-decoration: none;
}
.hero-tag:hover { background: var(--ink); }
.hero-tag:focus-visible { outline: 3px solid var(--memphis-pink); outline-offset: 3px; }
h1 {
  font-family: 'Outfit', 'PingFang SC', sans-serif;
  font-size: clamp(30px, 4.6vw, 46px); font-weight: 900; line-height: 1.12;
  margin-bottom: 12px;
}
h1 .u-pink { background: linear-gradient(transparent 60%, var(--memphis-pink) 60%, var(--memphis-pink) 92%, transparent 92%); }
h1 .u-teal { background: linear-gradient(transparent 60%, var(--memphis-teal) 60%, var(--memphis-teal) 92%, transparent 92%); }
.desc { font-size: 15px; font-weight: 500; max-width: 560px; margin: 0 auto; }
.desc b { background: var(--memphis-yellow); padding: 0 4px; }

.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin: 26px 0 12px; }
#search {
  flex: 1; min-width: 220px; font: inherit; font-size: 14.5px;
  padding: 11px 18px; background: #fff; color: var(--ink);
  border: 3px solid var(--ink); border-radius: 16px;
  box-shadow: 4px 4px 0 var(--memphis-teal);
}
#search:focus { outline: 3px solid var(--memphis-purple); outline-offset: 2px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.chip {
  font-family: 'Outfit', sans-serif;
  font-size: 13px; font-weight: 700;
  padding: 6px 16px; border-radius: 999px; cursor: pointer;
  background: #fff; color: var(--ink);
  border: 2.5px dashed var(--ink);
  transition: background 140ms ease, color 140ms ease, border-style 140ms ease;
}
.chip:hover { background: var(--memphis-yellow); }
.chip.on { background: var(--ink); color: #fff; border-style: solid; }
.chip:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }
.sort-chip { border-style: dashed; }
.sort-chip.on { border-style: solid; background: var(--memphis-purple); }
.count { font-size: 13px; font-weight: 600; color: #6E6E78; margin-bottom: 18px; }

.grid { display: grid; grid-template-columns: 1fr; gap: 24px; }
.m-card {
  background: #fff; border: 3px solid var(--ink); border-radius: 22px;
  padding: 24px 26px; position: relative;
  transition: transform 160ms ease, box-shadow 160ms ease;
}
.m-card.sa { box-shadow: 8px 8px 0 var(--memphis-pink); }
.m-card.sb { box-shadow: 8px 8px 0 var(--memphis-yellow); transform: rotate(-.4deg); }
.m-card.sc { box-shadow: 8px 8px 0 var(--memphis-teal); }
.m-card.sd { box-shadow: 8px 8px 0 var(--memphis-purple); transform: rotate(.35deg); }
.m-card:hover { transform: rotate(0) translateY(-4px); }
.m-card.hidden, .layer-head.hidden { display: none !important; }
.head { display: flex; justify-content: space-between; gap: 14px; align-items: flex-start; }
.head h2 { font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 800; }
.en { font-size: 12.5px; color: #8A8A96; letter-spacing: .04em; }
.theme-tag { display: inline-block; margin-left: 8px; font-size: 12px; font-weight: 700; color: #16161D; background: #FFCE5C; border: 2px solid #16161D; border-radius: 999px; padding: 1px 10px; }
.badges { display: flex; gap: 6px; flex: none; }
.badge {
  font-family: 'Outfit', sans-serif;
  font-size: 11.5px; font-weight: 700; padding: 3px 11px;
  border: 2px solid var(--ink); border-radius: 999px;
}
.badge.type { background: var(--memphis-teal); }
.b-active { background: var(--memphis-yellow); }
.b-supp { background: #F3F0E7; }
.b-prod { background: #86CCCA; }
.b-pat { background: #FFCE5C; }
.swatch { display: flex; gap: 6px; margin: 14px 0 10px; align-items: center; flex-wrap: wrap; }
.swatch i { width: 24px; height: 24px; border-radius: 8px; border: 2px solid var(--ink); }
.swatch .noswatch { font-size: 12px; color: #8A8A96; font-style: normal; }
.best { font-size: 13px; color: #4B4B55; margin-bottom: 14px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.links { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.demo-link {
  font-family: 'Outfit', sans-serif;
  display: inline-flex; align-items: center; font-size: 13px; font-weight: 700;
  padding: 8px 18px; border-radius: 999px; text-decoration: none;
  background: var(--ink); color: #fff; border: 2.5px solid var(--ink);
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.demo-link:hover { transform: translate(-2px, -2px); box-shadow: 4px 4px 0 var(--memphis-pink); }
.demo-link:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }
.demo-link.handmade { background: #fff; color: var(--ink); border-style: dashed; }
.demo-link.handmade:hover { box-shadow: 4px 4px 0 var(--memphis-teal); }
.prompt {
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12.5px; line-height: 1.65; white-space: pre-wrap; word-break: break-word;
  background: #FFFBEC; color: var(--ink);
  border: 2.5px dashed var(--ink); border-radius: 14px;
  padding: 16px 18px;
  max-height: 240px; overflow-y: auto; margin-bottom: 14px;
}
.copy-btn {
  font-family: 'Outfit', sans-serif;
  font-size: 13.5px; font-weight: 700;
  padding: 9px 22px;
  background: var(--memphis-pink); color: var(--ink);
  border: 3px solid var(--ink); border-radius: 999px;
  box-shadow: 4px 4px 0 var(--ink);
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.copy-btn:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
.copy-btn:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0 var(--ink); }
.copy-btn:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }
footer { margin-top: 36px; text-align: center; font-size: 13px; font-weight: 600; color: #6E6E78; }
footer a { color: var(--memphis-purple); font-weight: 700; }
@media (min-width: 900px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1180px) { .grid { grid-template-columns: repeat(3, 1fr); } }

/* 分层锚点标题 */
.layer-head { grid-column: 1 / -1; display: flex; align-items: baseline; gap: 14px;
  margin: 34px 0 6px; padding-bottom: 10px; border-bottom: 4px solid var(--ink);
  scroll-margin-top: 120px; }
.layer-head h2 { font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 26px; }
.layer-head span { font-size: 13px; color: #6E6E78; font-weight: 500; }

/* 提示词折叠盒 */
.prompt-box { border: 2.5px dashed var(--ink); border-radius: 12px; padding: 10px 14px; margin: 12px 0; }
.prompt-box summary { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 13.5px;
  cursor: pointer; color: var(--ink); user-select: none; }
.prompt-box summary:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }
.prompt-box[open] summary { border-bottom: 2px dashed rgba(22,22,29,.25); padding-bottom: 8px; margin-bottom: 10px; }
.prompt-box .prompt { max-height: 300px; }

/* 返回顶部 */
#to-top { position: fixed; right: 22px; bottom: 26px; z-index: 60;
  width: 46px; height: 46px; border-radius: 50%;
  background: var(--ink); color: #fff; border: 3px solid var(--ink);
  cursor: pointer; display: none; align-items: center; justify-content: center;
  box-shadow: 4px 4px 0 rgba(22,22,29,.25); }
#to-top.show { display: flex; }
#to-top:hover { transform: translate(-1px,-1px); }
#to-top:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }

/* 一级分区标签（横滑） */
.tabs { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: thin;
  -webkit-overflow-scrolling: touch; padding: 4px 2px 8px; margin: 18px 0 10px; }
.tab { flex: 0 0 auto; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 14.5px;
  border: 2.5px solid var(--ink); border-radius: 999px; padding: 8px 18px;
  background: #fff; color: var(--ink); cursor: pointer; white-space: nowrap;
  transition: background 150ms ease, color 150ms ease; }
.tab:hover { background: var(--memphis-yellow); }
.tab.on { background: var(--ink); color: #fff; }
.tab:focus-visible { outline: 3px solid var(--memphis-purple); outline-offset: 3px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }


/* 分区切换过渡：内容从左滑入（转场反馈，非亮相装饰） */
@keyframes layer-in { from { opacity: 0; transform: translateX(-36px); } to { opacity: 1; transform: none; } }
.grid.layer-anim { animation: layer-in 320ms cubic-bezier(.22,.61,.21,1) both; }
@media (prefers-reduced-motion: reduce) { .grid.layer-anim { animation: none; } }

/* 懒渲染占位 */
.m-card.pending { content-visibility: auto; contain-intrinsic-size: auto 366px; }
@media (max-width: 640px) { .deco { display: none; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
</style>
</head>
<body>
<div class="wrap">
  <span class="deco deco-tri" style="top:-14px; left:-6px; transform:rotate(-14deg)" aria-hidden="true"></span>
  <span class="deco deco-ring" style="top:6px; right:4%; transform:rotate(10deg)" aria-hidden="true"></span>

  <section class="hero">
    <a class="hero-tag" href="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill" target="_blank" rel="noopener">ui-ux-pro-max / 风格手册 ↗</a>
    <h1>UI 设计<span class="u-pink">提示词</span>库<br>× <span class="u-teal">一键</span>复刻</h1>
    <p class="desc">共 <b>196 个模板</b>：79 种风格 + 34 种落地页结构 + 18 种内容排版 + 40 个产品类型 + 25 种图表图鉴。用法：找模板 → <b>复制提示词</b> → 粘贴给 AI。</p>
    <p class="online-row" style="margin-top:12px"><span class="ts-online" hidden></span></p>
  </section>

  <div class="toolbar">
    <input id="search" type="search" placeholder="搜索风格名 / 关键词 / 适用场景，如：仪表盘、glassmorphism、playful…" aria-label="搜索风格">
  </div>

  <nav class="tabs" id="layer-tabs" role="tablist" aria-label="模板分区">
    <button class="tab on" data-layer="all" role="tab" aria-selected="true">全部 196</button>
    <button class="tab" data-layer="style" role="tab" aria-selected="false">视觉风格 79</button>
    <button class="tab" data-layer="pattern" role="tab" aria-selected="false">落地结构 34</button>
    <button class="tab" data-layer="content" role="tab" aria-selected="false">内容排版 18</button>
    <button class="tab" data-layer="product" role="tab" aria-selected="false">产品模板 40</button>
    <button class="tab" data-layer="chart" role="tab" aria-selected="false">图表图鉴 25</button>
  </nav>
  <div class="chips" id="sub-chips" role="group" aria-label="类型筛选"></div>
  <p class="count" id="count"></p>
  <button class="chip sort-chip" id="sort-hot" type="button" aria-pressed="false">热度排序</button>
  <div class="grid" id="grid">
__CARDS__
  </div>
  <footer>UI 设计提示词库 / Memphis Design 版 / 生成自 <a href="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill" target="_blank" rel="noopener">ui-ux-pro-max</a> 官方风格库 styles.csv（已剔除 9 个废弃风格）/ <a href="index.html">返回八版精修样张</a> / 友情链接 / <a href="https://www.lhxl.chat/" target="_blank" rel="noopener">lhxl.chat</a> / <a href="https://wordflow.lhxl.chat/download" target="_blank" rel="noopener">WordFlow 下载</a></footer>
</div>
<button id="to-top" type="button" aria-label="返回顶部">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>
<script src="stats.js"></script>
<script>
// 返回顶部
(function() {
  var btn = document.getElementById('to-top');
  var onScroll = function() { btn.classList.toggle('show', window.scrollY > window.innerHeight); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  btn.addEventListener('click', function() { window.scrollTo({ top: 0, behavior: 'smooth' }); });
})();
// 懒渲染：卡片带 content-visibility，浏览器自动跳过屏外渲染（.pending 类在 apply() 里统一加）
var gridEl = document.getElementById('grid');
var cards = Array.prototype.slice.call(document.querySelectorAll('.m-card'));
var heads = Array.prototype.slice.call(document.querySelectorAll('.layer-head'));
var searchEl = document.getElementById('search');
var countEl = document.getElementById('count');
var tabsEl = document.getElementById('layer-tabs');
var subEl = document.getElementById('sub-chips');
var curLayer = 'all';
var curSub = 'all';

// 卡片所属层：风格卡 data-type 是 Type 细分，其余层直接对应
function cardLayer(c) {
  var t = c.getAttribute('data-type'), st = c.getAttribute('data-status');
  if (t === 'pattern' || st === 'pattern') return 'pattern';
  if (t === 'content' || st === 'content') return 'content';
  if (t === 'product' || st === 'product') return 'product';
  if (t === 'chart' || st === 'chart') return 'chart';
  return 'style';
}

// 各层的二级筛选定义（只有风格层有子类）
var SUBS = {
  style: [['all', '全部'], ['General', '通用'], ['Mobile', '移动端'], ['BI/Analytics', 'BI 分析'], ['Platform/System', '平台系统'], ['Platform/Material', '平台材质'], ['active', '仅活跃']]
};

function renderSubs() {
  var defs = SUBS[curLayer];
  subEl.innerHTML = '';
  if (!defs) { subEl.style.display = 'none'; return; }
  subEl.style.display = 'flex';
  defs.forEach(function(d, i) {
    var b = document.createElement('button');
    b.className = 'chip' + (curSub === d[0] ? ' on' : '');
    b.setAttribute('data-f', d[0]);
    b.setAttribute('type', 'button');
    b.textContent = d[1];
    b.addEventListener('click', function() {
      curSub = d[0];
      Array.prototype.forEach.call(subEl.children, function(x) { x.classList.remove('on'); });
      b.classList.add('on');
      apply();
    });
    subEl.appendChild(b);
  });
}

function apply() {
  var q = searchEl.value.trim().toLowerCase();
  var n = 0;
  cards.forEach(function(c) {
    var okLayer = curLayer === 'all' || cardLayer(c) === curLayer;
    var okSub = curLayer !== 'style' || curSub === 'all' || c.getAttribute('data-type') === curSub || c.getAttribute('data-status') === curSub;
    var okQ = !q || c.getAttribute('data-search').indexOf(q) !== -1;
    var show = okLayer && okSub && okQ;
    c.classList.toggle('hidden', !show);
    if (show) c.classList.add('pending');
    if (show) n++;
  });
  // 分区标题：全部层时显示全部，选中层时只留该层标题
  heads.forEach(function(h) {
    var id = h.id.replace('layer-', '');
    h.classList.toggle('hidden', curLayer !== 'all' && curLayer !== id);
  });
  countEl.textContent = curLayer === 'all'
    ? '显示 ' + n + ' / ' + cards.length + ' 个模板'
    : '本区显示 ' + n + ' 个模板';
}
searchEl.addEventListener('input', apply);
Array.prototype.forEach.call(tabsEl.querySelectorAll('.tab'), function(t) {
  t.addEventListener('click', function() {
    Array.prototype.forEach.call(tabsEl.querySelectorAll('.tab'), function(x) {
      x.classList.remove('on'); x.setAttribute('aria-selected', 'false');
    });
    t.classList.add('on'); t.setAttribute('aria-selected', 'true');
    curLayer = t.getAttribute('data-layer');
    curSub = 'all';
    renderSubs();
    apply();
    gridEl.classList.remove('layer-anim');
    void gridEl.offsetWidth;
    gridEl.classList.add('layer-anim');
    window.scrollTo({ top: gridEl.getBoundingClientRect().top + window.scrollY - 140, behavior: 'auto' });
  });
});
renderSubs();
Array.prototype.forEach.call(document.querySelectorAll('.copy-btn'), function(btn) {
  btn.addEventListener('click', function() {
    var text = btn.closest('.m-card').querySelector('.prompt').textContent;
    var done = function() {
      btn.textContent = '已复制'; setTimeout(function() { btn.textContent = '复制提示词'; }, 1600);
      ThemeStats.mark(btn);
    };
    var fallback = function() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); }
      catch (e) { btn.textContent = '请手动选择复制'; }
      document.body.removeChild(ta);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else fallback();
  });
});

// 热度排序：按全站复制次数降序，再点一次恢复默认顺序
var origOrder = Array.prototype.slice.call(gridEl.querySelectorAll('.m-card'));
var hotOn = false;
var hotBtn = document.getElementById('sort-hot');
function hotCount(card) {
  return (ThemeStats.counts || {})[card.querySelector('h2').textContent.trim()] || 0;
}
function renderOrder() {
  var cards = Array.prototype.slice.call(gridEl.querySelectorAll('.m-card'));
  if (hotOn) cards.sort(function(a, b) { return hotCount(b) - hotCount(a); });
  else cards = origOrder;
  cards.forEach(function(c) { gridEl.appendChild(c); });
}
hotBtn.addEventListener('click', function() {
  hotOn = !hotOn;
  hotBtn.classList.toggle('on', hotOn);
  hotBtn.setAttribute('aria-pressed', hotOn ? 'true' : 'false');
  renderOrder();
});
if (window.ThemeStats) ThemeStats.onupdate = renderOrder;

apply();
</script>
</body>
</html>'''
    return page.replace('__CARDS__', '\n'.join(cards))

# ---------- 主流程 ----------
def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding='utf-8')) if r['Status'] != 'deprecated']
    rows.sort(key=lambda r: (r['Status'] != 'active', r['Type'], r['Style Category']))
    manifest = []
    fam_count = {}
    font_log = {}
    data_idx = 0
    theme_use = {}
    for r in rows:
        s = make_skin(r)
        fam_count[s['family']] = fam_count.get(s['family'], 0) + 1
        fh, fb, fq = pick_fonts(r['Keywords'] + ' ' + r['Style Category'])
        font_log[r['Style Category']] = '%s / %s' % (fh, fb)
        if s['family'] == 'data':
            tkey = DATA_CYCLE[data_idx % len(DATA_CYCLE)]
            t, data_idx = THEMES[tkey], data_idx + 1
        else:
            cyc = FAMILY_THEME.get(s['family'], ['newsroom'])
            n = fam_count[s['family']]
            tkey = cyc[(n - 1) % len(cyc)]
            t = THEMES[tkey]
        theme_use[tkey] = theme_use.get(tkey, 0) + 1
        prompt = theme_prompt(r, s, t)
        _handmade = {
            'AI-Native UI': 'ai-native.html', 'Liquid Glass': 'liquid-glass.html',
            'Brutalism': 'brutalism.html', 'Flat Design': 'flat-crm.html',
            'Aurora UI': 'aurora.html', 'Neumorphism': 'neumorphism.html',
            'Bento Box Grid': 'bento.html', 'Memphis Design': 'memphis.html',
            'Glassmorphism': 'glassmorphism.html', 'Neubrutalism': 'neubrutalism.html',
            'Spatial UI (VisionOS)': 'spatial-ui-visionos.html', 'Dark Mode (OLED)': 'dark-mode-oled.html',
            'Vaporwave': 'vaporwave.html', 'Pixel Art': 'pixel-art.html', 'Fluent 2': 'fluent-2.html',
            'Skeuomorphism': 'skeuomorphism.html',
            'Material 3 Expressive (Mobile)': 'material-3-expressive-mobile.html',
            'Adobe Spectrum': 'adobe-spectrum.html', 'Shopify Polaris': 'shopify-polaris.html',
            'E-Ink / Paper': 'e-ink-paper.html', 'Retro-Futurism': 'retro-futurism.html',
            'Cyberpunk UI': 'cyberpunk-ui.html', 'Kinetic Typography': 'kinetic-typography.html',
            'Claymorphism': 'claymorphism.html',
            'Swiss Modernism 2.0': 'swiss-modernism-2-0.html',
            'Editorial Grid / Magazine': 'editorial-grid-magazine.html',
            'Interactive Cursor Design': 'interactive-cursor-design.html',
            'Bauhaus (包豪斯)': 'bauhaus.html',
            'Organic Biophilic': 'organic-biophilic.html',
            'Data-Dense Dashboard': 'data-dense-dashboard.html',
            'HUD / Sci-Fi FUI': 'hud-sci-fi-fui.html',
            '3D Product Preview': '3d-product-preview.html',
            'Y2K Aesthetic': 'y2k-aesthetic.html',
            'Vintage Analog / Retro Film': 'vintage-analog-retro-film.html',
            'Motion-Driven': 'motion-driven.html',
            'Micro-interactions': 'micro-interactions.html',
            'Parallax Storytelling': 'parallax-storytelling.html',
            'Gen Z Chaos / Maximalism': 'gen-z-chaos-maximalism.html',
            'Dimensional Layering': 'dimensional-layering.html',
            'Minimalist Monochrome': 'minimalist-monochrome.html',
            '3D & Hyperrealism': '3d-hyperrealism.html',
            'Anti-Polish / Raw Aesthetic': 'anti-polish-raw-aesthetic.html',
            'Biomimetic / Organic 2.0': 'biomimetic-organic-2-0.html',
            'Chromatic Aberration / RGB Split': 'chromatic-aberration-rgb-split.html',
            'Exaggerated Minimalism': 'exaggerated-minimalism.html',
            'Gradient Mesh / Aurora Evolved': 'gradient-mesh-aurora-evolved.html',
            'Nature Distilled': 'nature-distilled.html',
            'Soft UI Evolution': 'soft-ui-evolution.html',
            'Minimalism & Swiss Style': 'minimalism-swiss-style.html',
            'Vibrant & Block-based': 'vibrant-block-based.html',
            'Voice-First Multimodal': 'voice-first-multimodal.html',
            'Zero Interface': 'zero-interface.html',
            'Tactile Digital / Deformable UI': 'tactile-digital-deformable-ui.html',
            'Spectrum 2': 'spectrum-2.html',
            'Accessible & Ethical': 'accessible-ethical.html',
            'Real-Time Monitoring': 'real-time-monitoring.html',
            'Financial Dashboard': 'financial-dashboard.html',
            'Executive Dashboard': 'executive-dashboard.html',
            'Sales Intelligence Dashboard': 'sales-intelligence-dashboard.html',
            'Comparative Analysis Dashboard': 'comparative-analysis-dashboard.html',
            'Drill-Down Analytics': 'drill-down-analytics.html',
            'Predictive Analytics': 'predictive-analytics.html',
            'Heat Map & Heatmap Style': 'heat-map-heatmap-style.html',
            'User Behavior Analytics': 'user-behavior-analytics.html',
            'Cyberpunk Mobile HUD': 'cyberpunk-mobile-hud.html',
            'Neumorphism (Mobile)': 'neumorphism-mobile.html',
            'Neo Brutalism (Mobile)': 'neo-brutalism-mobile.html',
            'Claymorphism (Mobile)': 'claymorphism-mobile.html',
            'Terminal CLI (Mobile)': 'terminal-cli-mobile.html',
            'Academia (Scholarly Mobile)': 'academia-scholarly-mobile.html',
            'Bitcoin DeFi (Mobile)': 'bitcoin-defi-mobile.html',
            'Modern Dark (Cinema Mobile)': 'modern-dark-cinema-mobile.html',
            'Bold Typography (Mobile Poster)': 'bold-typography-mobile-poster.html',
            'Enterprise SaaS (Mobile)': 'enterprise-saas-mobile.html',
            'Flat Design Mobile (Touch-First)': 'flat-design-mobile-touch-first.html',
            'Inclusive Design': 'inclusive-design.html',
            'Kinetic Brutalism (Mobile)': 'kinetic-brutalism-mobile.html',
            'SaaS Mobile (High-Tech Boutique)': 'saas-mobile-high-tech-boutique.html',
            'Sketch Hand-Drawn (Mobile)': 'sketch-hand-drawn-mobile.html',
        }
        if r['Style Category'] in _handmade:
            file = _handmade[r['Style Category']]  # 唯一样张 = 精修版，不再生成自动版
            manifest.append((r, file, t))
            continue
        _slug = slug(r['Style Category'])
        file = 'demos/' + _slug + '.html'
        title = '%s / 风格样张 — ui-ux-pro-max + frontend-design' % r['Style Category']
        if r['Type'] == 'BI/Analytics':
            body, css = dashboard_body(s, t, prompt), dashboard_css(s)
        elif r['Type'] == 'Mobile':
            body, css = mobile_body(s, t, prompt), mobile_css(s)
        else:
            body, css = landing_body(s, t, prompt), landing_css(s)
        body = body.replace('__BOLT__', BOLT)
        css = css.replace('__TITLE_EXTRA__', s['title_extra'])
        page = base_css(s, fh, fb, fq, title, css).replace('__BODY__', body)
        open(os.path.join(OUT_DIR, _slug + '.html'), 'w', encoding='utf-8').write(page)
        manifest.append((r, file, t))

    # ---- 落地页结构样板：landing.csv 34 种官方结构 → 真实成品页 ----
    os.makedirs(OUT_LDIR, exist_ok=True)
    styles_by_name = load_styles_by_name()
    theme_keys = list(THEMES.keys())
    lentries = []
    for li, l in enumerate(load_landing()):
        # 落地结构样张已全部手工精修（见 pattern-demos/l*.html），重跑不再覆盖
        fam = FAM_CYCLE[li % len(FAM_CYCLE)]
        rep = styles_by_name.get(FAMILY_REP.get(fam, 'Minimalism & Swiss Style'))
        s = make_skin(rep) if rep else base_skin()
        fh, fb, fq = pick_fonts(l['Keywords'] + ' ' + l['Pattern Name'])
        file = 'l%s-%s.html' % (l['No'], slug(l['Pattern Name']))
        lentries.append((l, s, file, (fh, fb)))
    print('落地结构样板: %d（手工精修版，生成器不再覆盖）' % len(lentries))

    # ---- 目录页：Memphis Design 版完整重建（风格 + 落地结构） ----
    pent = [(p, slug(p['name']) + '.html') for p in _load_json('products.json') if os.path.exists(os.path.join(BASE, 'product-demos', slug(p['name']) + '.html'))]
    chent = [(c, slug(c['Data Type']) + '.html') for c in _load_json('charts.json') if os.path.exists(os.path.join(BASE, 'chart-demos', slug(c['Data Type']) + '.html'))]
    open(CATALOG, 'w', encoding='utf-8').write(build_catalog(manifest, [], lentries, content_styles.CONTENT_STYLES, pent, chent))
    print('产品模板卡:', len(pent), '/ 40 | 图表卡:', len(chent), '/ 25')

    # ---- 内容排版风格样张：html-anything 18 种 → 独立模板 ----
    # 内容排版样张已全部手工精修（见 content-demos/*.html），重跑不再覆盖；
    # content_styles.py 仍保留数据（目录卡提示词的数据源）
    print('内容排版样张: %d（手工精修版，生成器不再覆盖）' % len(content_styles.CONTENT_STYLES))

    print('样张生成数:', len(manifest))
    print('皮肤族分布:', dict(sorted(fam_count.items(), key=lambda x: -x[1])))
    used = sorted(set(font_log.values()))
    print('官方字体配对使用数: %d 组' % len(used))
    print('\n'.join('  ' + u for u in used[:12]))

if __name__ == '__main__':
    main()
