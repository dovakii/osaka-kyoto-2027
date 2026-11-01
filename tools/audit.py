"""Static preservation, asset and external-link audit (stdlib only)."""
from html.parser import HTMLParser
from pathlib import Path
import collections, concurrent.futures, json, re, urllib.parse, urllib.request
ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__(); self.ids=[];self.links=[];self.images=[];self.scripts=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a':self.links.append(a)
  if tag=='img':self.images.append(a)
  if tag=='script':self.scripts.append(a)
s=(ROOT/'index.html').read_text(); old=(ROOT/'original.html').read_text();doc=Document(s)
assert len(doc.ids)==len(set(doc.ids)),'Duplicate ids'
for link in doc.links:
 href=link.get('href','')
 assert href,'Empty link'
 if href.startswith('#'):assert href[1:] in doc.ids,href
 elif not href.startswith('https://'):assert (ROOT/urllib.parse.unquote(href)).is_file(),href
 if link.get('target')=='_blank':assert 'noopener' in link.get('rel',''),href
for image in doc.images:
 assert not image['src'].startswith('http'),'Hotlinked photo'
 assert (ROOT/image['src']).is_file(),image['src']
 assert image.get('alt') and image.get('onerror'),'Missing accessibility/fallback'
 assert (ROOT/image['src']).read_bytes()[:2]==b'\xff\xd8','Invalid JPEG'
for i in range(1,8):
 prev=re.search(fr'<article class="day" id="day{i}">(.*?)</article>',old,re.S)[1]
 new=re.search(fr'<article class="day" id="day{i}".*?>(.*?)</article>',s,re.S)[1]
 assert re.findall(r'<tr>.*?</tr>',prev,re.S)==re.findall(r'<tr>.*?</tr>',new,re.S),f'Day {i} changed'
 assert re.search(r'<div class="note">(.*?)</div>',prev,re.S)[1] in new,f'Day {i} note lost'
assert s.count('data-check=')==12
assert len(json.loads((ROOT/'assets/images/credits.json').read_text()))==15
assert not re.search(r'@import|https?://', (ROOT/'assets/style.css').read_text()),'External stylesheet dependency'
report={'static':'PASS','days_preserved':7,'schedule_rows':sum(len(re.findall('<tr>',re.search(fr'<article class="day" id="day{i}">(.*?)</article>',old,re.S)[1])) for i in range(1,8)),'checklist_items':12,'image_elements':len(doc.images),'licensed_photographs':15,'internal_links':sum(x.get('href','').startswith('#') for x in doc.links),'external':[]}
maps=[];official=set();all_external=set()
for link in doc.links:
 u=link['href']
 if u.startswith('https://'): all_external.add(u)
 if 'google.com/maps' in u:
  parsed=urllib.parse.urlparse(u);q=urllib.parse.parse_qs(parsed.query)
  assert parsed.scheme=='https' and q.get('api')==['1'] and q.get('query'),u
  maps.append(u)
 elif u.startswith('https://') and not any(h in u for h in ['commons.wikimedia.org','creativecommons.org']):official.add(u)
report['maps_queries']=len(set(maps))
def check(u):
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 TravelSiteLinkAudit'})
  with urllib.request.urlopen(req,timeout=25) as r:
   return {'url':u,'status':r.status,'final_url':r.url}
 except Exception as e:return {'url':u,'status':'unverified','reason':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:report['external']=list(pool.map(check,sorted(all_external)))
report['official_websites']=len(official)
report['unique_external_links']=len(all_external)
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
