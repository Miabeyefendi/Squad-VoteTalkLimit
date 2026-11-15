# Capture one window at native resolution with PrintWindow, so other windows on top of it
# (chat, notifications) do not end up in the picture. Optionally crop a region given in screen pixels.
# Usage: powershell -File capture-window.ps1 -Pid 1234 -Out C:\path\shot.png [-X 380 -Y 167 -W 2004 -H 967]
param(
    [Parameter(Mandatory = $true)][int]$ProcId,
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$X = -1, [int]$Y = -1, [int]$W = 0, [int]$H = 0
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class PWin {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    public struct RECT { public int L, T, R, B; }
    // biggest visible top level window of a process (the main window, not a tooltip or popup)
    public static IntPtr Biggest(uint want) {
        IntPtr best = IntPtr.Zero; long area = 0;
        EnumWindows(delegate (IntPtr h, IntPtr l) {
            uint pid; GetWindowThreadProcessId(h, out pid);
            if (pid == want && IsWindowVisible(h)) {
                RECT r; GetWindowRect(h, out r);
                long a = (long)(r.R - r.L) * (r.B - r.T);
                if (a > area) { area = a; best = h; }
            }
            return true;
        }, IntPtr.Zero);
        return best;
    }
}
"@
$hwnd = [PWin]::Biggest([uint32]$ProcId)
$r = New-Object PWin+RECT
[void][PWin]::GetWindowRect($hwnd, [ref]$r)
$winW = $r.R - $r.L; $winH = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $winW, $winH
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[void][PWin]::PrintWindow($hwnd, $hdc, 2)
$g.ReleaseHdc($hdc); $g.Dispose()
if ($W -gt 0) {
    $rect = New-Object System.Drawing.Rectangle ($X - $r.L), ($Y - $r.T), $W, $H
    $crop = $bmp.Clone($rect, $bmp.PixelFormat)
    $crop.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
    $crop.Dispose()
} else {
    $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
}
$bmp.Dispose()
"window $($r.L),$($r.T) ${winW}x${winH} saved $Out"
