from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'2027大阪京都・精品旅遊網站.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.suffix=='.zip' or '__pycache__' in p.parts or p.name=='.DS_Store':continue
        z.write(p,Path('akitabi-kansai-2027')/p.relative_to(ROOT))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert 'akitabi-kansai-2027/index.html' in z.namelist()
print(target)
print('ZIP validated:',target.stat().st_size,'bytes')
