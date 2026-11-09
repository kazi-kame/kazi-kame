#!/usr/bin/env python3
"""Rebuild the self-contained animated ASCII terminal hero for the GitHub profile.

Dependencies: Pillow (pip install pillow). Font files are not bundled.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
W, H = 960, 396
FRAMES, FPS = 48, 12
BG = (7, 13, 19)
PANEL = (12, 22, 29)
EDGE = (42, 65, 76)
MAIN = (221, 240, 235)
ACCENT = (125, 224, 169)
CYAN = (114, 198, 216)
MUTED = (110, 148, 154)
GOLD = (238, 189, 110)
DIM = (48, 74, 78)

NORMAL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
font = ImageFont.truetype(NORMAL, 16)
small = ImageFont.truetype(NORMAL, 13)
mini = ImageFont.truetype(NORMAL, 12)
headline = ImageFont.truetype(BOLD, 48)
subheading = ImageFont.truetype(BOLD, 17)
ascii_font = ImageFont.truetype(NORMAL, 13)
CELLX, CELLY = 8.7, 12.5
Nx, Ny = 45, 17
RX, RY = 10.1, 6.3
CX, CY = (Nx-1) / 2, (Ny-1) / 2
# A few deterministic stars, independent from changes in planetary motion.
rg = random.Random(2411)
stars = [(rg.randrange(1,Nx-1),rg.randrange(1,Ny-1),rg.random()) for _ in range(27)]

# ASCII character chosen by computed intensity rather than using a static image.
RAMP = ' .,:;irsXA253hMHGS#9B&@'

def planet(t: float):
    out = {}  # (charx, chary) -> (character, color)
    # Background stars.
    for x,y,v in stars:
        if abs(x-CX) < RX+3 and abs(y-CY) < RY+2:
            continue
        if math.sin(2*math.pi*(t*(0.8+v*.5)+v)) > .18:
            out[x,y] = ('.' if v<.6 else '+', DIM if v < .65 else MUTED)
    # Thin elliptical Saturn rings, back and front arc as layered geometry.
    for layer in (0, 1):
        for j in range(1200):
            th = j * (2 * math.pi / 1200)
            # Perspective projected rings; tilt gives the animated 3D impression.
            r = 15.3 + 2.0 * math.sin(j * .019 + t * 2*math.pi*.58)
            x = CX + r*math.cos(th)
            y = CY + 0.27*r*math.sin(th) - 0.12*r*math.cos(th)
            iy, ix = round(y), round(x)
            if not(0 <= ix < Nx and 0 <= iy < Ny): continue
            # behind first and in front later
            front = math.sin(th) >= 0
            if int(front) != layer: continue
            # remove some ring pixels and use glyphs for grainy physical-looking ASCII.
            if (j//5 + math.floor(t*24)) % 11 == 0: continue
            char = '=' if abs(math.sin(th)) < .25 else '-' if math.sin(th) > 0 else ':'
            out[ix,iy] = (char, GOLD if front else (101, 117, 108))
        if layer == 0:
            # Planet sphere, with slow longitude rotation and bands.
            for yy in range(Ny):
                for xx in range(Nx):
                    px = (xx - CX) / RX
                    py = (yy - CY) / RY
                    rr = px*px + py*py
                    if rr > 1.0: continue
                    z = math.sqrt(max(0, 1 - rr))
                    lon = math.atan2(px, z) + t*2*math.pi*.75
                    lat = math.asin(max(-1.0, min(1.0, -py)))
                    band = .24*math.sin(10.5*lat + .35*math.sin(3.5*lon))
                    cloud = .10*math.sin(4*lon + 15*lat) + .045*math.sin(15*lon+6*lat)
                    lum = max(0.0, min(1.0, .49 + .40*(z*.7 - px*.55 + .38*py) + band + cloud))
                    char = RAMP[int(lum*(len(RAMP)-1))]
                    col = (int(103 + lum*109), int(118 + lum*95), int(109 + lum*67))
                    out[xx, yy] = (char, col)
    return out


def write(d, x, y, txt, color=MAIN, f=font):
    d.text((x,y), txt, fill=color, font=f, stroke_width=0)


def make_frame(frame_idx: int):
    t = frame_idx / FRAMES
    im = Image.new('RGB',(W,H), BG)
    d = ImageDraw.Draw(im)
    # Outer window.
    d.rounded_rectangle([10,10,W-11,H-11], radius=14, fill=PANEL, outline=EDGE, width=2)
    d.rounded_rectangle([10,10,W-11,51], radius=13, fill=(17, 30, 39))
    d.rectangle([11,37,W-12,51], fill=(17, 30, 39))
    d.line([11,51,W-11,51], fill=EDGE, width=1)
    for i,c in enumerate([(212,102,99),(225,174,92),(121,196,141)]):
        d.ellipse([32+i*24,27,42+i*24,37], fill=c)
    write(d, 119, 22, 'kazi@observatory  ~/simulation/control-room', MUTED, mini)
    write(d, W-187, 22, '●  SESSION 001', ACCENT, mini)

    # Left column.
    write(d, 48, 80, 'INITIALIZING RESEARCH CONSOLE...', CYAN, mini)
    d.line([48,107,523,107], fill=EDGE)
    write(d, 46, 125, 'ANAS KAZI', MAIN, headline)
    write(d, 50, 197, 'PHYSICS  /  CHAOS  /  COMPUTATION', ACCENT, subheading)
    write(d, 49, 237, 'I study how simple rules create', (170,198,194), font)
    write(d, 49, 261, 'extraordinarily complex behavior.', (170,198,194), font)

    # Animated command lines / cursor, loop reset.
    d.rounded_rectangle([47,309,521,354], radius=5, fill=(8,17,23), outline=(31,60,65), width=1)
    commands = ['python explore.py --system=saturn',
                'python measure.py --signal=chaos',
                'python evolve.py --model=orbits']
    cmd_i = int(t * 3) % 3
    sub = (t * 3) % 1
    string = commands[cmd_i]
    count = min(len(string), int(sub * (len(string)+7)))
    write(d, 62, 319, '$', ACCENT, font)
    write(d, 84, 319, string[:count], CYAN, font)
    if sub < .76 and frame_idx % 8 < 5:
        textlen = d.textbbox((0,0), string[:count], font=font)[2]
        d.rectangle([85+textlen,320,87+textlen,338], fill=ACCENT)

    # Divider.
    d.line([546,73,546,359], fill=EDGE, width=1)
    write(d, 567, 81, 'ASCII PLANETARY FEED', ACCENT, mini)
    write(d, 567, 104, 'SATURN // SYNTHETIC VIEW', MUTED, mini)

    # ASCII art simulation.
    positions = planet(t)
    ox, oy = 553, 119
    for (xx,yy), (ch, col) in positions.items():
        d.text((ox+xx*CELLX,oy+yy*CELLY), ch, font=ascii_font, fill=col)
    # Footer; explanatory telemetry rather than misleading live measurement.
    d.line([48,367,913,367], fill=EDGE, width=1)
    write(d, 49, 372, 'NUMERICAL WORLDS. REAL QUESTIONS.', MUTED, mini)
    write(d, 707, 372, 'LOOP  /  NOT LIVE DATA', MUTED, mini)
    return im


def main():
    frames=[]
    for k in range(FRAMES):
        img = make_frame(k)
        if k==21:
            img.save(ASSETS/'orbital-terminal-poster.png', optimize=True)
        frames.append(img.quantize(colors=96, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE))
    frames[0].save(ASSETS / 'orbital-terminal.gif', save_all=True, append_images=frames[1:],
                   duration=round(1000/FPS), loop=0, optimize=True, disposal=2)
    print('Saved', ASSETS / 'orbital-terminal.gif')

if __name__ == '__main__':
    main()
