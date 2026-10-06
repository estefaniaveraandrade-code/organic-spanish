#!/usr/bin/env python3
"""Overlay Spanish verbs (red) + English translations (yellow) on the coffee video."""
import subprocess, sys

SRC, OUT = sys.argv[1], sys.argv[2]
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
RED, YEL, WHITE = "0xFF2A2A", "0xFFE600", "white"
DUR, RECAP = 37.23, 4.5  # source length, recap card length

# (spanish, english, start, end) -- timed from the speech energy of the audio
V = [
 ("ponemos","we put",4.13,6.5), ("tapamos","we cover",6.63,8.6),
 ("encendemos","we turn on",8.83,10.3), ("colocamos","we place",10.37,12.9),
 ("abrimos","we open",13.18,14.6), ("ponemos","we put",14.67,16.6),
 ("tapamos","we cover",16.86,18.1), ("mezclamos","we mix",18.29,21.0),
 ("ponemos","we put",23.44,24.8), ("abrimos","we open",24.98,25.45),
 ("espolvoreamos","we sprinkle",25.49,29.0), ("mezclamos","we mix",29.61,31.2),
 ("olemos","we smell",31.34,33.8), ("disfrutamos","we enjoy",34.15,DUR-0.05),
]
# abrimos (2nd) is very short in the audio: hold it a little longer
V[9] = ("abrimos","we open",24.98,25.49)

def dt(text, color, size, y, s, e, border=10, extra=""):
    pop = f"if(lt(t-{s},0.18),{size}*(0.6+0.4*(t-{s})/0.18),{size})"
    return (f"drawtext=fontfile={FONT}:text='{text}':fontcolor={color}:fontsize='{pop}':"
            f"x=(w-text_w)/2:y={y}:borderw={border}:bordercolor=black:"
            f"shadowx=4:shadowy=4:shadowcolor=black@0.6:enable='between(t,{s},{e})'{extra}")

def plain(text, color, size, y, s, e, border=6):
    return (f"drawtext=fontfile={FONT}:text='{text}':fontcolor={color}:fontsize={size}:"
            f"x=(w-text_w)/2:y={y}:borderw={border}:bordercolor=black:enable='between(t,{s},{e})'")

f = []
# hook title (top safe area) + subtitle
f.append(plain("LET’S MAKE COFFEE", WHITE, 78, 230, 0, 4.1))
f.append(plain("IN SPANISH", YEL, 96, 320, 0, 4.1))
f.append(plain("9 verbos en 1ra persona plural", WHITE, 46, 450, 0.3, 4.1, 5))
for i,(es,en,s,e) in enumerate(V):
    f.append(plain(f"{i+1}/14", WHITE, 44, 230, s, e, 5))
    f.append(plain("nosotros...", WHITE, 46, 1120, s, e, 5))
    f.append(dt(es, RED, 150 if len(es) < 11 else 118, 1190, s, e))
    f.append(dt(en, YEL, 96, 1370, s+0.12, e, 8))
# progress bar (top)
f.append("drawbox=x=0:y=0:w=iw:h=18:color=black@0.5:t=fill")
f.append(f"drawbox=x=0:y=0:w='iw*min(t/{DUR},1)':h=18:color={RED}@1:t=fill")

# recap card appended on a frozen, darkened last frame
total = DUR + RECAP
f.append(f"tpad=stop_mode=clone:stop_duration={RECAP}")
f.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=black@0.78:t=fill:enable='gte(t,{DUR})'")
f.append(plain("REPASO", WHITE, 70, 200, DUR, total))
uniq = []
for es,en,_,_ in V:
    if es not in [u[0] for u in uniq]: uniq.append((es,en))
for i,(es,en) in enumerate(uniq):
    y = 300 + i*128
    f.append(plain(es, RED, 66, y, DUR, total, 7))
    f.append(plain(en, YEL, 42, y+70, DUR, total, 5))
f.append(plain("Sígueme para más español", WHITE, 52, 1530, DUR+1.0, total))
f.append(plain("Follow for more Spanish", YEL, 52, 1605, DUR+1.0, total))

vf = ",".join(f)
subprocess.run(["ffmpeg","-y","-v","error","-i",SRC,"-vf",vf,"-af",f"apad=pad_dur={RECAP}",
  "-t",str(total),"-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","160k","-movflags","+faststart",OUT],check=False)
