"""Join reel beats (beat_N.jpg from render.py --reel) into a 1080x1920 30fps MP4 with crossfades.

Usage: python3 reel.py out_dir 2.2,2.2,2.6,3.5   (seconds each beat is on screen)
Writes out_dir/reel.mp4 (H.264 + silent AAC track, which IG/TikTok/YouTube accept).
"""
import subprocess, sys, os

out, durs = sys.argv[1], [float(x) for x in sys.argv[2].split(',')]
X = 0.35  # crossfade seconds
cmd = ['ffmpeg', '-y', '-loglevel', 'error']
for i, d in enumerate(durs, 1):
    cmd += ['-loop', '1', '-framerate', '30', '-t', f'{d + X:.2f}', '-i', os.path.join(out, f'beat_{i}.jpg')]
cmd += ['-f', 'lavfi', '-t', f'{sum(durs) + X:.2f}', '-i', 'anullsrc=r=44100:cl=stereo']
# gentle 3% push-in on every beat so stills feel alive, then chain crossfades
f, prev, off = [], None, 0.0
for i, d in enumerate(durs):
    n = int((d + X) * 30)
    f.append(f"[{i}:v]scale=1080:1920,zoompan=z='1+0.03*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v{i}]")
for i in range(1, len(durs)):
    off += durs[i - 1]
    a = prev or 'v0'
    f.append(f"[{a}][v{i}]xfade=transition=fade:duration={X}:offset={off:.2f}[x{i}]")
    prev = f'x{i}'
cmd += ['-filter_complex', ';'.join(f), '-map', f'[{prev or "v0"}]', '-map', f'{len(durs)}:a',
        '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30',
        '-c:a', 'aac', '-shortest', '-movflags', '+faststart', os.path.join(out, 'reel.tmp.mp4')]
subprocess.run(cmd, check=True)
os.replace(os.path.join(out, 'reel.tmp.mp4'), os.path.join(out, 'reel.mp4'))
print('ok', os.path.join(out, 'reel.mp4'))
