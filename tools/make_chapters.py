"""Turn the per-part captures of record_demo.py into walkthrough chapters.

    python tools/record_demo.py walk --hq --headless      # then rename tools/out/capture -> tools/out/cap_walk
    python tools/record_demo.py live --hq --headless      # ... cap_live, cap_bench, cap_quiz
    python tools/make_chapters.py [walk live bench quiz]

For each part it writes:
    tools/out/chapters/NN-name.mp4     full speed, 1080p, no audio (upload these; *.mp4 is not committed)
    docs/walkthrough/NN-name.webp      a silent loop for docs/WALKTHROUGH.md (sped up, 960 px wide)
    docs/walkthrough/NN-name.jpg       a still, shown where animated images are not
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "out")
MP4 = os.path.join(OUT, "chapters")
DOCS = os.path.join(ROOT, "docs", "walkthrough")
FF = shutil.which("ffmpeg") or "ffmpeg"

# part -> (file name, loop speed-up, where the still is taken as a share of the clip)
PARTS = {
    "walk": ("01-walk-the-hall", 1.5, 0.55),
    "live": ("02-live-ticket", 4.0, 0.97),
    "bench": ("03-bench-work", 2.5, 0.45),
    "quiz": ("04-work-orders", 4.0, 0.12),
}
LOOP_W, LOOP_FPS = 960, 8


def run(args):
    p = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error"] + args, capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stderr[-1500:])


def seconds(listfile):
    with open(listfile) as f:
        return sum(float(x.split()[1]) for x in f if x.startswith("duration"))


def main():
    parts = [a for a in sys.argv[1:] if a in PARTS] or list(PARTS)
    os.makedirs(MP4, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    for part in parts:
        name, speed, still_at = PARTS[part]
        lst = os.path.join(OUT, f"cap_{part}", "list.txt")
        if not os.path.exists(lst):
            print(f"skip {part}: no capture at {lst}")
            continue
        dur = seconds(lst)
        src = ["-f", "concat", "-safe", "0", "-i", lst]
        mp4 = os.path.join(MP4, name + ".mp4")
        run(src + ["-vf", "fps=30,scale=1920:1080:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "22",
                   "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4])
        webp = os.path.join(DOCS, name + ".webp")
        # The last frame is held for a beat so the loop point is easy to see.
        run(["-i", mp4, "-vf", f"setpts=PTS/{speed},fps={LOOP_FPS},scale={LOOP_W}:-2:flags=lanczos,tpad=stop_mode=clone:stop_duration=1.5",
             "-c:v", "libwebp_anim", "-loop", "0", "-quality", "55", "-compression_level", "5", "-an", webp])
        jpg = os.path.join(DOCS, name + ".jpg")
        run(["-ss", f"{dur * still_at:.2f}", "-i", mp4, "-frames:v", "1", "-vf", f"scale={LOOP_W}:-2:flags=lanczos", "-q:v", "3", jpg])
        print(f"{part:<6} {dur:5.1f}s  mp4 {os.path.getsize(mp4) / 1e6:5.1f} MB   loop {dur / speed + 1.5:4.1f}s {os.path.getsize(webp) / 1e6:5.1f} MB")


if __name__ == "__main__":
    main()
