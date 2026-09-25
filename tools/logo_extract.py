"""Rebuild the transparent logo files from assets/img/logo-source.png (white background).

- removes the white background and the white halo around edges (colour-to-alpha on the edge band only)
- removes the light drop shadow under the plate
- recolours the wordmark for the dark site: cream name, gold tagline
Outputs: logo-plate(.png/.webp), logo-plate-160, logo-lockup(.png/.webp)
Run: python3 tools/logo_extract.py   (needs Pillow, numpy, scipy)
"""
from PIL import Image
import numpy as np
from scipy import ndimage

SRC = 'assets/img/logo-source.png'
OUT = 'assets/img/'

im = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W, _ = im.shape

# 1. background = near-white region connected to the image border
near = im.min(axis=2) > 228
lab, _ = ndimage.label(near)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
band = ndimage.binary_dilation(bg, iterations=4) & ~bg
alpha = np.ones((H, W), np.float32)
alpha[bg] = 0
alpha[band] = np.clip((255 - im.min(axis=2)) / 255 * 1.15, 0, 1)[band]
rgb = im.copy()
m = band & (alpha > 0.02)
for c in range(3):
    ch = rgb[..., c]
    ch[m] = np.clip((ch[m] - 255 * (1 - alpha[m])) / alpha[m], 0, 255)
alpha[alpha < 0.04] = 0

# plate / wordmark split = first empty row in the lower half
rows = (alpha > 0.08).sum(1)
split = next(y for y in range(int(H * 0.45), H) if rows[y] == 0)

# 2. drop shadow under the plate: light, low-saturation pixels reachable from the background
mx, mn = rgb.max(2), rgb.min(2)
shadowish = ((mx - mn) < 34) & (mn > 150)
shadowish[split:] = False
seed = alpha < 0.8
reach = ndimage.binary_propagation(seed, mask=seed | shadowish)
sh = reach & shadowish & (alpha > 0)
alpha[sh] = 0
soft = ndimage.binary_dilation(sh, iterations=2) & ~sh & (alpha > 0)
alpha[soft] *= 0.5

# 3. recolour the wordmark for a dark background. The lettering is ink on white, so its
#    coverage (alpha) comes from how far each pixel is from white — this keeps the letter
#    counters (inside of o, e…) transparent and the edges smooth.
src = im  # original colours, before any unmixing
txt = np.zeros((H, W), bool); txt[split:] = True
ink = np.clip((255 - src.min(axis=2)) / 255, 0, 1)
cover = np.clip((ink - 0.06) / 0.62, 0, 1)
alpha[txt] = cover[txt]
# the tagline is the last line of lettering: gold; everything above it: cream
has_ink = (cover > 0.2).sum(1) > 0
lines, y = [], split
while y < H:
    if has_ink[y]:
        y0 = y
        while y < H and has_ink[y]: y += 1
        lines.append((y0, y))
    y += 1
warm = np.zeros((H, W), bool)
warm[lines[-1][0] - 2:] = True
rgb[txt & ~warm] = (237, 228, 207)   # cream: name, "Côte d'Ivoire", rules
rgb[txt & warm] = (214, 178, 104)    # gold: tagline

rgba = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), 'RGBA')
def crop(img):
    return img.crop(img.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox())
lock = crop(rgba)
plate = crop(rgba.crop((0, 0, W, split)))
for name, img in (('logo-lockup', lock), ('logo-plate', plate)):
    img.save(OUT + name + '.png', optimize=True)
    img.save(OUT + name + '.webp', 'WEBP', quality=90, method=6)
small = plate.copy(); small.thumbnail((160, 160))
small.save(OUT + 'logo-plate-160.png', optimize=True)
small.save(OUT + 'logo-plate-160.webp', 'WEBP', quality=90, method=6)
print('lockup', lock.size, 'plate', plate.size, 'shadow px removed', int(sh.sum()))
