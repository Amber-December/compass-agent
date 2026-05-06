from zipfile import ZipFile
from pathlib import Path
import re
p = Path(r'J:\Desktop\TEST.docx')
with ZipFile(str(p), 'r') as z:
    xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
print('dollar count', xml.count('$'))
for m in re.finditer(r'.{0,80}\$.{0,120}\$.{0,80}', xml):
    print('---')
    print(m.group(0))
    break
