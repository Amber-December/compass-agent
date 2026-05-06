$ErrorActionPreference='Stop'
$csvPath = 'J:\Desktop\table-1775988874328.csv'
$outPath = 'J:\Desktop\table-1775988874328_wps公式对象版.docx'

function Convert-LatexToWordLinear {
    param([string]$s)
    if ($null -eq $s) { return '' }
    $t = $s.Trim()
    if ($t.StartsWith('$') -and $t.EndsWith('$') -and $t.Length -ge 2) {
        $t = $t.Substring(1, $t.Length - 2)
    }
    $t = $t -replace '\\times', '×'
    $t = $t -replace '\\cdot', '·'
    $t = $t -replace '\\sum_', '∑_'
    $t = $t -replace '\\sum', '∑'
    $t = $t -replace '\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', '($1)/($2)'
    $t = $t -replace '\\beta', 'β'
    $t = $t -replace '\\rho', 'ρ'
    $t = $t -replace '\\alpha', 'α'
    $t = $t -replace '\\gamma', 'γ'
    $t = $t -replace '\\delta', 'δ'
    $t = $t -replace '\\lambda', 'λ'
    $t = $t -replace '\\mu', 'μ'
    $t = $t -replace '\\sigma', 'σ'
    $t = $t -replace '\\pi', 'π'
    $t = $t -replace '\\_', '_'
    $t = $t -replace '\\', ''
    $t = $t -replace '\{', '('
    $t = $t -replace '\}', ')'
    $t = $t -replace '\s+', ' '
    return $t.Trim()
}

function Strip-LatexMarkers {
    param([string]$s)
    if ($null -eq $s) { return '' }
    $t = $s -replace '\$(.*?)\$', '$1'
    return $t
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
        $rng = $table.Cell(1, $c).Range
        $rng.End = $rng.End - 1
        $rng.Text = [string]$headers[$c-1]
    }

    for ($r = 0; $r -lt $data.Count; $r++) {
        $props = @($data[$r].PSObject.Properties)
        for ($c = 0; $c -lt $cols; $c++) {
            $cell = $table.Cell($r + 2, $c + 1)
            $rng = $cell.Range
            $rng.End = $rng.End - 1
            $raw = [string]$props[$c].Value

            if ($c -eq 1) {
                # 公式列：只放公式对象，避免和正文混排
                $linear = Convert-LatexToWordLinear $raw
                $rng.Text = $linear
                $doc.OMaths.Add($rng) | Out-Null
                $doc.OMaths.Item($doc.OMaths.Count).BuildUp()
            } else {
                $rng.Text = Strip-LatexMarkers $raw
            }
        }
    }

    $doc.SaveAs([ref]$outPath)
    Write-Host "SUCCESS: $outPath"
}
finally {
    if ($doc -ne $null) { try { $doc.Close() | Out-Null } catch {} }
    if ($word -ne $null) { try { $word.Quit() | Out-Null } catch {} }
}
