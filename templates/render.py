"""Render Ozara social slides from a JSON spec.

Usage:
  python3 render.py spec.json out_dir            # 1080x1350 carousel JPEGs (slide_N.jpg)
  python3 render.py spec.json out_dir --reel     # 1080x1920 frames (beat_N.jpg) for reel.sh

spec.json:
  {"accent": "sugar|pressure|cholesterol|brand",
   "slides": [ {"theme": "dark|light", "html": "<body html>"} , ... ]}
  (A slide may also be a plain HTML string = dark theme.)

Building blocks (classes):
  .k kicker | h1 headline | span.g gradient | span.a accent color | p body
  .pill CTA | .chips/.chip tags
  .big   giant number (lab result style);   .big small = unit/label
  .bars  > .bar[data-v=0..100] with <b>label</b><i>value</i>   (horizontal bar chart)
  .split > .col.muted + .col.ozara, each with .k, h2, p      (side-by-side comparison)
  .range > .seg (3 segments) + .marker[style="left:NN%"]     (range bar)
  .src   small source line
"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = open(os.path.join(HERE, 'logo.svg')).read()
G = "linear-gradient(100deg,#B966F8,#DD8929)"
ACCENTS = {  # one accent per condition; logo, type and gradient stay constant
    "sugar": "#F2A93B", "pressure": "#FF7A6B", "cholesterol": "#A98BFF", "brand": "#C9B8F2"}
ACCENTS_ON_LIGHT = {  # deeper shades for contrast on the cream background
    "sugar": "#B86A00", "pressure": "#D2412E", "cholesterol": "#6A49D6", "brand": "#6A49D6"}
THEMES = {
    "dark": dict(bg="radial-gradient(120% 80% at 85% 0%,#2a1650 0%,#0E0B24 55%,#090717 100%)",
                 fg="#F4F1FA", body="#CFC9DE", dim="#8C84A6", line="#4A3D73", card="rgba(255,255,255,.06)"),
    "light": dict(bg="linear-gradient(160deg,#FBF7F1 0%,#F3ECE2 100%)",
                  fg="#17122E", body="#4A4560", dim="#8A8399", line="#D8CFC3", card="rgba(23,18,46,.05)"),
}

def page(slide, n, total, accent, reel):
    if isinstance(slide, str):
        slide = {"theme": "dark", "html": slide}
    t = THEMES[slide.get("theme", "dark")]
    light = slide.get("theme") == "light"
    A = (ACCENTS_ON_LIGHT if light else ACCENTS).get(accent, ACCENTS["brand"])
    H = 1920 if reel else 1350
    top, bottom = (300, 360) if reel else (150, 190)
    counter = "" if reel else f'<div class="n">{n} / {total}</div>'
    return f"""<html><head><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:{H}px;background:{t['bg']};color:{t['fg']};font-family:'Inter';position:relative;overflow:hidden}}
.wrap{{position:absolute;left:96px;right:96px;top:{top}px;bottom:{bottom}px;display:flex;flex-direction:column;justify-content:center}}
.k{{font-size:34px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:{A};margin-bottom:40px}}
h1{{font-family:'Inter Display','Inter';font-weight:700;font-size:104px;line-height:1.04;letter-spacing:-.025em}}
h2{{font-family:'Inter Display','Inter';font-weight:700;font-size:62px;line-height:1.08;letter-spacing:-.02em}}
.g{{background:{G};-webkit-background-clip:text;color:transparent}}
.a{{color:{A}}}
p{{font-size:46px;line-height:1.35;color:{t['body']};margin-top:48px}}
.src{{font-size:28px;color:{t['dim']};margin-top:40px}}
.logo{{position:absolute;left:96px;bottom:{'150' if reel else '90'}px;width:200px}}
.n{{position:absolute;right:96px;bottom:92px;font-size:30px;color:{t['dim']};font-weight:500}}
.bar0{{position:absolute;left:96px;top:{'200' if reel else '96'}px;width:120px;height:8px;border-radius:4px;background:{A}}}
.pill{{display:inline-block;margin-top:56px;padding:22px 36px;border-radius:999px;background:{G};color:#0E0B24;font-weight:700;font-size:38px;align-self:flex-start}}
.chips{{margin-top:44px;display:flex;flex-wrap:wrap;gap:18px}}
.chip{{padding:16px 28px;border:2px solid {t['line']};border-radius:999px;font-size:36px;font-weight:500}}
.big{{font-family:'Inter Display','Inter';font-weight:800;font-size:330px;line-height:.9;letter-spacing:-.04em;color:{A}}}
.big small{{display:block;font-size:44px;letter-spacing:.12em;font-weight:600;text-transform:uppercase;color:{t['dim']};margin-bottom:24px}}
.bars{{margin-top:56px;display:flex;flex-direction:column;gap:40px}}
.bar{{position:relative}}
.bar b{{display:block;font-size:36px;font-weight:600;color:{t['body']};margin-bottom:14px}}
.bar .track{{height:84px;border-radius:18px;background:{t['card']};overflow:hidden}}
.bar .fill{{height:100%;border-radius:18px;background:{t['dim']};display:flex;align-items:center;justify-content:flex-end;padding-right:26px;font-size:40px;font-weight:700;color:#fff}}
.bar.win .fill{{background:{A};color:#17122E}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:20px}}
.col{{border-radius:32px;padding:44px 40px;min-height:{'980' if reel else '760'}px;display:flex;flex-direction:column}}
.col .k{{margin-bottom:28px;font-size:28px}}
.col h2{{font-size:54px}}
.col p{{font-size:36px;margin-top:28px}}
.col.muted{{background:{t['card']};color:{t['dim']}}}
.col.muted .k,.col.muted h2,.col.muted p{{color:{t['dim']}}}
.col.ozara{{background:#17122E;border:3px solid {A}}}
.col.ozara h2{{color:#F4F1FA}} .col.ozara p{{color:#CFC9DE}}
.range{{margin-top:64px}}
.range .track{{display:grid;grid-template-columns:1fr 1fr 1fr;height:72px;border-radius:36px;overflow:hidden}}
.range .s1{{background:#6FCF97}} .range .s2{{background:{ACCENTS.get(accent, ACCENTS["brand"])}}} .range .s3{{background:#FF7A6B}}
.range .labels{{display:grid;grid-template-columns:1fr 1fr 1fr;margin-top:26px;font-size:32px;font-weight:600;color:{t['body']}}}
.range .labels span:nth-child(2){{color:{A};white-space:nowrap}}
.rows{{margin-top:56px;display:flex;flex-direction:column;gap:26px}}
.row{{display:flex;align-items:baseline;gap:28px;font-size:44px}}
.row b{{font-family:'Inter Display','Inter';font-size:64px;min-width:300px}}
</style></head><body><div class="bar0"></div><div class="wrap">{slide['html']}</div>
<div class="logo">{LOGO}</div>{counter}</body></html>"""

async def main(spec_path, out, reel=False):
    from PIL import Image
    spec = json.load(open(spec_path))
    slides, accent = spec["slides"], spec.get("accent", "brand")
    os.makedirs(out, exist_ok=True)
    H = 1920 if reel else 1350
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': H})
        for i, s in enumerate(slides, 1):
            await pg.set_content(page(s, i, len(slides), accent, reel))
            await pg.wait_for_timeout(300)
            png = os.path.join(out, f'tmp_{i}.png')
            await pg.screenshot(path=png)
            name = f'beat_{i}.jpg' if reel else f'slide_{i}.jpg'
            Image.open(png).convert('RGB').save(os.path.join(out, name), quality=92 if reel else 82, optimize=True, progressive=not reel)
            os.remove(png)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2], "--reel" in sys.argv))
