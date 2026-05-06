$ErrorActionPreference='Stop'
$word = New-Object -ComObject KWPS.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $word.Documents.Add()
try {
  $r = $doc.Range(0,0)
  $r.Text = 'x'
  $doc.OMaths.Add($r) | Out-Null
  $om = $doc.OMaths.Item(1)
  $om | Get-Member | Sort-Object Name | Select-Object Name, MemberType | Out-String -Width 200 | Set-Content '.\\omath_members.txt'
  Write-Host 'saved members'
} finally {
  try { $doc.Close($false) | Out-Null } catch {}
  try { $word.Quit() | Out-Null } catch {}
}
