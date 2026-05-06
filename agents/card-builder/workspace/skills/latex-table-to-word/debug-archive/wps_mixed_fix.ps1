$ErrorActionPreference='Stop'
$outPath = 'J:\Desktop\table-1775988874328_wps混排修正版.docx'

$rows = @(
    [ordered]@{id='S-1'; f=@('V = ∑ Q_i × P_i'); p='产量Q_i、市场价格P_i'},
    [ordered]@{id='S-2'; f=@('V = ∑ Q_k × P_k'); p='原料产量Q_k、市场价格P_k'},
    [ordered]@{id='S-3'; f=@('V_wr = ∑ (P_i - ET_i - R_i) × A_i × P_w'); p='降水P_i、蒸散发ET_i、径流R_i、水价P_w'},
    [ordered]@{id='S-4'; f=@('V = Q_bio × P_energy'); p='生物量Q_bio、能源价格P_energy'},
    [ordered]@{id='M-1'; f=@('C_total = ∑ (A_i × C_(i,above) + A_i × C_(i,below) + A_i × C_(i,soil))'); p='植被碳密度C_above、C_below、土壤碳密度C_soil'},
    [ordered]@{id='M-2'; f=@('V_(O_2) = 1.63 × NPP × A × P_(O_2)'); p='净初级生产力NPP、面积A、氧气价格P_(O_2)'},
    [ordered]@{id='M-3'; f=@('Q = ((P - 0.2S)^2)/(P + 0.8S)','S = 25400/CN - 254'); p='降雨量P、曲线数CN、潜在最大滞蓄量S'},
    [ordered]@{id='M-4'; f=@('V_control = (Q_pre - Q_post) × A × P_storage'); p='改造前后径流量Q_pre、Q_post、替代成本P_storage'},
    [ordered]@{id='M-5'; f=@('Y_x = (1 - AET_x/P_x) × P_x'); p='实际蒸散发AET_x、降水量P_x'},
    [ordered]@{id='M-6'; f=@('V_land = A × H × ρ × P_land'); p='面积A、淤积厚度H、土壤容重ρ、造地成本P_land'},
    [ordered]@{id='M-7'; f=@('H_x = H_0 × e^(-k x)','V = L_m × (P_c + P_mp)'); p='初始波高H_0、衰减系数k、植被宽度x、岸线长度L_m、工程单价P_c、维护成本P_mp'},
    [ordered]@{id='M-8'; f=@('A = R × K × L × S × C × P'); p='降雨侵蚀力R、土壤可蚀性K、坡长L、坡度S、覆盖C、措施P'},
    [ordered]@{id='M-9'; f=@('S_r = S_p - S_a','S_a = (S^2/(2z)) × Q_max × e^(-(z/S)^2)'); p='潜在风蚀S_p、实际风蚀S_a、最大输沙量Q_max、关键地块长度S'},
    [ordered]@{id='M-10'; f=@('V = ∑ (Q_i × C_i × R × P_i)'); p='污染物含量Q_i、浓度C_i、去除率R、处理成本P_i'},
    [ordered]@{id='M-11'; f=@('V = A × H × (C_pre - C_post) × P_remediation'); p='修复面积A、土层厚度H、污染前后浓度C_pre、C_post、修复单价P_remediation'},
    [ordered]@{id='M-12'; f=@('V = ∑ (Q_j × A_j × P_j)'); p='污染物吸收量Q_j、面积A_j、治理成本P_j'},
    [ordered]@{id='M-13'; f=@('CCI = ∑ (A × (T_e - T_i))','V = (Q_e × S_v × 10 × P_e)/(β × ρ)'); p='降温面积A、温差(T_e - T_i)、蒸发量Q_e、植被面积S_v、电价P_e、汽化热β、水密度ρ'},
    [ordered]@{id='M-14'; f=@('V = (Q_w × S_w + Q_v × S_v) × 10 × P_h'); p='水面蒸发Q_w、植被蒸发Q_v、水面积S_w、植被面积S_v、加湿成本P_h'},
    [ordered]@{id='C-1'; f=@('TV = ∑_(i=1)^n (TC_i + OC_i) × V_i + CS'); p='旅行成本TC_i、时间成本OC_i、游客量V_i、消费者剩余CS'},
    [ordered]@{id='C-2'; f=@('V = S × P_ed + ∑ (N_k × B_k)'); p='面积S、教育价值P_ed、活动场次N_k、单场效益B_k'},
    [ordered]@{id='C-3'; f=@('V_social = f(E, S, P, C)'); p='环境变量E、社会变量S、物理可达性P、文化价值C；基于偏好映射'},
    [ordered]@{id='C-4'; f=@('V = A × P_view × S_quality','V = WTP × N'); p='景观面积A、景观价格P_view、质量评分S_quality、支付意愿WTP、受访人数N'},
    [ordered]@{id='C-5'; f=@('V = ∑ (WTP_i) + C_maintenance'); p='个体支付意愿WTP_i、维护成本C_maintenance'}
)

function Add-EquationAtRange {
    param($doc, $range, [string]$eq)
    $range.Text = $eq
    $doc.OMaths.Add($range) | Out-Null
    $doc.OMaths.Item($doc.OMaths.Count).BuildUp()
}

function Add-EquationLine {
    param($doc, $cell, [string]$eq)
    $rng = $cell.Range.Duplicate
    $rng.End = $rng.End - 1
    $rng.Collapse(0)
    if ($cell.Range.Text -and $cell.Range.Text.Trim([char]13,[char]7).Length -gt 0) {
        $rng.InsertParagraphAfter() | Out-Null
        $rng.SetRange($cell.Range.End - 1, $cell.Range.End - 1)
    }
    Add-EquationAtRange -doc $doc -range $rng -eq $eq
}

function Add-MixedParamContent {
    param($doc, $cell, [string]$text)
    $body = $cell.Range
    $body.End = $body.End - 1
    $body.Text = ''

    $parts = [regex]::Split($text, '([A-Za-zβρ]+(?:_\(?[A-Za-z0-9,]+\)?)?)')
    $cursor = $cell.Range.Duplicate
    $cursor.End = $cursor.End - 1
    $cursor.Collapse(0)

    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($part)) { continue }
        $rng = $cell.Range.Duplicate
        $rng.SetRange($cursor.End, $cursor.End)

        if ($part -match '^[A-Za-zβρ]+(?:_\(?[A-Za-z0-9,]+\)?)?$') {
            Add-EquationAtRange -doc $doc -range $rng -eq $part
            $cursor.SetRange($rng.End, $rng.End)
        } else {
            $rng.Text = $part
            $cursor.SetRange($rng.End, $rng.End)
        }
    }
}

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject KWPS.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Add()

    $table = $doc.Tables.Add($doc.Range(0,0), $rows.Count + 1, 3)
    $table.Borders.Enable = 1
    $table.AllowAutoFit = $true
    $table.Range.Font.Name = 'Times New Roman'
    $table.Range.Font.Size = 10.5
    $table.Rows.Item(1).Range.Bold = 1

    $headers = @('指标序号','关键公式','关键参数')
    for ($c = 1; $c -le 3; $c++) {
        $hr = $table.Cell(1,$c).Range
        $hr.End = $hr.End - 1
        $hr.Text = $headers[$c-1]
    }

    for ($i = 0; $i -lt $rows.Count; $i++) {
        $row = $rows[$i]
        $r = $i + 2

        $c1 = $table.Cell($r,1).Range; $c1.End = $c1.End - 1; $c1.Text = $row.id
        $c2 = $table.Cell($r,2).Range; $c2.End = $c2.End - 1; $c2.Text = ''

        foreach ($eq in $row.f) {
            Add-EquationLine -doc $doc -cell $table.Cell($r,2) -eq $eq
        }

        Add-MixedParamContent -doc $doc -cell $table.Cell($r,3) -text $row.p
    }

    $doc.SaveAs([ref]$outPath)
    Write-Host "SUCCESS: $outPath"
}
finally {
    if ($doc -ne $null) { try { $doc.Close() | Out-Null } catch {} }
    if ($word -ne $null) { try { $word.Quit() | Out-Null } catch {} }
}
