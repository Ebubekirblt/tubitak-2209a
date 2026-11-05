#requires -Version 5.1
<#
TUBITAK 2209-A | Windows 10/11 x64 | Python 3.14 | AASIST + Turkish datasets

PowerShell (normal user session):
  powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\Downloads\TUBITAK_2209A_Windows_Tek_Script.ps1"

Default location: Windows Desktop\Tubitak folder; it is created when missing
(including OneDrive-redirected Desktop).
Default: setup + Common Voice TR, FLEURS TR, girenit, Anilosan15, and
20 MLAAD files per Turkish TTS model. Large optional sources are explicit:
  -MlaadFull       All Turkish MLAAD files (potentially large / slow)
  -IncludeASR      TurkicASR Google Drive archive (optional, not a deepfake detector)

Other examples:
  -Mode Setup
  -Mode Datasets -SkipMlaad
  -Mode MLAAD -MlaadFull
  -Mode Check
  -Mode All -MlaadLimit 30

Rerunnable: existing datasets/files/venv are not removed. Does not install
CUDA Toolkit; CUDA-capable PyTorch wheels bundle necessary CUDA runtime pieces.

Dataset use, permissions and redistribution must be reviewed separately.
#>
[CmdletBinding()]
param(
    [ValidateSet('All','Setup','Datasets','MLAAD','Check')]
    [string]$Mode = 'All',
    [string]$Root = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Tubitak'),
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
$ProgressPreference = 'Continue'
$Root = [System.IO.Path]::GetFullPath($Root)
$Venv = Join-Path $Root '.venv-aasist-py314'
if (-not (Test-Path $Venv) -and (Test-Path (Join-Path $Root '.venv\Scripts\python.exe'))) {
    $Venv = Join-Path $Root '.venv'
}
$Py = Join-Path $Venv 'Scripts\python.exe'
$HF = Join-Path $Venv 'Scripts\hf.exe'
$DataDir = Join-Path $Root 'dataset'
$SourceDir = Join-Path $Root 'aasist-source'
$WeightDir = Join-Path $SourceDir 'models\weights'
$ToolDir = Join-Path $Root 'tools'
$LogDir = Join-Path $Root 'logs'
$MlaadDest = Join-Path $DataDir 'MLAAD'
$script:DatasetErrors = New-Object System.Collections.Generic.List[string]

if (([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture).ToString() -ne 'X64') {
    throw 'Bu kurulum Windows x64 icindir; Windows ARM64/UTM icin CUDA paketleri uygun degildir.'
}

function Info([string]$Message)  { Write-Host "[BILGI] $Message" -ForegroundColor Cyan }
function Good([string]$Message)  { Write-Host "[TAMAM] $Message" -ForegroundColor Green }
function Warn([string]$Message)  { Write-Host "[UYARI] $Message" -ForegroundColor Yellow }
function Invoke-Checked([string]$File, [string[]]$Arguments) {
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Komut basarisiz (kod=$LASTEXITCODE): $File $($Arguments -join ' ')"
    }
}
function Refresh-Path {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
    $wingetLinks = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links'
    if (Test-Path $wingetLinks) { $env:Path += ";$wingetLinks" }
    $gitCmd = 'C:\Program Files\Git\cmd'
    if (Test-Path $gitCmd) { $env:Path += ";$gitCmd" }
}
function Find-CommandPath([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return [string]$cmd.Source }
    return $null
}
function Install-WinGetPackage([string]$Id) {
    $winget = Find-CommandPath 'winget.exe'
    if (-not $winget) {
        throw "winget bulunamadi. App Installer kurun veya $Id paketini elle kurun: https://learn.microsoft.com/windows/package-manager/winget/"
    }
    Info "winget ile kuruluyor: $Id"
    Invoke-Checked $winget @('install','--id',$Id,'--exact','--accept-package-agreements','--accept-source-agreements')
    Refresh-Path
}
function Find-Python314 {
    $candidates = @()
    $pyLauncher = Find-CommandPath 'py.exe'
    if ($pyLauncher) { $candidates += ,@($pyLauncher, '-3.14') }
    $paths = @(
        (Join-Path $Venv 'Scripts\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314\python.exe'),
        'C:\Program Files\Python314\python.exe',
        'C:\Python314\python.exe'
    )
    $foundPy = Find-CommandPath 'python.exe'
    if ($foundPy) { $paths += $foundPy }
    foreach ($candidate in $paths) {
        if (Test-Path $candidate) { $candidates += ,@($candidate) }
    }
    foreach ($c in $candidates) {
        $exe = [string]$c[0]
        $prefix = @()
        if ($c.Count -gt 1) { $prefix = @([string]$c[1]) }
        try {
            $version = & $exe @prefix -c 'import sys; print(str(sys.version_info.major)+chr(46)+str(sys.version_info.minor))' 2>$null
            if ($LASTEXITCODE -eq 0 -and "$version".Trim() -eq '3.14') { return ,$c }
        } catch { }
    }
    return $null
}
function Ensure-Python {
    $base = Find-Python314
    if (-not $base) {
        if ($SkipSystemTools) { throw 'Python 3.14 bulunamadi. -SkipSystemTools kaldirin veya Python 3.14 kurun.' }
        Install-WinGetPackage 'Python.Python.3.14'
        $base = Find-Python314
    }
    if (-not $base) {
        throw 'Python 3.14 bulundu olarak dogrulanamadi. Yeni PowerShell acip betigi tekrar calistirin.'
    }
    if (-not (Test-Path $Py)) {
        if (Test-Path $Venv) {
            throw "Sanal ortam klasoru var ama python.exe yok: $Venv (otomatik silinmedi)."
        }
        Info 'Python 3.14 sanal ortami olusturuluyor...'
        $exe = [string]$base[0]
        $argv = @()
        if ($base.Count -gt 1) { $argv += [string]$base[1] }
        $argv += @('-m','venv',$Venv)
        Invoke-Checked $exe $argv
    }
    Invoke-Checked $Py @('-c','import sys; assert sys.version_info[:2] == (3,14), sys.version; print(sys.version)')
}
function Ensure-Tools {
    if (-not (Find-CommandPath 'git.exe')) {
        if ($SkipSystemTools) { throw 'Git eksik; -SkipSystemTools olmadan tekrar calistirin.' }
        Install-WinGetPackage 'Git.Git'
    }
    if (-not (Find-CommandPath 'ffmpeg.exe')) {
        if ($SkipSystemTools) { Warn 'FFmpeg bulunamadi; telefon kodek testleri icin gerekir.' }
        else { Install-WinGetPackage 'Gyan.FFmpeg' }
    }
    if (-not (Find-CommandPath 'git.exe')) { throw 'Git hala bulunamadi. PowerShell yeniden acip tekrar deneyin.' }
    if (-not (Find-CommandPath 'ffmpeg.exe')) {
        Warn 'FFmpeg PATH uzerinde gorunmuyor. PowerShell yeniden acilirsa duzelebilir.'
    }
}
function Nvidia-Present {
    $nvidia = Find-CommandPath 'nvidia-smi.exe'
    if (-not $nvidia) {
        $system = Join-Path $env:WINDIR 'System32\nvidia-smi.exe'
        if (Test-Path $system) { $nvidia = $system }
    }
    if (-not $nvidia) { return $false }
    try {
        & $nvidia --query-gpu=name --format=csv,noheader
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}
function Ensure-PyDeps {
    Info 'Pip ve Python paketleri kurulum/kontrol asamasi...'
    Invoke-Checked $Py @('-m','pip','install','--upgrade','pip','setuptools','wheel')
    $hasNvidia = Nvidia-Present
    if ($hasNvidia) {
        Info 'NVIDIA algilandi: CUDA 13.0 destekli PyTorch + torchaudio kurulacak.'
        # Windows x64 + CPython 3.14 wheels verified on official PyTorch index.
        Invoke-Checked $Py @('-m','pip','install','--upgrade','torch','torchaudio','--index-url','https://download.pytorch.org/whl/cu130')
    } else {
        Warn 'NVIDIA GPU surucusu algilanmadi: CPU PyTorch kurulacak. CUDA icin surucu yukleyip tekrar kurulum yapin.'
        Invoke-Checked $Py @('-m','pip','install','--upgrade','torch','torchaudio','--index-url','https://download.pytorch.org/whl/cpu')
    }
    Info 'Ses isleme, yapay zeka ve veri kutuphaneleri kuruluyor.'
    Invoke-Checked $Py @('-m','pip','install',
        'numpy','scipy','soundfile','librosa','soxr',
        'scikit-learn','pandas','pyarrow','datasets','huggingface_hub',
        'matplotlib','tqdm','pyyaml','tensorboard',
        'transformers','accelerate','evaluate','gdown')
    Info 'Eski AASIST egitim aracisi torchcontrib istege bagli kuruluyor.'
    & $Py -m pip install torchcontrib
    if ($LASTEXITCODE -ne 0) { Warn 'torchcontrib kurulmasi basarisiz; temel AASIST inference etkilenmez.' }
}
function Ensure-AASIST {
    if (Test-Path (Join-Path $SourceDir 'main.py')) {
        Info 'Mevcut AASIST kaynak kodu korunuyor.'
    } elseif (Test-Path (Join-Path $SourceDir '.git')) {
        Info 'Mevcut AASIST kaynak kodu korunuyor (otomatik git pull yapilmayacak).'
    } elseif (Test-Path $SourceDir) {
        throw "Bu klasor mevcut ama Git deposu degil: $SourceDir"
    } else {
        $git = Find-CommandPath 'git.exe'
        Info 'Resmi AASIST kaynak kodu indiriliyor.'
        Invoke-Checked $git @('clone','--depth','1','https://github.com/clovaai/aasist.git',$SourceDir)
    }
    New-Item -ItemType Directory -Force -Path $WeightDir | Out-Null
    if (-not (Test-Path (Join-Path $WeightDir 'AASIST.pth'))) {
        Info 'AASIST.pth onceden egitilmis agirlik indiriliyor.'
        Invoke-Checked $HF @('download','SpeechAntiSpoofingBenchmarks/AASIST','AASIST.pth','--local-dir',$WeightDir)
    }
    $aasistL = Join-Path $WeightDir 'AASIST-L.pth'
    if (-not (Test-Path $aasistL)) {
        Info 'AASIST-L.pth onceden egitilmis agirlik indiriliyor.'
        Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/clovaai/aasist/main/models/weights/AASIST-L.pth' -OutFile $aasistL
    }
}
function Ensure-HfLogin {
    if (-not (Test-Path $HF)) { throw 'Hugging Face CLI bulunamadi. Once -Mode Setup calistirin.' }
    & $HF auth whoami 2>$null
    if ($LASTEXITCODE -eq 0) {
        Info 'Hugging Face oturumu bulundu; token veri indirmelerinde kullanilacak.'
    } else {
        Warn 'Hugging Face oturumu yok; public veri setleri token olmadan deneniyor.'
        Warn 'Erisim hatasi olursa once: hf auth login'
    }
}
function Download-Dataset([string]$Repo, [string]$Folder, [string]$Include = '') {
    $target = Join-Path $DataDir $Folder
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    $args = @('download',$Repo,'--repo-type','dataset','--local-dir',$target,'--max-workers','3')
    if ($Include) { $args += @('--include',$Include) }
    Info "Veri seti indiriliyor: $Repo -> $target"
    Invoke-Checked $HF $args
}
function Try-Dataset([string]$Repo, [string]$Folder, [string]$Include = '') {
    try {
        Download-Dataset $Repo $Folder $Include
        Good "Veri seti indirildi/kontrol edildi: $Repo"
    } catch {
        $script:DatasetErrors.Add("$Repo : $($_.Exception.Message)")
        Warn "Veri seti hatasi, digerlerine devam ediliyor: $Repo -> $($_.Exception.Message)"
    }
}
function Write-MlaadHelper {
    # Written from this same PS1 file: no second user-downloaded script needed.
    $code = @'
import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('HF_HUB_DOWNLOAD_TIMEOUT', '120')
os.environ.setdefault('HF_HUB_ETAG_TIMEOUT', '30')
from huggingface_hub import HfApi, RepoFile, RepoFolder, hf_hub_download

REPO = 'mueller91/MLAAD'
TR_ROOT = 'fake/tr'

def say(s):
    print(s, flush=True)

def main():
    p = argparse.ArgumentParser(description='Download Turkish MLAAD folders without listing the full repo')
    p.add_argument('--dest', type=Path, required=True)
    p.add_argument('--limit', type=int, default=20)
    p.add_argument('--full', action='store_true')
    args = p.parse_args()
    api = HfApi()
    say('MLAAD TR TTS klasorleri sorgulaniyor...')
    folders = sorted((e for e in api.list_repo_tree(
        repo_id=REPO, repo_type='dataset', path_in_repo=TR_ROOT,
        recursive=False, expand=False, token=os.environ.get('HF_TOKEN') or None)
        if isinstance(e, RepoFolder)), key=lambda e: e.path)
    say(f'Bulunan TTS klasoru: {len(folders)}')
    if not folders:
        raise RuntimeError('Turkce TTS klasoru bulunamadi.')
    failed = []
    for folder in folders:
        say(f'\n{folder.path} listeleniyor...')
        try:
            files = sorted((e for e in api.list_repo_tree(
                repo_id=REPO, repo_type='dataset', path_in_repo=folder.path,
                recursive=True, expand=False, token=os.environ.get('HF_TOKEN') or None)
                if isinstance(e, RepoFile)),
                key=lambda e: (not e.path.endswith('meta.csv'), e.path))
        except Exception as exc:
            say(f'LISTE HATASI: {type(exc).__name__}: {exc}')
            failed.append(folder.path)
            continue
        if not files:
            say('Bos klasor, geciliyor.')
            continue
        bytes_total = sum(e.size or 0 for e in files)
        subset = files if args.full else files[:args.limit]
        say(f'{len(files)} dosya / toplam {bytes_total/(1024**3):.2f} GiB; '
            f'bu turda {len(subset)} dosya')
        for i, entry in enumerate(subset, 1):
            for attempt in range(3):
                try:
                    hf_hub_download(repo_id=REPO, repo_type='dataset',
                                    filename=entry.path, local_dir=str(args.dest),
                                    token=os.environ.get('HF_TOKEN') or None)
                    break
                except KeyboardInterrupt:
                    say('Durduruldu. Ayni komutla devam edilebilir.')
                    return 130
                except Exception as exc:
                    if attempt == 2:
                        say(f'INDIRME HATASI: {entry.path} {type(exc).__name__}: {exc}')
                        failed.append(entry.path)
                    else:
                        time.sleep(2*(attempt+1))
            if i == 1 or i % 20 == 0 or i == len(subset):
                say(f'{folder.path}: {i}/{len(subset)} kontrol edildi')
    say(f'\nMLAAD indirme adimi bitti. Hata sayisi: {len(failed)}')
    if failed:
        say('Ilk 10 hata: ' + '; '.join(failed[:10]))
    return 2 if failed else 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        say(f'KRITIK HATA: {type(e).__name__}: {e}')
        sys.exit(1)
'@
    New-Item -ItemType Directory -Force -Path $ToolDir | Out-Null
    $dest = Join-Path $ToolDir 'mlaad_tr_download.py'
    [System.IO.File]::WriteAllText($dest,$code,[System.Text.UTF8Encoding]::new($false))
    return $dest
}
function Download-Mlaad {
    if ($SkipMlaad) { Info 'MLAAD atlandi (-SkipMlaad).'; return }
    if ($MlaadFull) {
        Warn 'MLAAD TAM TURKCE INDIRME secildi: binlerce dosya ve buyuk disk kullanimi olabilir.'
    } else {
        Info "MLAAD ilk pilot indirmesi: 7 model klasorunun her birinden en fazla $MlaadLimit dosya."
    }
    $helper = Write-MlaadHelper
    New-Item -ItemType Directory -Force -Path $MlaadDest | Out-Null
    $args = @($helper,'--dest',$MlaadDest,'--limit',[string]$MlaadLimit)
    if ($MlaadFull) { $args += '--full' }
    Invoke-Checked $Py $args
}
function Download-ASR {
    $outDir = Join-Path $DataDir 'turkic_languages_model'
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $file = Join-Path $outDir 'turkic_languages_model.zip'
    if ((Test-Path $file) -and (Get-Item $file).Length -gt 1000000) {
        Info 'TurkicASR ZIP zaten mevcut; yeniden indirilmiyor.'
        return
    }
    Info 'Opsiyonel TurkicASR modeli Google Drive indirmesi...'
    & $Py -m gdown '1GtK-OrH3ZRYz2Zc8vf-xndp7R9dic4rV' '--continue' '--output' $file
    if ($LASTEXITCODE -ne 0) { Warn 'ASR Google Drive indirmesi basarisiz; ana proje kurulumu devam eder.' }
}
function Write-CheckScript {
    $code = @'
from pathlib import Path
import importlib
import json
import os
import sys

root = Path(sys.argv[1])
print('=== PYTHON / MODULLER ===', flush=True)
print('Python:', sys.version.split()[0])
for name in ('numpy','scipy','torch','torchaudio','librosa','soundfile',
             'sklearn','pandas','pyarrow','datasets','huggingface_hub',
             'transformers','accelerate','tensorboard'):
    m = importlib.import_module(name)
    print(name, getattr(m,'__version__','OK'))

import torch
print('CUDA derleme:', torch.version.cuda)
print('CUDA mevcut:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))

sys.path.insert(0, str(root / 'aasist-source'))
from models.AASIST import Model
cfg = json.loads((root / 'aasist-source/config/AASIST.conf').read_text(encoding='utf-8'))
for model_name in ('AASIST', 'AASIST-L'):
    cfg = json.loads((root / 'aasist-source/config' / f'{model_name}.conf').read_text(encoding='utf-8'))
    model = Model(cfg['model_config'])
    weights = root / 'aasist-source/models/weights' / f'{model_name}.pth'
    state = torch.load(weights, map_location='cpu', weights_only=True)
    model.load_state_dict(state, strict=True)
    model.eval()
    with torch.inference_mode():
        _, logits = model(torch.zeros(1,64600,dtype=torch.float32))
    assert logits.shape == (1,2), (model_name, tuple(logits.shape))
    print(f'{model_name} agirlik ve CPU ileri gecis: OK {tuple(logits.shape)}', flush=True)

if torch.cuda.is_available():
    try:
        model = model.cuda()
        with torch.inference_mode():
            _, logits = model(torch.zeros(1,64600,device='cuda'))
        print('AASIST CUDA testi: OK', tuple(logits.shape))
    except Exception as exc:
        print('UYARI: CUDA algilaniyor fakat AASIST CUDA testi basarisiz:', repr(exc))
        raise

print('=== VERI KUMELERI ===')
data = root / 'dataset'
for folder in ('girenit-tts-tr-synthetic','MLAAD','commonvoice_17_tr_fixed',
               'FLEURS_TR','Synthetic_Turkish_TTS_Data',
               'turkic_languages_model'):
    path = data / folder
    if not path.exists():
        print(folder, 'YOK (opsiyonel olabilir)')
        continue
    wavs = sum(1 for _ in path.rglob('*.wav'))
    parquets = list(path.rglob('*.parquet'))
    tarballs = sum(1 for _ in path.rglob('*.tar.gz'))
    print(folder, 'wav:', wavs, 'parquet:', len(parquets), 'tar.gz:', tarballs)
    if folder == 'Synthetic_Turkish_TTS_Data' and parquets:
        import pyarrow.parquet as pq
        rows = sum(pq.ParquetFile(p).metadata.num_rows for p in parquets)
        print('Anilosan kayit:', rows)
print('=== KONTROL TAMAMLANDI ===')
'@
    New-Item -ItemType Directory -Force -Path $ToolDir | Out-Null
    $dest = Join-Path $ToolDir 'kontrol.py'
    [System.IO.File]::WriteAllText($dest,$code,[System.Text.UTF8Encoding]::new($false))
    return $dest
}
function Run-Checks {
    if (-not (Test-Path $Py)) { throw 'Sanal ortam yok. Once -Mode Setup calistirin.' }
    $test = Write-CheckScript
    Invoke-Checked $Py @($test,$Root)
    $ffmpeg = Find-CommandPath 'ffmpeg.exe'
    if ($ffmpeg) {
        & $ffmpeg -version | Select-Object -First 1
    } else { Warn 'FFmpeg PATH uzerinde bulunamadi.' }
}

New-Item -ItemType Directory -Force -Path $Root,$DataDir,$WeightDir,$ToolDir,$LogDir,(Join-Path $Root 'experiments') | Out-Null
$env:HF_HUB_DOWNLOAD_TIMEOUT = '120'
$env:HF_HUB_ETAG_TIMEOUT = '30'
$env:HF_HUB_CACHE = Join-Path $Root '_hf_cache\hub'
$env:HF_XET_CACHE = Join-Path $Root '_hf_cache\xet'
$env:HF_ASSETS_CACHE = Join-Path $Root '_hf_cache\assets'
$transcript = Join-Path $LogDir ("kurulum_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))
$recording = $false
try {
    Start-Transcript -Path $transcript -ErrorAction Stop | Out-Null
    $recording = $true
} catch { Warn "Log kaydi acilamadi: $_" }

try {
    Write-Host ''
    Write-Host '============================================' -ForegroundColor Cyan
    Write-Host ' TUBITAK 2209-A | WINDOWS TEK SCRIPT' -ForegroundColor Cyan
    Write-Host '============================================' -ForegroundColor Cyan
    Info "Mod: $Mode | Konum: $Root"
    if ($Mode -eq 'All' -or $Mode -eq 'Setup') {
        Ensure-Tools
        Ensure-Python
        Ensure-PyDeps
        Ensure-AASIST
    }
    if ($Mode -eq 'All' -or $Mode -eq 'Datasets' -or $Mode -eq 'MLAAD') {
        if (-not (Test-Path $Py)) { throw 'Sanal ortam yok. Once -Mode Setup calistirin.' }
        Ensure-HfLogin
        if ($Mode -ne 'MLAAD') {
            if (-not $SkipCommonVoice) {
                Try-Dataset 'ysdede/commonvoice_17_tr_fixed' 'commonvoice_17_tr_fixed'
            }
            if (-not $SkipFleurs) {
                Try-Dataset 'google/fleurs' 'FLEURS_TR' 'data/tr_tr/**'
            }
            if (-not $SkipGirenit) {
                Try-Dataset 'girenit/girenit-tts-tr-synthetic' 'girenit-tts-tr-synthetic'
            }
            if (-not $SkipAnilosan) {
                Try-Dataset 'Anilosan15/Synthetic_Turkish_TTS_Data' 'Synthetic_Turkish_TTS_Data'
            }
            if ($IncludeASR) { Download-ASR }
        }
        try { Download-Mlaad } catch {
            $script:DatasetErrors.Add("MLAAD : $($_.Exception.Message)")
            Warn "MLAAD indirmesi tamamlanamadi: $($_.Exception.Message)"
        }
    }
    if ($Mode -eq 'All' -or $Mode -eq 'Setup' -or $Mode -eq 'Check') {
        Run-Checks
    }
    if ($script:DatasetErrors.Count -gt 0) {
        foreach ($errorEntry in $script:DatasetErrors) { Warn $errorEntry }
        throw "$($script:DatasetErrors.Count) veri setinde hata var; logu kontrol edin, ayni komutla yeniden devam edebilirsiniz."
    }
    Good 'Secilen kurulum / indirme adimlari tamamlandi.'
    Info "Proje: $Root"
    Info "Log: $transcript"
    Info "Sanal ortamdaki Python: $Py"
    Info 'Alania veri seti BILEREK indirilmedi.'
    Info 'TurkicASR istege baglidir; kullanmak icin -IncludeASR secenegini ekleyin.'
    Info 'MLAAD TR tum dosyalar icin -Mode MLAAD -MlaadFull kullanin.'
} catch {
    Write-Host "[HATA] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[HATA] Log: $transcript" -ForegroundColor Red
    exit 1
} finally {
    if ($recording) { Stop-Transcript | Out-Null }
}
