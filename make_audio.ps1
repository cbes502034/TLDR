Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$outDir = "C:\Users\User\Desktop\agent\tldr\2026-08-19_星期三"
$tmpDir = Join-Path $outDir "_wav_parts"
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

$narrationPath = Join-Path $outDir "_narration.txt"
$lines = Get-Content -Path $narrationPath -Encoding UTF8

$zhVoice = "Microsoft Hanhan Desktop"
$enVoice = "Microsoft Zira Desktop"

$idx = 0
foreach ($line in $lines) {
    $line = $line.Trim()
    if ($line.Length -eq 0) { continue }

    if ($line.StartsWith("[EN]")) {
        $text = $line.Substring(4).Trim()
        $synth.SelectVoice($enVoice)
    }
    elseif ($line.StartsWith("[ZH]")) {
        $text = $line.Substring(4).Trim()
        $synth.SelectVoice($zhVoice)
    }
    elseif ($line.StartsWith("--")) {
        $text = $line.Trim('-', ' ')
        $synth.SelectVoice($zhVoice)
    }
    else {
        $text = $line
        $synth.SelectVoice($zhVoice)
    }

    $idx++
    $wavPath = Join-Path $tmpDir ("{0:D4}.wav" -f $idx)
    $synth.SetOutputToWaveFile($wavPath)
    $synth.Speak($text)
    $synth.SetOutputToNull()
}

Write-Output "Generated $idx wav parts in $tmpDir"
