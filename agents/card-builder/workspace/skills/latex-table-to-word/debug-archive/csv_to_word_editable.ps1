$ErrorActionPreference='Stop'
$csvPath = 'J:\Desktop\table-1775988874328.csv'
$outPath = 'J:\Desktop\table-1775988874328_editable.docx'

function Add-MixedContentToCell {
    param($doc, $cell, [string]$text)
    if ($null -eq $text) { return }

    $parts = [regex]::Split(($text -replace "`r?`n", ' '), '(\$.*?\$)')
    $cursor = $cell.Range.Duplicate
    $cursor.End = $cursor.End - 1
    $cursor.Collapse(0)  # wdCollapseEnd

    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($part)) { continue }

        if ($part.StartsWith('$') -and $part.EndsWith('$')) {
            $latex = $part.Substring(1, $part.Length - 2).Trim()
            if ($latex.Length -eq 0) { continue }

            $eqRange = $cell.Range.Duplicate
            $eqRange.SetRange($cursor.End, $cursor.End)
            $eqRange.Text = $latex
            $doc.OMaths.Add($eqRange) | Out-Null
            $doc.OMaths.Item($doc.OMaths.Count).BuildUp()
            $cursor.SetRange($eqRange.End, $eqRange.End)
        }
        else {
            $txtRange = $cell.Range.Duplicate
            $txtRange.SetRange($cursor.End, $cursor.End)
            $txtRange.Text = $part
            $cursor.SetRange($txtRange.End, $txtRange.End)
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
    $table.AllowAutoFit = $true
    $table.Range.Font.Name = 'Times New Roman'
    $table.Range.Font.Size = 10.5
    $table.Rows.Item(1).Range.Bold = 1

    for ($c = 1; $c -le $cols; $c++) {
        $cellRange = $table.Cell(1, $c).Range
        $cellRange.End = $cellRange.End - 1
        $cellRange.Text = [string]$headers[$c-1]
    }

    for ($r = 0; $r -lt $data.Count; $r++) {
        $props = @($data[$r].PSObject.Properties)
        for ($c = 0; $c -lt $cols; $c++) {
            $cell = $table.Cell($r + 2, $c + 1)
            $body = $cell.Range
            $body.End = $body.End - 1
            $body.Text = ''
            Add-MixedContentToCell -doc $doc -cell $cell -text ([string]$props[$c].Value)
        }
    }

    $doc.SaveAs([ref]$outPath)
    Write-Host "SUCCESS: $outPath"
}
finally {
    if ($doc -ne $null) { try { $doc.Close() | Out-Null } catch {} }
    if ($word -ne $null) { try { $word.Quit() | Out-Null } catch {} }
}
