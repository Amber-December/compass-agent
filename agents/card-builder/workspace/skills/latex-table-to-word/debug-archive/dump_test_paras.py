from docx import Document
from pathlib import Path
p = Path(r'J:\Desktop\TEST.docx')
doc = Document(str(p))
for i, para in enumerate(doc.paragraphs[:120], 1):
    txt = ''.join(r.text for r in para.runs)
    if txt.strip() or i <= 40:
        print(f'{i:03d}: {txt!r}')
