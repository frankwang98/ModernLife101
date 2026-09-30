"""Build crawlable article pages, share cards and sitemap from Markdown."""
from pathlib import Path
from html import escape as h
import json, os, re
from urllib.parse import urlparse
import markdown
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'site'
BASE = os.environ.get('SITE_URL','https://frankwang98.asia/ModernLife101').rstrip('/')
if urlparse(BASE).scheme != 'https':
    raise ValueError('SITE_URL must be an absolute HTTPS URL')
items = json.loads((ROOT/'content/index.json').read_text())
worlds = json.loads((ROOT/'content/worlds.json').read_text())
ids = {x['id'] for x in items}
assert len(ids) == len(items), 'duplicate ID'
font_path = os.environ.get('CJK_FONT','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
if not Path(font_path).is_file():
    raise RuntimeError('Install fonts-noto-cjk or set CJK_FONT to a Chinese font file')
(SITE/'articles').mkdir(exist_ok=True)
(SITE/'covers').mkdir(exist_ok=True)
def cover(name,title,subtitle):
    im=Image.new('RGB',(1200,630),'#f5f3eb');d=ImageDraw.Draw(im)
    def font(size):return ImageFont.truetype(font_path,size)
    d.rounded_rectangle((65,55,119,109),radius=14,fill='#234d3e')
    d.polygon([(105,65),(96,94),(75,101),(86,80)],fill='#ecb477')
    d.text((140,57),'ModernLife101',font=font(32),fill='#234d3e')
    d.text((70,155),subtitle,font=font(23),fill='#64716a')
    lines=[];line=''
    for char in title:
        if d.textlength(line+char,font=font(58))>1030 and line:
            lines.append(line);line=char
        else:line+=char
    if line:lines.append(line)
    for i,line in enumerate(lines):d.text((70,240+i*82),line,font=font(58),fill='#233b32')
    d.line((70,525,1130,525),fill='#d9ded2',width=2)
    d.text((70,554),'读懂一点。试做一点。再走远一点。',font=font(24),fill='#64716a')
    d.text((900,554),'modernlife101',font=font(23),fill='#b56e39')
    im.save(SITE/'covers'/f'{name}.png',optimize=True)
def meta(title,description,url,image,kind='article'):
    return f'''<meta name="description" content="{h(description,quote=True)}"><link rel="canonical" href="{h(url)}">
<meta property="og:site_name" content="ModernLife101"><meta property="og:locale" content="zh_CN"><meta property="og:type" content="{kind}"><meta property="og:title" content="{h(title,quote=True)}"><meta property="og:description" content="{h(description,quote=True)}"><meta property="og:url" content="{h(url)}"><meta property="og:image" content="{h(image)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{h(title,quote=True)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{h(title,quote=True)}"><meta name="twitter:description" content="{h(description,quote=True)}"><meta name="twitter:image" content="{h(image)}">'''
for item in items:
    assert re.fullmatch(r'\d{3}',item['id']), 'invalid ID'
    assert item['world'] in {w['id'] for w in worlds}
    assert all(x in ids for x in item['related'])
    text=(ROOT/'content'/f"{item['id']}.md").read_text()
    assert text.startswith(f"# {item['id']} · ")
    assert all(s in text for s in ['## 三件值得知道的事','## 试着做一件事','## 来源与继续阅读','## 继续探索'])
    text=re.sub(r'\]\((\d{3})\.md\)',r'](\1.html)',text)
    item['html']=markdown.markdown(text,extensions=['extra'])
    item['source']=f"https://github.com/frankwang98/ModernLife101/blob/main/content/{item['id']}.md"
    item['url']=f"articles/{item['id']}.html"
    url=f"{BASE}/{item['url']}";image=f"{BASE}/covers/{item['id']}.png"
    world=next(w for w in worlds if w['id']==item['world'])
    cover(item['id'],item['title'],f"{item['id']} / {world['name']} / 约 {item['minutes']} 分钟")
    schema=json.dumps({'@context':'https://schema.org','@type':'Article','headline':item['title'],'description':item['summary'],'image':image,'dateModified':item['verified'],'author':{'@type':'Organization','name':'ModernLife101'},'mainEntityOfPage':url,'inLanguage':'zh-CN'},ensure_ascii=False).replace('<','\\u003c')
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(item['title'])} · ModernLife101</title>{meta(item['title'],item['summary'],url,image)}<link rel="icon" href="../logo.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css"><script type="application/ld+json">{schema}</script><script src="../article.js" defer></script></head><body><a class="skip" href="#article-content">跳到正文</a><header><a class="brand" href="../"><img src="../logo.svg" width="36" height="36" alt="">ModernLife<span>101</span></a><nav aria-label="主导航"><a href="../#learn">读一点</a><a href="../#explore">看世界</a><a href="https://github.com/frankwang98/ModernLife101">GitHub ↗</a></nav></header><main><article id="reader" data-id="{item['id']}"><a class="back" href="../#learn">← 回到问题集</a><p class="eyebrow">{h(world['name'])} / 约 {item['minutes']} min / 更新 {item['verified']}</p><div id="article-content">{item['html']}</div><div class="reader-end"><button id="mark" hidden>标记读过</button><button id="share" hidden>复制文章链接</button><a href="{item['source']}" target="_blank" rel="noopener">纠错 / 查看 Markdown ↗</a><a href="../#random">再随机读一篇 ↗</a></div><p id="share-status" role="status"></p><p class="fine">阅读记录仅存在当前浏览器；具体产品和地区规则请核对原始说明。</p></article></main><footer><a class="brand" href="../">ModernLife101</a><p>读懂一点。试做一点。再走远一点。</p><a href="https://github.com/frankwang98/ModernLife101/blob/main/CONTRIBUTING.md">一起写好它 ↗</a></footer></body></html>'''
    (SITE/item['url']).write_text(page)
(SITE/'data.json').write_text(json.dumps(dict(items=items,worlds=worlds,explore=json.loads((ROOT/'content/explore.json').read_text())),ensure_ascii=False))
cover('home','世界很大。从一个好问题开始。','现代世界生存与探索指南 / 10 个世界 · 30 篇短读')
p=SITE/'index.html';home=p.read_text();home=re.sub(r'<!-- SHARE META -->[\s\S]*?<!-- /SHARE META -->','',home)
home=home.replace('</head>',f'<!-- SHARE META -->{meta("ModernLife101 · 现代世界生存与探索指南","没人系统教过你，但生活在现代世界应该知道的 1001 件事。",BASE+"/",BASE+"/covers/home.png","website")}<!-- /SHARE META --></head>')
# Keep the three entry points readable before JavaScript loads.
featured=[]
for id in ['013','011','022']:
    item=next(x for x in items if x['id']==id)
    featured.append(f'<a class="feature" href="{item["url"]}"><small>{id} / 代表作</small><h3>{h(item["title"])}</h3><p>{h(item["summary"])}</p></a>')
home=re.sub(r'<div id="featured" class="featured">[\s\S]*?</div>', '<div id="featured" class="featured">'+''.join(featured)+'</div>',home)
p.write_text(home)
urls=[(BASE+'/',max(x['verified'] for x in items))]+[(BASE+'/'+x['url'],x['verified']) for x in items]
(SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{h(url)}</loc><lastmod>{date}</lastmod></url>' for url,date in urls)+'</urlset>\n')
(SITE/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
print(f'Built {len(items)} static articles, {len(items)+1} share cards and sitemap')
