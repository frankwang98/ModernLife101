"""Build static content from Markdown. Run from any working directory."""
from pathlib import Path
import json
import re
import markdown
ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT/'content/index.json').read_text())
worlds = json.loads((ROOT/'content/worlds.json').read_text())
ids = {x['id'] for x in items}
assert len(ids) == len(items), 'duplicate ID'
for item in items:
    assert item['world'] in {w['id'] for w in worlds}
    assert all(x in ids for x in item['related'])
    text = (ROOT/'content'/f"{item['id']}.md").read_text()
    assert text.startswith(f"# {item['id']} · ")
    assert all(s in text for s in ['## 三件值得知道的事','## 试着做一件事','## 来源与继续阅读','## 继续探索'])
    text = re.sub(r'\]\((\d{3})\.md\)', r'](#article/\1)', text)
    item['html'] = markdown.markdown(text, extensions=['extra'])
    item['source'] = f"https://github.com/frankwang98/ModernLife101/blob/main/content/{item['id']}.md"
(ROOT/'site/data.json').write_text(json.dumps(dict(items=items,worlds=worlds,explore=json.loads((ROOT/'content/explore.json').read_text())),ensure_ascii=False))
print(f'Built {len(items)} articles in {len(worlds)} worlds')
