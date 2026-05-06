Write-Host "=== BUKTI 2: MODULARITAS ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "-- Jumlah baris kode per file --"
$training = (Get-Content "prediction\training_linear.py").Count
$logika   = (Get-Content "prediction\logika_ml.py").Count
$models   = (Get-Content "prediction\models.py").Count
$views    = (Get-Content "prediction\views.py").Count
$admin    = (Get-Content "prediction\admin.py").Count

Write-Host "  training_linear.py : $training baris"
Write-Host "  logika_ml.py       : $logika baris"
Write-Host "  models.py          : $models baris"
Write-Host "  views.py           : $views baris"
Write-Host "  admin.py           : $admin baris"
$total = $training + $logika + $models + $views + $admin
Write-Host "  TOTAL              : $total baris"

Write-Host ""
Write-Host "-- Brand yang dilayani 1 class LinearModelTrainer --"
$pkls = Get-ChildItem "ml_models\*.pkl"
foreach ($p in $pkls) {
    Write-Host "  * $($p.BaseName)"
}
Write-Host "  Total: $($pkls.Count) brand, 1 class yang sama"

Write-Host ""
Write-Host "-- Cek hardcode nama brand di views.py & logika_ml.py --"
$hardcode = Select-String -Path "prediction\views.py","prediction\logika_ml.py" -Pattern "toyota|honda|daihatsu|mitsubishi|suzuki|wuling" -CaseSensitive:$false
if ($hardcode) {
    Write-Host "  DITEMUKAN hardcode:"
    $hardcode | ForEach-Object { Write-Host "  File: $($_.Filename) Baris: $($_.LineNumber) -> $($_.Line.Trim())" }
} else {
    Write-Host "  TIDAK ADA hardcode nama brand di views.py & logika_ml.py"
    Write-Host "  -> Sistem bersifat brand-agnostic (OOP abstraksi berhasil)"
}

Write-Host ""
Write-Host "-- Coupling: jumlah file yang import logika_ml --"
$coupling = Select-String -Path "prediction\*.py" -Pattern "logika_ml"
$coupling | ForEach-Object { Write-Host "  $($_.Filename) baris $($_.LineNumber): $($_.Line.Trim())" }
Write-Host "  Total file yang bergantung pada logika_ml: $($coupling.Count) baris import"
