from zipfile import ZipFile
from pathlib import Path
p = Path(r'J:\Desktop\TEST.docx')
print('exists', p.exists(), p)
if p.exists():
    with ZipFile(str(p), 'r') as z:
        names = z.namelist()
        print('has document.xml', 'word/document.xml' in names)
        data = z.read('word/document.xml')
        print(data[:1000].decode('utf-8', errors='ignore'))
