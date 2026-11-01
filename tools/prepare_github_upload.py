from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
stage = Path('/private/tmp/akitabi-github-upload')
stage.mkdir(exist_ok=True)
count = 0
for path in sorted(root.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(root)
    if any(p in {'.git', '__pycache__'} for p in relative.parts):
        continue
    if path.suffix in {'.zip', '.pyc'} or path.name.startswith('.env') or path.name in {'.DS_Store', 'fallback-check.html'}:
        continue
    target = stage / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    count += 1
print(stage)
print(f'{count} website files ready; ZIP and temporary test files excluded')
batches = Path('/private/tmp/akitabi-github-batches')
for label, source in [('root',stage),('assets',stage/'assets'),('images',stage/'assets/images'),('tools',stage/'tools')]:
    target_dir=batches/label
    target_dir.mkdir(parents=True,exist_ok=True)
    for path in source.iterdir():
        if path.is_file(): shutil.copy2(path,target_dir/path.name)
print(batches)
