# TÜBİTAK Türkçe ses sahteciliği projesi - Windows tek giriş betiği.
#
# PowerShell:
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\setup-windows.ps1
#
# İsteğe bağlı parametreler mevcut ayrıntılı betiğe aktarılır:
#   .\setup-windows.ps1 -Mode Setup
#   .\setup-windows.ps1 -Mode All -MlaadLimit 20
[CmdletBinding()]
param(
    [ValidateSet('All','Setup','Datasets','MLAAD','Check')]
    [string]$Mode = 'All',
    [ValidateRange(1,10000)]
    [int]$MlaadLimit = 20,
    [switch]$MlaadFull,
    [switch]$IncludeASR,
    [switch]$SkipCommonVoice,
    [switch]$SkipFleurs,
    [switch]$SkipGirenit,
    [switch]$SkipAnilosan,
    [switch]$SkipMlaad,
    [switch]$SkipSystemTools
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '.')).Path
$installer = Join-Path $PSScriptRoot 'scripts\TUBITAK_2209A_Windows_Tek_Script-2.ps1'
if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) {
    throw "Kurulum betiği bulunamadı: $installer"
}

$arguments = @{
    Mode = $Mode
    Root = $root
    MlaadLimit = $MlaadLimit
}
foreach ($name in @(
    'MlaadFull', 'IncludeASR', 'SkipCommonVoice', 'SkipFleurs',
    'SkipGirenit', 'SkipAnilosan', 'SkipMlaad', 'SkipSystemTools'
)) {
    if ((Get-Variable -Name $name -ValueOnly)) {
        $arguments[$name] = $true
    }
}

& $installer @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Windows kurulum betiği başarısız oldu (kod=$LASTEXITCODE)."
}
