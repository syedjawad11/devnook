import os
import re
import sqlite3

drafts_dir = r"agents/content-team/drafts"
db_path = r"agents/content-team/registry.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()

files = [f for f in os.listdir(drafts_dir) if f.endswith(".md")]
cleaned = 0

for fname in files:
    path = os.path.join(drafts_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    m = re.search(r"```(?:markdown|md)?\s*\n(---.*?)\n```\s*$", content, re.DOTALL | re.IGNORECASE)
    if m:
        new_content = m.group(1).strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        slug = fname[:-3]
        c.execute("UPDATE posts SET status='drafted' WHERE slug=?", (slug,))
        cleaned += 1

conn.commit()
conn.close()
print(f"Cleaned {cleaned}/{len(files)} files")
