import os, glob

for f in glob.glob('src/content/**/*.md', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'related_content:' not in content:
        content = content.replace('---\n', '---\nrelated_content: []\n', 1)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
