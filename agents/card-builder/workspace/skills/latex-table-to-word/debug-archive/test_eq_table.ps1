$ErrorActionPreference='Stop'
$out='J:\Desktop\word_eq_table_test.docx'
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try {
  $doc=$word.Documents.Add()
  $table=$doc.Tables.Add($doc.Range(0,0),2,2)
  $cell=$table.Cell(2,2)
  $rng=$cell.Range
  $rng.End = $rng.End - 1
  $rng.Text='desc '
  $ins=$cell.Range.Duplicate
  $ins.SetRange($rng.End,$rng.End)
  $ins.Text='V = \sum Q_i \times P_i'
  $doc.OMaths.Add($ins) | Out-Null
  $doc.OMaths.Item($doc.OMaths.Count).BuildUp()
  $tail=$cell.Range.Duplicate
  $tail.SetRange($ins.End,$ins.End)
  $tail.Text=' end'
  $doc.SaveAs([ref]$out)
  Write-Host 'OK' $out
}
finally {
  if($doc){ $doc.Close() | Out-Null }
  if($word){ try{$word.Quit()|Out-Null}catch{} }
}
