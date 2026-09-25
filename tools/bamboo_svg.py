"""Generates the bamboo line illustrations used across the site (assets/img/deco/*.svg).
Deterministic (seeded) so re-running gives the same drawings."""
import random, math
OUT = 'assets/img/deco/'
GOLD = '#CDA85A'; GOLD_L = '#E2C589'; LEAF = '#5E7F3C'; LEAF_L = '#8DB26A'; CULM = '#2E5A3A'; CULM_L = '#4F7F4E'

def leaf(x, y, ang, L, w, fill, stroke, op=1):
    p = f"M0 0 C {L*.22:.1f} {-w:.1f}, {L*.6:.1f} {-w*1.05:.1f}, {L:.1f} 0 C {L*.6:.1f} {w*.8:.1f}, {L*.22:.1f} {w*.75:.1f}, 0 0 Z"
    vein = f"M{L*.05:.1f} 0 L{L*.92:.1f} 0"
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f})" opacity="{op}">'
            f'<path d="{p}" fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>'
            f'<path d="{vein}" stroke="{stroke}" stroke-width=".7" opacity=".7"/></g>')

def culm(x, top, bottom, w, seg, rnd, lean=0):
    out = []
    y = bottom; i = 0
    while y > top:
        h = seg * rnd.uniform(.85, 1.15); y0 = max(top, y - h)
        dx0 = lean * (bottom - y0) / (bottom - top); dx1 = lean * (bottom - y) / (bottom - top)
        out.append(f'<path d="M{x+dx1-w/2:.1f} {y:.1f} L{x+dx0-w/2:.1f} {y0+3:.1f} Q{x+dx0:.1f} {y0-1:.1f} {x+dx0+w/2:.1f} {y0+3:.1f} L{x+dx1+w/2:.1f} {y:.1f} Z" '
                   f'fill="url(#g-culm)" stroke="{GOLD}" stroke-width="1" stroke-opacity=".55"/>')
        out.append(f'<rect x="{x+dx0-w/2-2:.1f}" y="{y0-1:.1f}" width="{w+4:.1f}" height="4" rx="2" fill="{GOLD}" opacity=".85"/>')
        out.append(f'<path d="M{x+dx1-w/2+w*.28:.1f} {y-6:.1f} L{x+dx0-w/2+w*.28:.1f} {y0+8:.1f}" stroke="{GOLD_L}" stroke-width="1.2" opacity=".35"/>')
        y = y0; i += 1
    return out

def spray(x, y, side, rnd, n=5, scale=1.0):
    out = [f'<path d="M{x:.1f} {y:.1f} q {side*30*scale:.1f} -12 {side*62*scale:.1f} -30" stroke="{GOLD}" stroke-width="1.3" fill="none" opacity=".8"/>']
    bx, by = x + side*62*scale, y - 30*scale
    for k in range(n):
        base = (18 if side > 0 else 162) + (k - n/2) * 17 * side + rnd.uniform(-6, 6)
        L = rnd.uniform(70, 110) * scale; w = L * .14
        fill = LEAF if k % 2 else LEAF_L
        out.append(leaf(bx - side*k*9*scale, by + k*6*scale, base, L, w, fill, GOLD, op=.92))
    return out

def svg(w, h, body, extra=''):
    defs = (f'<defs><linearGradient id="g-culm" x1="0" x2="1"><stop offset="0" stop-color="{CULM}"/>'
            f'<stop offset=".45" stop-color="{CULM_L}"/><stop offset="1" stop-color="{CULM}"/></linearGradient></defs>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" fill="none">{defs}{extra}{"".join(body)}</svg>'

import os; os.makedirs(OUT, exist_ok=True)

# 1. Tall grove edge (for page sides): three culms + leaf sprays
rnd = random.Random(7); body = []
for (x, w, lean, top) in [(60, 26, -8, 60), (120, 18, 10, 150), (170, 13, -4, 260)]:
    body += culm(x + 40, top, 1200, w, 150, rnd, lean)
for (x, y, s, n, sc) in [(112, 330, 1, 6, 1.1), (152, 520, -1, 5, 1), (168, 760, 1, 6, 1.05), (205, 420, 1, 4, .85), (95, 900, 1, 5, 1), (216, 980, -1, 4, .8)]:
    body += spray(x, y, s, rnd, n, sc)
open(OUT + 'bamboo-grove.svg', 'w').write(svg(340, 1200, body))

# 2. Leaf sprig ornament (for section kickers, dividers)
rnd = random.Random(3); body = []
body.append(f'<path d="M10 40 Q 60 34 110 22" stroke="{GOLD}" stroke-width="1.4"/>')
for i, (x, y, a, L) in enumerate([(40, 37, -28, 48), (58, 34, 22, 44), (78, 30, -34, 42), (92, 27, 18, 36), (108, 22, -8, 30)]):
    body.append(leaf(x, y, a, L, L*.15, LEAF_L if i % 2 else LEAF, GOLD))
open(OUT + 'bamboo-sprig.svg', 'w').write(svg(160, 60, body))

# 3. Single culm with node (for the node divider / hero frame)
rnd = random.Random(11); body = culm(30, 0, 400, 20, 120, rnd, 0) + spray(38, 150, 1, rnd, 4, .8)
open(OUT + 'bamboo-culm.svg', 'w').write(svg(190, 400, body))

# 4. Horizontal leaf garland (wide divider)
rnd = random.Random(5); body = [f'<path d="M0 30 Q 300 18 600 30" stroke="{GOLD}" stroke-width="1.2" opacity=".7"/>']
for i in range(14):
    x = 30 + i * 40 + rnd.uniform(-6, 6); y = 30 - 8 * math.sin(i / 13 * math.pi)
    body.append(leaf(x, y, (-35 if i % 2 else 35) + rnd.uniform(-10, 10), rnd.uniform(34, 50), 6, LEAF_L if i % 3 else LEAF, GOLD, .9))
open(OUT + 'bamboo-garland.svg', 'w').write(svg(620, 60, body))
print('ok')
