#!/usr/bin/env python3
"""Render the animated Lorenz-system GitHub profile hero.

A real numerical Lorenz trajectory (RK4) powers the moving plot; the terminal
text and timings are drawn explicitly to prevent GIF text-generation errors.
Dependencies: Pillow only. A system-installed monospace font is used, not bundled.
Usage: python tools/render_chaos_terminal.py
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
W, H = 1200, 592
N_FRAMES, MS_PER_FRAME = 134, 100
OUT_GIF = ASSETS / "chaos-terminal.gif"
OUT_PNG = ASSETS / "chaos-terminal-poster.png"

# Terminal palette (RGB): midnight charcoal, acid green, icy cyan, gold, red.
BG=(4,10,13); PANEL=(8,17,22); HEAD=(13,27,30)
EDGE=(36,93,84); GRID=(20,49,48); MINT=(56,250,159)
GREEN=(105,240,161); CYAN=(113,225,225); WHITE=(212,241,228)
DIM=(85,139,134); SUBTLE=(51,100,97); GOLD=(255,204,111)
RED=(255,121,121)

FONT_LOCATIONS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
]
BOLD_LOCATIONS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf',
]
def get_font(paths, size):
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
FONT = get_font(FONT_LOCATIONS,18)
FONT_SM = get_font(FONT_LOCATIONS,13)
FONT_TINY = get_font(FONT_LOCATIONS,11)
FONT_BOLD = get_font(BOLD_LOCATIONS,18)
FONT_HEAD = get_font(BOLD_LOCATIONS,21)

# Physical parameters for the classical Lorenz '63 system.
SIGMA, RHO, BETA = 10.0, 28.0, 8.0/3.0
DT=0.007

def rhs(s):
    x,y,z=s
    return (SIGMA*(y-x), x*(RHO-z)-y, x*y-BETA*z)

def add(s,ds,h):
    return (s[0]+h*ds[0],s[1]+h*ds[1],s[2]+h*ds[2])

def integrate(n=12500):
    a=(0.1,0.0,0.2); result=[]
    for k in range(n+900):
        p=rhs(a); q=rhs(add(a,p,DT/2)); r=rhs(add(a,q,DT/2)); u=rhs(add(a,r,DT))
        a=tuple(a[i]+DT/6*(p[i]+2*q[i]+2*r[i]+u[i]) for i in range(3))
        if k >= 900: result.append(a)
    return result

TRAJECTORY = integrate()
# Diagram extents. x horizontal and z vertical (x-z projection of 3D flow).
PLOT=(669,131,1158,484)
XMIN,XMAX=-22.5,22.5
ZMIN,ZMAX=1.5,51.5

def position(p):
    x,y,z=p
    left,top,right,bottom=PLOT
    return (int(left+(x-XMIN)/(XMAX-XMIN)*(right-left)),
            int(bottom-(z-ZMIN)/(ZMAX-ZMIN)*(bottom-top)))

PXY=[position(p) for p in TRAJECTORY]

# Timeline: status lines are terminal-typed at ~60 characters per second.
# The exact jokes are intentionally preserved as agreed.
LINES=[
    (0,   124, '$ ./kazi_kame.exe', MINT),
    (9,   155, '> initializing questionable life choices...', WHITE),
    (22,  198, '[ OK ] chaos kernel loaded', GREEN),
    (29,  226, '[ OK ] attractor renderer online', GREEN),
    (40,  276, '[INFO] physics undergrad', CYAN),
    (48,  304, '[INFO] making deterministic systems', CYAN),
    (56,  332, '       regret being deterministic', WHITE),
    (67,  375, '[WARN] results statistically significant', GOLD),
    (75,  403, '       to my delusions', GOLD),
    (86,  446, '[ERR ] interested in chaos?', RED),
    (94,  474, '       study my dating life', WHITE),
    (105, 512, '> stability not found_', MINT),
]

def tiny_text(draw, xy, s, color=WHITE, font=FONT_SM):
    draw.text(xy,s,fill=color,font=font)

def make_static():
    im=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(im)
    # Terminal frame and chrome.
    d.rounded_rectangle((10,10,W-11,H-11), radius=16, fill=PANEL, outline=EDGE, width=2)
    d.rounded_rectangle((11,11,W-12,67),radius=15,fill=HEAD)
    d.rectangle((12,39,W-13,67), fill=HEAD)
    d.line((11,67,W-11,67),fill=(42,115,100),width=2)
    for i,c in enumerate(((255,111,103),(255,207,100),(72,231,153))):
        x=31+i*23
        d.ellipse((x,31,x+11,42),fill=c)
    tiny_text(d,(118,25),'kazi_kame.exe',MINT,FONT_HEAD)
    tiny_text(d,(306,31),'//  CHAOS RESEARCH TERMINAL',CYAN,FONT_SM)
    tiny_text(d,(1004,32),'[  ONLINE  ]',GREEN,FONT_SM)
    d.line((629,90,629,527),fill=EDGE,width=1)
    tiny_text(d,(47,89),'SESSION 01 / INITIAL CONDITIONS: QUESTIONABLE',DIM,FONT_SM)
    d.line((48,109,597,109),fill=GRID,width=1)
    tiny_text(d,(670,90),'PHASE SPACE  /  LORENZ ATTRACTOR',GREEN,FONT_SM)
    tiny_text(d,(1082,91),'SIMULATED',DIM,FONT_TINY)
    # subtle right panel and grid.
    d.rounded_rectangle((649,113,1175,502),radius=10,fill=(5,16,19),outline=(30,80,74),width=1)
    x0,y0,x1,y1=PLOT
    for xtick in (-20,-10,0,10,20):
        x=round(x0+(xtick-XMIN)/(XMAX-XMIN)*(x1-x0))
        d.line((x,y0,x,y1),fill=GRID,width=1)
        tiny_text(d,(x-10,y1+6),str(xtick),SUBTLE,FONT_TINY)
    for ztick in (10,20,30,40,50):
        y=round(y1-(ztick-ZMIN)/(ZMAX-ZMIN)*(y1-y0))
        d.line((x0,y,x1,y),fill=GRID,width=1)
        tiny_text(d,(x0-25,y-6),str(ztick),SUBTLE,FONT_TINY)
    tiny_text(d,(1157,487),'x',DIM,FONT_TINY)
    tiny_text(d,(650,120),'z',DIM,FONT_TINY)
    # Full attractor shown as dim reference; a bright particle will run on top.
    # Break into segments to avoid massive polyline artifacts at attractor excursions.
    ghost=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(ghost)
    # The 2D projection is mathematically generated, not a traced illustration.
    gd.line(PXY[:10800],fill=(43,183,124,45),width=1,joint='curve')
    glow=ghost.filter(ImageFilter.GaussianBlur(7))
    im=Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB')
    im=Image.alpha_composite(im.convert('RGBA'),ghost).convert('RGB')
    d=ImageDraw.Draw(im)
    # Footer data strip; no claim that the GIF measures live data.
    d.line((28,548,1172,548),fill=EDGE,width=1)
    tiny_text(d,(42,555),'github.com/kazi-kame',GREEN,FONT_TINY)
    tiny_text(d,(668,555),'sigma=10  rho=28  beta=8/3   //  RK4 simulation',DIM,FONT_TINY)
    # micro decoration / fine lattice bars
    for x in range(1036,1115,7):
        d.rectangle((x,88,x+3,90),fill=SUBTLE)
    return im

STATIC = make_static()

def frame_at(index):
    out=STATIC.copy().convert('RGBA')
    # Mathematical trajectory: a bright moving tip and decaying phosphor tail.
    # Temporal motion is numerical evolution, not merely a brightness effect.
    end=1250+index*29
    spans=[(500,360,(20,124,94,38),2),
           (360,230,(36,195,118,70),2),
           (230,120,(50,236,147,130),2),
           (120,45,(91,255,193,205),3),
           (45,0,(207,255,225,255),3)]
    trace=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(trace)
    for back_start,back_end,c,width in spans:
        a=max(0,end-back_start); b=end-back_end
        if b>a+2:
            td.line(PXY[a:b],fill=c,width=width,joint='curve')
    blur1=trace.filter(ImageFilter.GaussianBlur(8))
    blur2=trace.filter(ImageFilter.GaussianBlur(3))
    out=Image.alpha_composite(out,blur1)
    out=Image.alpha_composite(out,blur2)
    out=Image.alpha_composite(out,trace)
    d=ImageDraw.Draw(out)
    cx,cy=PXY[end]
    d.ellipse((cx-9,cy-9,cx+9,cy+9),fill=(39,244,160,46))
    d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=(145,255,197,190))
    d.ellipse((cx-2,cy-2,cx+2,cy+2),fill=(235,255,234,255))
    # Actual changing coordinates tied to the integrated path.
    x,y,z=TRAJECTORY[end]
    d.rounded_rectangle((852,460,1139,480),radius=3,fill=(7,22,22,225))
    tiny_text(d,(860,464),f'x={x:+06.2f}   y={y:+06.2f}   z={z:05.2f}',CYAN,FONT_TINY)
    # Syntax-colored status lines, appearing at a controlled typing speed.
    latest=None
    for start,py,s,col in LINES:
        if index<start: continue
        visible=min(len(s),max(0,(index-start+1)*6))
        if visible:
            d.text((47,py),s[:visible],fill=col,font=FONT)
            latest=(py,s[:visible])
    # Blinking insertion cursor following the last typed line.
    if latest and index % 8 < 5:
        py,shown=latest
        width=d.textbbox((0,0),shown,font=FONT)[2]
        d.rectangle((49+width,py+3,51+width,py+20),fill=MINT)
    # The terminal heartbeat subtly moves independent of the simulation.
    if index%10<6:
        d.line((1111,37,1128,37,1133,28,1138,47,1143,32,1147,37,1163,37),
               fill=MINT,width=2)
    # Light scanline texture intentionally subdued; improves retro feel.
    overlay=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(overlay)
    for yy in range(75,525,5):
        od.line((12,yy,1188,yy),fill=(0,0,0,8),width=1)
    out=Image.alpha_composite(out,overlay)
    return out.convert('RGB')


def main():
    # Save a fully revealed still for easy preview outside the GIF loop.
    frame_at(116).save(OUT_PNG,optimize=True)
    # A shared adaptive palette keeps color consistent frame-to-frame.
    # Include a mature frame with all syntax colors in the palette.
    palette_img=frame_at(116).quantize(colors=144,method=Image.Quantize.MEDIANCUT,
                                       dither=Image.Dither.NONE)
    frames=[]
    for i in range(N_FRAMES):
        frames.append(frame_at(i).quantize(palette=palette_img,dither=Image.Dither.NONE))
        if i%25==0:
            print('rendered',i+1,'/',N_FRAMES,flush=True)
    frames[0].save(OUT_GIF,save_all=True,append_images=frames[1:],duration=MS_PER_FRAME,
                   loop=0,disposal=2,optimize=True)
    print('GIF:',OUT_GIF,'bytes:',OUT_GIF.stat().st_size)
    print('Poster:',OUT_PNG,'bytes:',OUT_PNG.stat().st_size)

if __name__=='__main__': main()
