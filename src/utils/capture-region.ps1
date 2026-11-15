# Capture a screen region at native resolution as a lossless PNG (no downscaling, no JPEG).
# Usage: powershell -File capture-region.ps1 -X 380 -Y 170 -W 2004 -H 965 -Out C:\path\shot.png
# X, Y, W, H are physical pixels of the primary screen (2560x1440 here).
param(
    [Parameter(Mandatory = $true)][int]$X,
    [Parameter(Mandatory = $true)][int]$Y,
    [Parameter(Mandatory = $true)][int]$W,
    [Parameter(Mandatory = $true)][int]$H,
    [Parameter(Mandatory = $true)][string]$Out
)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($X, $Y, 0, 0, $bmp.Size)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"saved $Out ($W x $H)"
