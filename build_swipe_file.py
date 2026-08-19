#!/usr/bin/env python3
"""Render the 1,000 Winning Ads swipe file HTML from brand JSON data."""
import json, sys, html

data_path = sys.argv[1] if len(sys.argv) > 1 else "pilot-data.json"
out_path = sys.argv[2] if len(sys.argv) > 2 else "swipe-file.html"
title_suffix = sys.argv[3] if len(sys.argv) > 3 else ""

data = json.load(open(data_path))
brands = data["brands"]
total_ads = sum(len(b["ads"]) for b in brands)

def esc(s):
    return html.escape(str(s or ""))

def slug(name):
    return "b-" + "".join(c if c.isalnum() else "-" for c in name.lower())

cards = []
menu_items = []
for b in brands:
    sid = slug(b["name"])
    menu_items.append(
        f'<a class="menu-item" href="#{sid}">{esc(b["name"])} <span>{len(b["ads"])}</span></a>')
    ad_cards = []
    for ad in b["ads"]:
        if ad["type"] == "video":
            media = (f'<video controls preload="metadata" playsinline '
                     f'src="{esc(ad["media"])}#t=0.1"></video>')
        else:
            media = f'<img loading="lazy" src="{esc(ad["media"])}" alt="{esc(ad["title"])}">'
        ad_cards.append(f'''
      <div class="ad">
        <div class="media">{media}<span class="rank">#{ad["rank"]}</span></div>
        <div class="ad-body">
          <h4>{esc(ad["title"])}</h4>
          <p class="hook"><strong>Hook:</strong> {esc(ad["hook"])}</p>
          <p class="angle"><strong>Angle:</strong> {esc(ad["angle"])}</p>
          <p class="copy">{esc(ad["copy"])}</p>
          <p class="meta">Running {ad["days"]} days · launched {esc(ad["launch"])} · {esc(ad["trend"])}</p>
        </div>
      </div>''')
    cards.append(f'''
  <section class="brand-section" id="{sid}">
    <div class="brand-head">
      <img class="logo" loading="lazy" src="{esc(b.get("logo",""))}" alt="">
      <div><h2>{esc(b["name"])}</h2><p>{esc(b.get("category",""))} · top {len(b["ads"])} ads by impressions</p></div>
    </div>
    <div class="ad-grid">{"".join(ad_cards)}
    </div>
  </section>''')

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>1,000 Winning Ads — Swipe File{esc(title_suffix)}</title>
<style>
  :root {{ --navy:#1F3864; --blue:#2E5496; --gold:#F0B429; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:Arial, Helvetica, sans-serif; background:#f2f3f7; color:#222; padding-bottom:80px; }}
  header {{ background:var(--navy); color:#fff; text-align:center; padding:40px 24px 30px; }}
  header h1 {{ font-size:30px; }}
  header p {{ margin-top:10px; font-size:14px; opacity:.85; max-width:660px; margin-left:auto; margin-right:auto; line-height:1.5; }}
  .menu {{ position:sticky; top:0; z-index:20; background:#fff; border-bottom:2px solid var(--navy);
    box-shadow:0 2px 10px rgba(0,0,0,.07); padding:10px 16px; display:flex; gap:8px; overflow-x:auto; }}
  .menu-item {{ flex:0 0 auto; text-decoration:none; color:var(--navy); font-size:13px; font-weight:bold;
    background:#eef1f8; border:1px solid #dfe4f0; border-radius:16px; padding:6px 12px; }}
  .menu-item span {{ background:var(--gold); color:var(--navy); border-radius:10px; padding:1px 7px; font-size:11px; margin-left:4px; }}
  .menu-item:hover {{ background:var(--blue); color:#fff; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:0 20px; }}
  .brand-section {{ margin-top:44px; scroll-margin-top:64px; }}
  .brand-head {{ display:flex; align-items:center; gap:14px; border-bottom:3px solid var(--navy); padding-bottom:12px; margin-bottom:18px; }}
  .brand-head .logo {{ width:52px; height:52px; border-radius:10px; object-fit:cover; background:#ddd; }}
  .brand-head h2 {{ font-size:22px; color:var(--navy); }}
  .brand-head p {{ font-size:13px; color:#777; margin-top:2px; }}
  .ad-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(300px,1fr)); gap:18px; }}
  .ad {{ background:#fff; border:1px solid #e2e5ef; border-radius:12px; overflow:hidden; display:flex; flex-direction:column; }}
  .media {{ position:relative; background:#0d0f14; }}
  .media video, .media img {{ width:100%; height:300px; object-fit:contain; display:block; }}
  .rank {{ position:absolute; top:10px; left:10px; background:var(--gold); color:var(--navy);
    font-weight:bold; font-size:13px; padding:4px 10px; border-radius:14px; }}
  .ad-body {{ padding:14px 16px 16px; display:flex; flex-direction:column; gap:8px; }}
  .ad-body h4 {{ font-size:15px; color:var(--navy); line-height:1.35; }}
  .ad-body p {{ font-size:12.5px; line-height:1.5; }}
  .hook {{ color:#333; }}
  .angle {{ color:#555; }}
  .copy {{ color:#666; font-style:italic; }}
  .meta {{ color:#999; font-size:11.5px !important; margin-top:auto; padding-top:6px; border-top:1px solid #eef0f6; }}
  footer {{ text-align:center; margin-top:60px; font-size:12px; color:#999; }}
</style>
</head>
<body>
<header>
  <h1>1,000 Winning Ads</h1>
  <p>The top {total_ads} ads by impressions across {len(brands)} of the biggest DTC brands —
     ranked from public Meta Ad Library impressions data. Built with Parker (heyparker.ai).</p>
</header>
<nav class="menu">{"".join(menu_items)}</nav>
<div class="wrap">{"".join(cards)}
</div>
<footer>Impressions ranks from the public Meta Ad Library via Parker · no ad-account data used</footer>
</body>
</html>'''

open(out_path, "w").write(page)
print(f"built {out_path}: {len(brands)} brands, {total_ads} ads")
