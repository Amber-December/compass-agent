$ErrorActionPreference='Stop'
$tests = @(
  'Q_i',
  'Q_(i)',
  'Q_pre',
  'Q_(pre)',
  'TV = \\sum_{i=1}^{n} (TC_i + OC_i) \\times V_i + CS',
  'S_a = \\frac{S^2}{2z} \\times Q_{max} \\times e^{-(\\frac{z}{S})^2}'
)
$word = New-Object -ComObject KWPS.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $word.Documents.Add()
try {
  foreach($t in $tests){
    $p = $doc.Paragraphs.Add()
    $r = $p.Range
    $r.Text = $t
    $doc.OMaths.Add($r) | Out-Null
    $doc.OMaths.Item($doc.OMaths.Count).BuildUp()
  }
  $out='J:\Desktop\\latex_probe.docx'
  $doc.SaveAs([ref]$out)
  Write-Host $out
} finally {
  try { $doc.Close() | Out-Null } catch {}
  try { $word.Quit() | Out-Null } catch {}
}
