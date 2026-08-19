#!/usr/bin/env python3
"""Render the public, self-contained swipe file: sidebar by niche + filters."""
import json, os, base64, hashlib, html, sys
from categories import category_for, CATEGORY_ORDER

# "live"  -> media loaded from Parker URLs, videos PLAY inline (for GitHub Pages hosting)
# "embed" -> media baked in as data URIs, videos show a still (for CSP-restricted hosts)
MODE = sys.argv[1] if len(sys.argv) > 1 else "live"
OUTNAME = sys.argv[2] if len(sys.argv) > 2 else (
    "swipe-file-live.html" if MODE == "live" else "public-swipe-file.html")

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".media-cache")
AD_W, LOGO_W = 264, 56

def cache_path(url, kind):
    return os.path.join(CACHE, hashlib.md5((kind + url).encode()).hexdigest() + ".webp")

def uri(path):
    return "data:image/webp;base64," + base64.b64encode(open(path, "rb").read()).decode()

def esc(s): return html.escape(str(s or ""))
def slug(n): return "b-" + "".join(c if c.isalnum() else "-" for c in n.lower())
def cslug(n): return "c-" + "".join(c if c.isalnum() else "-" for c in n.lower())

data = json.load(open(os.path.join(HERE, "full-data.json")))
brands = data["brands"]

# group by category
grouped = {}
for b in brands:
    grouped.setdefault(category_for(b["name"]), []).append(b)
for v in grouped.values():
    v.sort(key=lambda x: x["name"].lower())

shown_ads = missing_media = 0
sections, side = [], []

for cat in CATEGORY_ORDER:
    if cat not in grouped:
        continue
    cat_brands, cat_count = [], 0
    for b in grouped[cat]:
        cards, nvid, nimg = [], 0, 0
        for ad in b["ads"]:
            is_vid = ad["type"] == "video"
            cp = cache_path(ad["media"], "vid%d" % AD_W if is_vid else "img%d" % AD_W)
            if MODE == "embed" and not os.path.exists(cp):
                missing_media += 1
                continue
            shown_ads += 1
            nvid += is_vid; nimg += (not is_vid)
            badge = '<span class="vid">▶</span>' if is_vid else '<span class="stat">STATIC</span>'
            watch = (f'<a class="watch" href="{esc(ad["media"])}" target="_blank" rel="noopener">Watch ad →</a>'
                     if (is_vid and MODE == "embed") else "")
            bits = []
            if ad.get("hook"):  bits.append(f'<p class="hook"><b>Hook:</b> {esc(ad["hook"])}</p>')
            if ad.get("angle"): bits.append(f'<p class="angle"><b>Angle:</b> {esc(ad["angle"])}</p>')
            if ad.get("copy"):  bits.append(f'<p class="copy">{esc(ad["copy"][:200])}</p>')
            meta = f'Running {esc(ad.get("days","?"))} days'
            if ad.get("launch"): meta += f' · {esc(ad["launch"])}'
            if MODE == "live":
                poster = f' poster="{uri(cp)}"' if os.path.exists(cp) else ""
                media_el = (f'<video controls preload="none" playsinline{poster} src="{esc(ad["media"])}"></video>'
                            if is_vid else
                            f'<img loading="lazy" src="{esc(ad["media"])}" alt="{esc(ad.get("title",""))}">')
            else:
                media_el = f'<img loading="lazy" src="{uri(cp)}" alt="{esc(ad.get("title",""))}">'
            cards.append(f'''<article class="ad" data-type="{'video' if is_vid else 'static'}">
<div class="media">{media_el}
<span class="rank">#{ad["rank"]}</span>{badge}</div>
<div class="body"><h4>{esc(ad.get("title",""))}</h4>{"".join(bits)}
<p class="meta">{meta}</p>{watch}</div></article>''')
        if not cards:
            continue
        cat_count += len(cards)
        lp = cache_path(b["logo"], "img%d" % LOGO_W) if b.get("logo") else None
        logo = (f'<img class="logo" src="{uri(lp)}" alt="">' if lp and os.path.exists(lp)
                else '<div class="logo ph"></div>')
        cat_brands.append(f'''<section class="brand" id="{slug(b['name'])}" data-brand="{esc(b['name'].lower())}"
 data-cat="{esc(cat)}" data-video="{nvid}" data-static="{nimg}">
<header class="bh">{logo}<div><h3>{esc(b["name"])}</h3>
<p>{esc(b.get("category",""))} · top {len(cards)} by impressions</p></div></header>
<div class="grid">{"".join(cards)}</div></section>''')
        side.append(f'<a class="sb" href="#{slug(b["name"])}" data-brand="{esc(b["name"].lower())}">{esc(b["name"])}</a>')
    if cat_brands:
        sections.append(f'<div class="catblock" id="{cslug(cat)}" data-cat="{esc(cat)}">'
                        f'<h2 class="cathead">{esc(cat)} <span>{len(cat_brands)} brands</span></h2>'
                        + "".join(cat_brands) + '</div>')

# sidebar grouped
side_html = []
for cat in CATEGORY_ORDER:
    if cat not in grouped: continue
    items = [b for b in grouped[cat] if any(True for _ in b["ads"])]
    if not items: continue
    links = "".join(
        f'<a class="sb" href="#{slug(b["name"])}" data-brand="{esc(b["name"].lower())}">{esc(b["name"])}</a>'
        for b in items)
    side_html.append(f'''<div class="sgroup" data-cat="{esc(cat)}">
<button class="scat" type="button">{esc(cat)}<span>{len(items)}</span></button>
<div class="slist">{links}</div></div>''')

total_brands = sum(len(v) for v in grouped.values())

page = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>1,000 Winning Ads Swipe File</title>
<link rel="icon" type="image/png" href="parker-logo.png">
<link rel="apple-touch-icon" href="parker-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Radio+Canada+Big:wght@700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f5f4fa;--card:#fff;--line:#e6e3f1;--ink:#1d1a28;--dim:#6f6a85;--navy:#524b9e;
--blue:#5f58b0;--gold:#eebf12;--side:#fff;--shadow:0 1px 3px rgba(40,30,70,.08)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#131120;--card:#1c1a29;
--line:#2e2b41;--ink:#eae8f4;--dim:#9d97b8;--navy:#aaa3e6;--blue:#b0aae2;--side:#171525;--shadow:none}}}}
:root[data-theme="dark"]{{--bg:#131120;--card:#1c1a29;--line:#2e2b41;--ink:#eae8f4;--dim:#9d97b8;
--navy:#aaa3e6;--blue:#b0aae2;--side:#171525;--shadow:none}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink)}}
.hero{{background:#7f78c5;color:#fcf5e2;text-align:center;padding:38px 20px 36px;border-bottom:3px solid #14121f}}
.hero .pk{{width:84px;height:84px;display:block;margin:0 auto 8px;border-radius:50%}}
.hero h1{{font-family:'Radio Canada Big',-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;
font-weight:700;font-size:clamp(26px,5vw,42px);letter-spacing:-.5px;color:#fff}}
.hero p{{margin:13px auto 0;max-width:660px;font-size:14.5px;line-height:1.7;color:rgba(252,245,226,.94)}}
.hero b{{color:inherit}}
.hero a{{color:#fff;font-weight:700;text-decoration:underline;text-decoration-color:#eebf12;
text-decoration-thickness:2px;text-underline-offset:3px}}
.hero a:hover{{color:#eebf12}}
.hero .promo{{background:#eebf12;color:#14121f;font-weight:800;padding:2px 9px;border-radius:7px;
border:1.6px solid #14121f;font-size:.9em;letter-spacing:.04em;white-space:nowrap}}
.shell{{display:flex;align-items:flex-start;max-width:1500px;margin:0 auto}}
aside{{position:sticky;top:0;flex:0 0 236px;height:100vh;overflow-y:auto;background:var(--side);
border-right:1px solid var(--line);padding:14px 10px 40px}}
aside h4{{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--dim);padding:0 8px 8px}}
.scat{{width:100%;display:flex;justify-content:space-between;align-items:center;gap:6px;background:none;
border:0;font:600 13px inherit;color:var(--navy);padding:7px 8px;cursor:pointer;text-align:left;border-radius:6px}}
.scat:hover{{background:var(--bg)}}
.scat span{{background:var(--line);color:var(--dim);border-radius:9px;padding:1px 7px;font-size:11px;font-weight:600}}
.slist{{display:none;padding:0 0 6px 8px}}
.sgroup.open .slist{{display:block}}
.sgroup.open .scat{{color:var(--blue)}}
.sb{{display:block;font-size:12.5px;color:var(--dim);text-decoration:none;padding:4px 8px;border-radius:5px}}
.sb:hover{{color:var(--blue);background:var(--bg)}}
main{{flex:1;min-width:0;padding:0 20px 70px}}
.bar{{position:sticky;top:0;z-index:8;background:var(--bg);padding:13px 0 11px;
display:flex;gap:9px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--line)}}
.bar input{{flex:1;min-width:160px;font:14px inherit;padding:8px 12px;border:1px solid var(--line);
border-radius:8px;background:var(--card);color:var(--ink)}}
.seg{{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--card)}}
.seg button{{font:600 12.5px inherit;padding:8px 13px;border:0;background:none;color:var(--dim);cursor:pointer}}
.seg button.on{{background:#7f78c5;color:#fff}}
.count{{font-size:12.5px;color:var(--dim);margin-left:auto}}
.catblock{{margin-top:34px}}
.cathead{{font-size:13px;letter-spacing:.07em;text-transform:uppercase;color:var(--dim);
padding-bottom:8px;border-bottom:2px solid var(--navy);display:flex;gap:9px;align-items:center}}
.cathead span{{font-size:11px;background:var(--line);border-radius:9px;padding:1px 8px;letter-spacing:0;text-transform:none}}
.brand{{margin-top:26px;scroll-margin-top:66px}}
.bh{{display:flex;align-items:center;gap:11px;margin-bottom:13px}}
.logo{{width:40px;height:40px;border-radius:8px;object-fit:cover;flex:0 0 auto}}
.logo.ph{{background:var(--line)}}
.bh h3{{font-size:17px;color:var(--navy);font-family:'Radio Canada Big',-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
.bh p{{font-size:11.5px;color:var(--dim);margin-top:1px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:13px}}
@media(min-width:1330px){{.grid{{grid-template-columns:repeat(5,minmax(0,1fr))}}}}
body.noside aside{{display:none}}
@media(min-width:1100px){{body.noside .grid{{grid-template-columns:repeat(5,minmax(0,1fr))}}}}
.sideT{{font:600 12.5px inherit;padding:8px 13px;border:1px solid var(--line);border-radius:8px;
background:var(--card);color:var(--dim);cursor:pointer;white-space:nowrap}}
.sideT:hover{{color:var(--navy);border-color:var(--navy)}}
.ad{{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;
display:flex;flex-direction:column;box-shadow:var(--shadow)}}
.media{{position:relative;background:#0c0e13;min-height:190px;display:flex;align-items:center;justify-content:center}}
.media img,.media video{{width:100%;height:246px;object-fit:contain;display:block;background:#0c0e13}}
.rank{{position:absolute;top:7px;left:7px;background:var(--gold);color:#14121f;font-weight:700;
font-size:11.5px;padding:2px 8px;border-radius:11px}}
.vid,.stat{{position:absolute;top:7px;right:7px;background:rgba(0,0,0,.72);color:#fff;
font-size:10px;font-weight:600;padding:2px 7px;border-radius:10px;letter-spacing:.04em}}
.body{{padding:11px 13px 13px;display:flex;flex-direction:column;gap:5px;flex:1}}
.body h4{{font-size:13.5px;line-height:1.3;color:var(--navy)}}
.body p{{font-size:12px;line-height:1.42}}
.hook{{color:var(--ink)}} .angle,.copy{{color:var(--dim)}} .copy{{font-style:italic}}
.meta{{color:var(--dim);font-size:10.5px !important;margin-top:auto;padding-top:6px;border-top:1px solid var(--line)}}
.watch{{font-size:11.5px;font-weight:600;color:var(--blue);text-decoration:none}}
.watch:hover{{text-decoration:underline}}
.empty{{padding:50px 0;text-align:center;color:var(--dim);font-size:14px;display:none}}
a:focus-visible,button:focus-visible,input:focus-visible{{outline:2px solid var(--gold);outline-offset:2px}}
footer{{text-align:center;padding:34px 20px 50px;font-size:11.5px;color:var(--dim)}}
footer a{{color:var(--blue);font-weight:600;text-decoration:none}}
footer a:hover{{text-decoration:underline}}
@media(max-width:900px){{aside{{display:none}} main{{padding:0 14px 60px}} .sideT{{display:none}}}}
</style>
<div class="hero"><img class="pk" src="parker-logo.png" alt="Parker" width="84" height="84">
<h1>1,000 Winning Ads Swipe File</h1>
<p>Built with the Parker MCP in Claude Code. The top 5 ads by impressions from <b>{total_brands}</b> of the biggest DTC brands. <a href="https://heyparker.ai/" target="_blank" rel="noopener">Try Parker free for 30 days</a> with code <span class="promo">PARKERBRAIN</span>.</p></div>
<div class="shell">
<aside><h4>Browse by niche</h4>{"".join(side_html)}</aside>
<main>
<div class="bar">
<button id="sideToggle" class="sideT" type="button" aria-pressed="false">Hide niches</button>
<input id="q" type="search" placeholder="Search brands…" aria-label="Search brands">
<div class="seg" role="group" aria-label="Filter by format">
<button data-f="all" class="on">All</button><button data-f="video">Video</button><button data-f="static">Static</button>
</div>
<span class="count" id="count"></span>
</div>
{"".join(sections)}
<p class="empty" id="empty">No brands match that search.</p>
</main></div>
<footer>Ranked by impressions from the public Meta Ad Library via <a href="https://heyparker.ai/" target="_blank" rel="noopener">Parker</a>. No ad-account data used.<br>
{"Videos play in the page." if MODE=="live" else "Video ads show their opening frame. Tap “Watch ad” to play."}</footer>
<script>
(function(){{
 var q=document.getElementById('q'),cnt=document.getElementById('count'),
     empty=document.getElementById('empty'),fmt='all',
     brands=[].slice.call(document.querySelectorAll('.brand')),
     blocks=[].slice.call(document.querySelectorAll('.catblock'));
 document.querySelectorAll('.scat').forEach(function(b){{
   b.addEventListener('click',function(){{ b.parentNode.classList.toggle('open'); }});
 }});
 document.querySelectorAll('.seg button').forEach(function(b){{
   b.addEventListener('click',function(){{
     document.querySelectorAll('.seg button').forEach(function(x){{x.classList.remove('on')}});
     b.classList.add('on'); fmt=b.dataset.f; apply();
   }});
 }});
 var st=document.getElementById('sideToggle');
 if(st){{
   var off0=false;
   try{{off0=localStorage.getItem('noside')==='1'}}catch(e){{}}
   if(off0){{document.body.classList.add('noside');st.textContent='Show niches';st.setAttribute('aria-pressed','true');}}
   st.addEventListener('click',function(){{
     var off=document.body.classList.toggle('noside');
     st.textContent=off?'Show niches':'Hide niches';
     st.setAttribute('aria-pressed',off?'true':'false');
     try{{localStorage.setItem('noside',off?'1':'0')}}catch(e){{}}
   }});
 }}
 q.addEventListener('input',apply);
 function apply(){{
   var term=q.value.trim().toLowerCase(), vis=0, ads=0;
   brands.forEach(function(sec){{
     var nameOk=!term||sec.dataset.brand.indexOf(term)>-1||sec.dataset.cat.toLowerCase().indexOf(term)>-1;
     var shown=0;
     sec.querySelectorAll('.ad').forEach(function(a){{
       var ok=nameOk&&(fmt==='all'||a.dataset.type===fmt);
       a.style.display=ok?'':'none'; if(ok)shown++;
     }});
     sec.style.display=shown?'':'none'; if(shown){{vis++;ads+=shown;}}
   }});
   blocks.forEach(function(bl){{
     bl.style.display=bl.querySelector('.brand:not([style*="none"])')?'':'none';
   }});
   cnt.textContent=vis+' brands · '+ads+' ads';
   empty.style.display=vis?'none':'block';
 }}
 apply();
}})();
</script>'''

out = os.path.join(HERE, OUTNAME)
open(out, "w").write(page)
print(f"[{MODE}] {OUTNAME}: {total_brands} brands · {shown_ads} ads · missing media {missing_media} · "
      f"{len(page.encode())/1048576:.1f}MB")
