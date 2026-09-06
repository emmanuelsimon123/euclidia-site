from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json,re
root=Path('.').resolve()
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.refs=[];self.images=[];self.h1=0;self.scripts=[];self.script=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='img':self.images.append(a)
  for key in ('href','src'):
   if key in a:self.refs.append((tag,a[key]))
  if tag=='script' and a.get('type')=='application/ld+json':self.script=''
 def handle_data(self,text):
  if self.script is not None:self.script+=text
 def handle_endtag(self,tag):
  if tag=='script' and self.script is not None:self.scripts.append(self.script);self.script=None
files=list(root.glob('*.html'))+list((root/'lessons').glob('*.html'))+list((root/'blog').glob('*.html'))
docs={p:Document(p.read_text(encoding='utf-8')) for p in files}
errors=[];refs=0
for p,d in docs.items():
 if d.h1!=1:errors.append(f'{p.name}: {d.h1} H1 headings')
 if len(set(d.ids))!=len(d.ids):errors.append(f'{p.name}: duplicate IDs')
 for img in d.images:
  if not img.get('alt'):errors.append(f'{p.name}: image missing alt text {img.get("src")}')
 for script in d.scripts:
  try:json.loads(script)
  except Exception as e:errors.append(f'{p.name}: invalid schema {e}')
 for tag,url in d.refs:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  dest=(root/u.path.lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)).resolve() if u.path else p
  if dest.is_dir():dest=dest/'index.html'
  refs+=1
  if not dest.exists():errors.append(f'{p.relative_to(root)}: missing {url}')
  elif u.fragment and dest in docs and u.fragment not in docs[dest].ids:errors.append(f'{p.name}: missing anchor {url}')
print(f'Checked {len(docs)} HTML pages, {refs} local references, image alt text, unique IDs, H1 headings, JSON-LD.')
for e in errors:print(e)
raise SystemExit(bool(errors))
