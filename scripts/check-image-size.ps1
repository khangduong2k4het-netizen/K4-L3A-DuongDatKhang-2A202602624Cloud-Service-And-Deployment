param([string]$Image = "day12-agent:prod")
$ErrorActionPreference = "Stop"
$sizeText = docker image inspect $Image --format '{{.Size}}'
if ($LASTEXITCODE -ne 0) { throw "Cannot inspect image $Image. Build it first." }
$sizeBytes = [long]$sizeText
Write-Output ("{0}: {1:N2} MB ({2} bytes)" -f $Image, ($sizeBytes / 1000000), $sizeBytes)
if ($sizeBytes -ge 500000000) { throw "Image must be strictly below 500 MB." }
# Docker's containerd store reports compressed content in inspect.Size,
# while image ls reports disk usage including unpacked layers. Check both.
$diskUsage = docker image ls $Image --format '{{.Size}}'
if ($LASTEXITCODE -ne 0) { throw "Cannot read image disk usage." }
if ($diskUsage -notmatch '^([0-9.]+)(B|kB|MB|GB|TB)$') {
    throw "Unknown Docker size format: $diskUsage"
}
$multipliers = @{ B = 1; kB = 1000; MB = 1000000; GB = 1000000000; TB = 1000000000000 }
$diskBytes = [double]::Parse($Matches[1], [cultureinfo]::InvariantCulture) * $multipliers[$Matches[2]]
Write-Output "Docker disk usage: $diskUsage"
if ($diskBytes -ge 500000000) { throw "Image disk usage must be strictly below 500 MB." }
