import re
import pathlib

# Matches: ](/path) where path starts with / and does not already end in / # or ?
pattern = re.compile(r'(\]\()(/[^)#?\s]*[^/)#?\s])(\))')

def add_slash(m):
    return m.group(1) + m.group(2) + '/' + m.group(3)

content_dir = pathlib.Path('src/content')
total_files = 0
total_replacements = 0

for md_file in sorted(content_dir.rglob('*.md')):
    original = md_file.read_text(encoding='utf-8')
    fixed, count = pattern.subn(add_slash, original)
    if count > 0:
        md_file.write_text(fixed, encoding='utf-8')
        print(f'  [{count:2d}] {md_file}')
        total_files += 1
        total_replacements += count

print(f'\nDone: {total_replacements} replacements across {total_files} files.')
