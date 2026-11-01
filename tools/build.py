"""Build a dependency-free, file:// compatible website, preserving the original itinerary."""
from pathlib import Path
import re, json, html, urllib.parse
ROOT=Path(__file__).resolve().parents[1]
original=(ROOT/'original.html').read_text()
credits=json.loads((ROOT/'assets/images/credits.json').read_text())
for r in credits:
 r['license_url']=r['license_url'].replace('http://','https://')
byid={r['id']:r for r in credits}
esc=lambda s:html.escape(str(s),quote=True)
fallback='data:image/svg+xml,'+urllib.parse.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="#ded8cd"/><path d="M0 650L350 300 600 550 850 250 1200 650" fill="none" stroke="#a59a86" stroke-width="2"/><text x="600" y="710" text-anchor="middle" fill="#5f6457" font-size="24" font-family="sans-serif">圖片暫時無法顯示 · 請繼續閱讀行程</text></svg>')
def image(slug,eager=False):
 r=byid[slug]
 sizes='100vw' if eager else '(max-width: 700px) 100vw, 60vw'
 return f'<img src="{r["file"]}" srcset="{r["small"]} 800w, {r["file"]} 1800w" sizes="{sizes}" width="1800" height="1200" alt="{esc(r["label"])}實景照片" loading="{"eager" if eager else "lazy"}" decoding="async" {"fetchpriority=high" if eager else ""} onerror="this.onerror=null;this.removeAttribute(\'srcset\');this.src=\'{fallback}\';this.dataset.fallback=\'true\'"/>'
def attribution(slug):
 r=byid[slug]
 return f'<span class="credit">攝影：{esc(r["photographer"])} · <a href="{esc(r["source"])}" target="_blank" rel="noopener noreferrer">來源</a> · <a href="{esc(r["license_url"])}" target="_blank" rel="noopener noreferrer">{esc(r["license"])}</a></span>'
def heading(kicker,title,desc=''):
 return f'<div class="section-heading"><div><p class="eyebrow">{kicker}</p><h2>{title}</h2></div>{f"<p>{desc}</p>" if desc else ""}</div>'
sections={id:re.search(r'<section class="panel" id="'+id+r'">(.*?)</section>',original,re.S)[1] for id in ['usj','hotel','budget','checklist']}
days=re.findall(r'<article class="day" id="day(\d)">(.*?)</article>',original,re.S)
dayimages=['station','arashiyama','yasaka','shinkansen','whaleshark','usj','dotonbori']
daynames=['初見京都','嵐山秋色','和服寫真','鐵道時光','海洋漫遊','環球冒險','滿載而歸']
weekdays=['六','日','一','二','三','四','五']
dayhtml=[]
for n,content in days:
 slug=dayimages[int(n)-1]
 content=re.sub(r'<figure class="day-photo">.*?</figure>','',content,flags=re.S)
 head,body=content.split('<div class="day-body">',1)
 extras={'2':['sagano','tenryuji','bamboo'],'4':['railway'],'5':['aquarium','tempozan']}.get(n,[])
 extra='<div class="detail-strip">'+''.join(f'<figure>{image(s)}<figcaption>{byid[s]["label"]}</figcaption>{attribution(s)}</figure>' for s in extras)+'</div>' if extras else ''
 content=head+f'<div class="day-layout"><div class="day-visual"><figure>{image(slug)}<figcaption>{byid[slug]["label"]} / DAY 0{n}</figcaption></figure>{attribution(slug)}'+('</div>')+'<div class="day-body">'+body+'</div>'+extra
 dayhtml.append(f'<article class="day" id="day{n}" tabindex="-1" aria-label="第{n}天行程">{content}</article>')
datebar=''.join(f'<a href="#day{i}" class="date-link" data-day="{i}" aria-label="第{i}天 11月{19+i}日 {daynames[i-1]}"><small>DAY 0{i}</small><b>11.{19+i} <span>（{weekdays[i-1]}）</span></b><span>{daynames[i-1]}</span></a>' for i in range(1,8))
gallery=''
for idx,(slug,day,name,sub) in enumerate([('arashiyama',2,'山河之間，遇見秋色','ARASHIYAMA / 嵐山・渡月橋'),('yasaka',3,'穿上和服，走進京都','HIGASHIYAMA / 八坂塔・和服攝影'),('shinkansen',4,'下一站，小小鐵道迷','RAILWAY MUSEUM / 京都鐵道博物館'),('whaleshark',5,'潛入一片深藍','KAIYUKAN / 大阪海遊館'),('usj',6,'今天，把童心放大','UNIVERSAL STUDIOS JAPAN / 日本環球影城')]):
 gallery+=f'<div class="gallery-card"><a class="gallery-image" href="#day{day}">{image(slug)}<span class="photo-index">0{idx+1} /</span><span class="gallery-overlay">查看當日行程 ↗</span></a><p class="eyebrow">{sub}</p><h3><a href="#day{day}">{name} <span>↗</span></a></h3>{attribution(slug)}</div>'
usj=sections['usj']
usj=re.sub(r'<h2>.*?</h2>',heading('03 / FAMILY PLAYBOOK','把冒險，留給每一個人。'),usj,count=1)
usj=usj.replace('⭐ ','').replace('⚠️ ','')
usj=usj.replace('咚奇剛瘋狂礦車：107公分以上，較刺激，視孩子接受度。','咚奇剛瘋狂礦車：107公分以上，未滿122公分須成人陪同；較刺激，視孩子接受度。')
usj=usj.replace('小小兵瘋狂乘車遊：102公分以上，動感較強。','小小兵瘋狂乘車遊：102公分以上，未滿122公分須成人陪同；動感較強。')
usj=usj.replace('飛天史努比、環球奇境：適合安排較輕鬆的下午。','飛天史努比：92公分以上，未滿122公分須成人陪同；環球奇境可安排較輕鬆的下午。')
usj+=f'<div class="usj-bottom"><figure>{image("nintendo")}<figcaption>超級任天堂世界入口・歷史實景，裝飾可能隨活動更換</figcaption>{attribution("nintendo")}</figure><div class="note"><b>入園前再次確認</b><p>以上身高整理依2026/11/01查閱的<a href="https://www.usj.co.jp/web/en/us/service-guide/safe/height-restriction" target="_blank" rel="noopener noreferrer">USJ官方身高規範 ↗</a>；2027年設施、陪同及票券規則仍以當時公告為準。Express Pass 不等於 Studio Pass，須另備入園門票。六人的區域入場時段應一致。</p></div></div>'
hotel=re.sub(r'<h2>.*?</h2>',heading('04 / STAY & MOVE','住得從容，走得輕盈。'),sections['hotel'],count=1)
hotel=hotel.replace('<h3>京都｜11/20–11/23</h3>','<p class="eyebrow">KYOTO / 11.20 — 11.23 / 3 NIGHTS</p><h3>京都站，把旅途安頓好。</h3>')
hotel=hotel.replace('<h3>大阪｜11/23–11/26</h3>','<p class="eyebrow">OSAKA / 11.23 — 11.26 / 3 NIGHTS</p><h3>難波，城市生活的起點。</h3>')
def maplink(label,query):
 return f'<a href="https://www.google.com/maps/search/?api=1&amp;query={urllib.parse.quote(query)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'
hotel+='<div class="hotel-links"><p>京都住宿地圖</p><div class="day-links">'+''.join(maplink(a,b) for a,b in [('都酒店 京都八條','Miyako Hotel Kyoto Hachijo'),('Hotel Granvia Kyoto','Hotel Granvia Kyoto')])+'</div><p>大阪住宿地圖</p><div class="day-links">'+''.join(maplink(a,b) for a,b in [('Hotel Royal Classic Osaka','Hotel Royal Classic Osaka'),('Swissôtel Nankai Osaka','Swissotel Nankai Osaka')])+'</div></div><p class="fine">住宿為原稿候選清單，尚未預訂；三間客房須核對實際成人、兒童入住人數。</p>'
budget=re.sub(r'<h2>.*?</h2>',heading('05 / TRAVEL BUDGET','美好的旅行，心裡有個底。'),sections['budget'],count=1)
budget=budget.replace('onclick="budget(\'low\')"','data-budget="low" aria-pressed="false"').replace('onclick="budget(\'mid\')"','data-budget="mid" aria-pressed="true"').replace('onclick="budget(\'high\')"','data-budget="high" aria-pressed="false"')
budget=budget.replace('USJ門票＋親子Express＋餐飲','USJ門票＋親子Express＋園內餐飲').replace('餐飲7天</td>','餐飲7天（園外）</td>')
budget=budget.replace('<table class="budget"','<div class="budget-layout"><div><table class="budget"')
budget=budget.replace('</table>','</table></div><aside class="budget-total"><p class="eyebrow">YOUR JOURNEY, YOUR BUDGET</p><p>全團 5 大 1 小・合計</p><output id="total" aria-live="polite">NT$ 283,000</output><p id="average">平均每人 NT$ 47,167</p><label for="shopping">額外購物預算（全團／NT$）</label><input type="number" id="shopping" inputmode="numeric" min="0" max="10000000" step="100" value="0"/><p class="fine">原稿建議版 NT$ 283,000。可額外加入購物預算；成人與兒童實際分攤依票價調整。</p></aside></div>')
check=sections['checklist']
check=re.sub(r'<h2>.*?</h2>',heading('06 / BEFORE YOU GO','準備好，才更能隨心出發。'),check,count=1)
check=check.replace('勾選已完成事項；此頁為單一HTML檔，勾選狀態僅在目前頁面使用期間保留。','逐一完成旅行的小事。進度會儲存在目前裝置的瀏覽器。')
check=check.replace('<div id="checks">','<div class="check-progress"><span id="checkCount" aria-live="polite">已完成 0 / 12</span><progress id="checkProgress" max="12" value="0" aria-label="行前清單完成進度"></progress></div><p id="storageNote" class="fine" role="status"></p><div id="checks">')
counter=iter(range(12));check=re.sub('<input aria-label=',lambda _:f'<input data-check="{next(counter)}" aria-label=',check)
check=check.replace('<button onclick="window.print()">','<div class="check-actions"><button id="printButton">').replace('列印／儲存成PDF</button>','列印／儲存成PDF</button><button id="resetChecks" class="button-outline">清除勾選</button><button id="undoReset" class="button-outline" hidden>復原清除</button></div>')
credititems=''.join(f'<li><b>{esc(r["label"])}</b>{attribution(r["id"])}<span class="fine">{esc(r["title"])}<br/>已縮放與壓縮；版面採裁切顯示。衍生圖片沿用原授權。</span></li>' for r in credits)
page='''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/><meta name="theme-color" content="#f5f2ec"/><meta name="description" content="2027大阪京都7天6夜親子賞楓旅行：京都和服攝影、嵐山小火車、鐵道博物館、海遊館、USJ，完整時程、住宿交通與預算。"/><title>秋旅 AKITABI｜2027 大阪・京都 七日紀行</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"/><link rel="stylesheet" href="assets/style.css"/><script src="assets/app.js" defer></script></head><body><a class="skip-link" href="#overview">跳至行程內容</a><div class="masthead"><a class="brand" href="#top"><span class="brand-mark">旅</span><span>秋旅 <small>AKITABI</small></span></a><nav class="top-nav" aria-label="主要導覽"><a href="#gallery">旅行風景</a><a href="#overview">七日紀行</a><a href="#usj">親子攻略</a><a href="#hotel">住宿交通</a><a href="#budget">旅費試算</a></nav><a class="nav-cta" href="#checklist">行前準備 <span>↗</span></a></div><header class="hero" id="top"><div class="hero-image">'''+image('kiyomizu',True)+'''</div><div class="hero-shade"></div><div class="hero-content"><p class="eyebrow">JAPAN / KANSAI / AUTUMN 2027</p><h1>把秋天，<br/>留在京都。</h1><p class="hero-subtitle">大阪・京都 七日紀行</p><p class="hero-description">一場三代同行的秋日旅行。<br/>從古都的楓紅，到孩子眼裡閃閃發光的冒險。</p><a class="button hero-button" href="#overview">展開七日旅程 <span>↓</span></a></div><div class="hero-bottom"><span>2027.11.20 — 11.26</span><span>KYOTO → OSAKA</span></div><div class="vertical-note" aria-hidden="true">家族と、秋を旅する。</div></header><div class="hero-credit">清水寺・秋日實景 / '''+attribution('kiyomizu')+'''</div><main><div class="trip-facts"><div><small>THE JOURNEY</small><strong>7 <span>天</span> 6 <span>夜</span></strong></div><div><small>OUR COMPANY</small><strong>5 <span>大人</span> 1 <span>小孩</span></strong></div><div><small>STAY A LITTLE</small><strong>京都 <span>3 晚</span>＋大阪 <span>3 晚</span></strong></div><div><small>ESTIMATED BUDGET</small><strong><span>NT$</span> 283,000</strong></div></div><section class="container intro"><p class="eyebrow">A SLOWER JOURNEY, A CLOSER FAMILY.</p><h2>風景慢慢看，回憶一起收藏。</h2><p>給長輩留一段從容的步調，給孩子留一場期待的冒險。<br class="desktop-only"/>這個秋天，我們在京都與大阪，把平凡的相聚變成珍藏。</p><span class="seal" aria-hidden="true">秋<br/>日</span></section><section class="container" id="gallery">'''+heading('01 / MOMENTS TO REMEMBER','此行，值得期待的風景。','五種風景，串起一家人的秋日記憶。')+f'<div class="gallery-grid">{gallery}</div>'+'''<p class="fine">照片為不同年份與季節拍攝的真實景點紀錄，僅供風景參考；2027年楓況與活動布置依現場為準。<a href="#credits">查看全部照片授權 ↗</a></p></section><section class="itinerary-section" id="overview"><div class="container">'''+heading('02 / THE SEVEN-DAY JOURNEY','七天六夜，剛剛好的節奏。','11.20–11.22 京都 / 11.23 移動 / 11.24–11.26 大阪')+f'<nav class="date-bar" aria-label="選擇行程日期">{datebar}</nav>'+'''<div class="itinerary-toolbar"><p>選一天，看看今天的旅行。</p><div><button id="previousDay" class="icon-button" aria-label="前一天">←</button><button id="nextDay" class="icon-button" aria-label="後一天">→</button><button id="showAll" class="button-outline" aria-pressed="false">顯示全部 7 天</button></div></div><noscript><p class="note">JavaScript 未啟用：以下仍可閱讀全部行程；預算切換與儲存勾選需啟用 JavaScript。</p></noscript><div id="days">'''+''.join(dayhtml)+'''</div><p class="fine">時程依原稿完整保留，為規劃參考。航班、2027年營業日、票價、班次與體驗名額須於預訂前確認。</p></div></section><section class="container content-section" id="usj">'''+usj+'''</section><section class="stay-section"><div class="container content-section" id="hotel">'''+hotel+'''</div></section><section class="container content-section" id="budget">'''+budget+'''</section><section class="check-section"><div class="container content-section" id="checklist">'''+check+'''</div></section><section class="container credits-section" id="credits"><details><summary>照片來源與開放授權 <span>15 張實景 / CREDITS ＋</span></summary><p class="fine">所有照片均由 Wikimedia Commons 下載至 assets/images；網站無外部圖片或字型請求。攝影著作依各自授權使用；CC BY-SA 圖片及衍生縮圖保留相同授權。公共領域照片亦保留來源。完整紀錄：<a href="assets/images/credits.json">credits.json</a>。</p><ul>'''+credititems+'''</ul></details></section></main><footer class="site-footer"><a class="brand" href="#top"><span class="brand-mark">旅</span><span>秋旅 <small>AKITABI</small></span></a><p>與家人同行的日子，就是最好的風景。</p><div><span>2026.11.01 規劃版本 · 2027 大阪京都親子賞楓</span><a href="#top">回到頁首 ↑</a></div></footer></body></html>'''
(ROOT/'index.html').write_text(page)
(ROOT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#8f3d2c"/><text x="32" y="45" text-anchor="middle" font-size="40" fill="#faf6ed" font-family="serif">旅</text></svg>')
testimage=image('kiyomizu',True).replace('assets/images/kiyomizu.jpg','missing-test-image.jpg').replace('assets/images/kiyomizu-small.jpg','missing-test-small.jpg')
(ROOT/'tools/fallback-check.html').write_text('<!DOCTYPE html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>圖片備援測試</title><body style="background:#f5f2ec;color:#293b31;font-family:serif"><h1>圖片失敗備援驗證</h1><div style="max-width:600px">'+testimage.replace('<img ','<img style="width:100%;height:auto" ')+'</div><p>故意使用不存在的照片，應顯示內嵌 SVG，且不循環重試。</p></body></html>')
(ROOT/'assets/images/CREDITS.md').write_text('# 照片授權紀錄\n\n下載日期：2026-11-01。圖片縮放、JPEG壓縮，CSS裁切；衍生圖片沿用各自原授權。\n\n'+'\n\n'.join(f'## {r["label"]}\n- 檔案：{r["file"]} / {r["small"]}\n- 攝影：{r["photographer"]}\n- 來源：{r["source"]}\n- 原圖：{r["original_url"]}\n- 授權：{r["license"]} — {r["license_url"]}' for r in credits))
print('Built index.html; retained',len(days),'days and',len(re.findall('<tr>',original)),'original table rows')
