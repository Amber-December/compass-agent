$ErrorActionPreference = 'Stop'
$csvPath = 'J:\Desktop\table-1775988874328.csv'
$outPath = 'J:\Desktop\table-1775988874328.docx'

function Add-MixedContentToCell {
    param($cell, [string]$text)
    if ($null -eq $text) { return }

    $work = $text -replace "`r?`n", ' '
    $parts = [regex]::Split($work, '(\$.*?\$)')
    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($part)) { continue }
        $insertPos = $cell.Range.End - 1
        $range = $cell.Range.Duplicate
        $range.SetRange($insertPos, $insertPos)

        if ($part.StartsWith('$') -and $part.EndsWith('$')) {
            $latex = $part.Substring(1, $part.Length - 2)
            $range.Text = $latex
            $cell.Range.OMaths.Add($range) | Out-Null
            $cell.Range.OMaths.Item($cell.Range.OMaths.Count).BuildUp()
        } else {
            $range.Text = $part
        }
    }
}

$data = Import-Csv -Path $csvPath -Encoding UTF8
if (-not $data -or $data.Count -eq 0) { throw 'CSV is empty.' }

$headers = @($data[0].PSObject.Properties.Name)
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Add()

    $rows = $data.Count + 1
    $cols = $headers.Count
    $table = $doc.Tables.Add($doc.Range(0,0), $rows, $cols)
    $table.Borders.Enable = 1
    $table.Range.Font.Name = 'Times New Roman'
    $table.Range.Font.Size = 10.5
    $table.Rows.Item(1).Range.Bold = 1
    $table.AllowAutoFit = $true

    for ($c = 1; $c -le $cols; $c++) {
        $table.Cell(1, $c).Range.Text = [string]$headers[$c-1]
    }

    for ($r = 0; $r -lt $data.Count; $r++) {
        $props = @($data[$r].PSObject.Properties)
        for ($c = 0; $c -lt $cols; $c++) {
            $cell = $table.Cell($r + 2, $c + 1)
            $cell.Range.Text = ''
            Add-MixedContentToCell -cell $cell -text ([string]$props[$c].Value)
        }
    }

    $table.Columns.AutoFit()
    $doc.SaveAs([ref]$outPath)
    Write-Host "SUCCESS: $outPath"
}
finally {
    if ($doc -ne $null) { $doc.Close() | Out-Null }
    if ($word -ne $null) { $word.Quit() | Out-Null }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
