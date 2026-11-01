import concurrent.futures, html, json, re, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = {'User-Agent': 'KansaiFamilyJourney/1.0 (educational travel site; license attribution)'}
def request(url):
    for attempt in range(5):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=60).read()
        except Exception:
            if attempt==4: raise
            time.sleep(3+attempt*5)
def api(**query):
    return json.loads(request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action':'query','format':'json',**query})))
def clean(s): return html.unescape(re.sub('<[^>]+>', '', s)).strip()
def search(term):
    data=api(generator='search',gsrsearch=term+' filetype:bitmap',gsrnamespace=6,gsrlimit=5,prop='imageinfo',iiprop='url|extmetadata')
    return sorted(data.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',0))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        for term in sys.argv[1:]:
            print('\nSEARCH',term)
            for p in search(term):
                m=p['imageinfo'][0]['extmetadata']
                print(p['title'], '|', clean(m.get('Artist',{}).get('value','')), '|',m.get('LicenseShortName',{}).get('value',''))
        raise SystemExit
    selections={
      'kiyomizu': ('清水寺・秋色', 'Kiyomizu-dera in Kyoto-r.jpg'),
      'arashiyama': ('嵐山・渡月橋', 'Togetsukyo0270.jpg'),
      'sagano': ('嵯峨野小火車・秋景', 'Autumn foliage 2012 (8252583379).jpg'),
      'yasaka': ('東山・八坂塔', 'Yasakanoto Hokanji-temple Kyoto.jpg'),
      'railway': ('京都鐵道博物館', 'Kyoto Railway Museum from train of Tokaido Main Line.jpg'),
      'aquarium': ('大阪海遊館', 'Kaiyukan.JPG'),
    }
    selections.update(json.loads((ROOT/'tools/extra-images.json').read_text()))
    records=[]
    def download(item):
        slug,(label,title)=item
        p=next(iter(api(titles='File:'+title,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=1600)['query']['pages'].values()))
        i=p['imageinfo'][0]; m=i['extmetadata']; license=clean(m.get('LicenseShortName',{}).get('value',''))
        if not (license.startswith('CC BY') or license in ['Public domain','CC0']): raise ValueError('Unapproved license: '+license)
        local=ROOT/'assets/images'/f'{slug}.jpg'
        # Original URLs avoid thumbnail-service availability; files are resized locally.
        cache=ROOT/'assets/images'/f'{slug}.metadata.json'
        if local.exists() and local.stat().st_size>10000:
            data=local.read_bytes()
        else:
            try: data=request(i['url'].split('?')[0])
            except Exception: data=request(i.get('thumburl',i['url']))
            local.write_bytes(data)
        subprocess.run(['sips','-Z','1800','-s','format','jpeg','-s','formatOptions','82',str(local)],check=True,capture_output=True)
        small=local.with_name(slug+'-small.jpg')
        subprocess.run(['sips','-Z','800',str(local),'--out',str(small)],check=True,capture_output=True)
        record={'id':slug,'label':label,'title':title,'file':str(local.relative_to(ROOT)),'small':str(small.relative_to(ROOT)),'photographer':clean(m.get('Artist',{}).get('value','')),'source':i['descriptionurl'],'original_url':i['url'].split('?')[0],'license':license,'license_url':m.get('LicenseUrl',{}).get('value','https://commons.wikimedia.org/wiki/Commons:Public_domain'),'changes':'JPEG resized/recompressed to 1800px and 800px; CSS cover crop. Image derivatives retain the source license.','retrieved':'2026-11-01','metadata':m}
        cache.write_text(json.dumps(record,ensure_ascii=False,indent=2))
        print(slug,license,len(data),'bytes',flush=True)
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        for r in pool.map(download,selections.items()): records.append(r)
    (ROOT/'assets/images/credits.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print('Saved',len(records),'licensed local photographs')
