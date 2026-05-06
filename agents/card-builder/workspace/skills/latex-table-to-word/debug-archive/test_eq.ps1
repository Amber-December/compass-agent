$ErrorActionPreference='Stop'
$out='J:\Desktop\word_eq_test.docx'
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try {
  $doc=$word.Documents.Add()
  $sel=$word.Selection
  $sel.TypeText('before ')
  $r=$sel.Range
  $r.Text='V = \sum Q_i \times P_i'
  $doc.OMaths.Add($r) | Out-Null
  $doc.OMaths.Item(1).BuildUp()
  $sel.SetRange($r.End,$r.End)
  $sel.TypeText(' after')
  $doc.SaveAs([ref]$out)
  Write-Host 'OK' $out
}
finally {
  if($doc){ $doc.Close() | Out-Null }
  if($word){ $word.Quit() | Out-Null }
}
