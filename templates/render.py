"""Render Ozara carousel slides (1080x1350 JPEG) from a JSON spec.
Usage: python3 render.py spec.json out_dir
spec.json = {"slides": ["<html body for slide 1>", ...]}
Classes: .k kicker, h1 headline, .g gradient text, p body, .pill CTA, .chips/.chip tags.
"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
logo=open(os.path.join(HERE,'logo.svg')).read()
G="linear-gradient(100deg,#B966F8,#DD8929)"
def page(body,n,total):
    return f"""<html><head><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:radial-gradient(120% 80% at 85% 0%,#2a1650 0%,#0E0B24 55%,#090717 100%);color:#F4F1FA;font-family:'Inter';position:relative;overflow:hidden}}
.wrap{{position:absolute;left:96px;right:96px;top:150px;bottom:190px;display:flex;flex-direction:column;justify-content:center}}
.k{{font-size:34px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#C9B8F2;margin-bottom:44px}}
h1{{font-family:'Inter Display','Inter';font-weight:700;font-size:104px;line-height:1.04;letter-spacing:-.025em}}
.g{{background:{G};-webkit-background-clip:text;color:transparent}}
p{{font-size:46px;line-height:1.35;color:#CFC9DE;margin-top:52px}}
.logo{{position:absolute;left:96px;bottom:90px;width:200px}}
.n{{position:absolute;right:96px;bottom:92px;font-size:30px;color:#8C84A6;font-weight:500}}
.bar{{position:absolute;left:96px;top:96px;width:120px;height:8px;border-radius:4px;background:{G}}}
.pill{{display:inline-block;margin-top:56px;padding:22px 36px;border-radius:999px;background:{G};color:#0E0B24;font-weight:700;font-size:38px}}
.chips{{margin-top:48px;display:flex;flex-wrap:wrap;gap:18px}}
.chip{{padding:16px 28px;border:2px solid #4A3D73;border-radius:999px;font-size:36px;color:#E6E0F5;font-weight:500}}
</style></head><body><div class="bar"></div><div class="wrap">{body}</div>
<div class="logo">{logo}</div><div class="n">{n} / {total}</div></body></html>"""
async def main(spec,out):
    from PIL import Image
    slides=json.load(open(spec))["slides"]; os.makedirs(out,exist_ok=True)
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1350})
        for i,s in enumerate(slides,1):
            await pg.set_content(page(s,i,len(slides))); await pg.wait_for_timeout(300)
            png=os.path.join(out,f'slide_{i}.png'); await pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(os.path.join(out,f'slide_{i}.jpg'),quality=82,optimize=True,progressive=True); os.remove(png)
        await b.close()
asyncio.run(main(sys.argv[1],sys.argv[2]))
