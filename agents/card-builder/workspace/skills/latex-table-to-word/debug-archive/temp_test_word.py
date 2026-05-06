import win32com.client as win32
from pathlib import Path
out = Path(r'J:\Desktop\latex_test.docx')
word = win32.gencache.EnsureDispatch('Word.Application')
word.Visible = False
doc = word.Documents.Add()
r = doc.Range(0,0)
r.Text = r'V = \\sum Q_i \\times P_i'
try:
    om = doc.OMaths.Add(r)
    om.BuildUp()
    doc.SaveAs(str(out))
    print('saved', out)
finally:
    doc.Close(False)
    word.Quit()
