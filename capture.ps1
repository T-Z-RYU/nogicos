Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Write-Host "Capturing in 5 seconds..."
for ($i = 5; $i -gt 0; $i--) {
    Write-Host "$i..."
    Start-Sleep -Seconds 1
}

$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
$bmp.Save("C:\Users\WIN\Desktop\cursor-chat.png")
$g.Dispose()
$bmp.Dispose()

Write-Host "Screenshot saved to C:\Users\WIN\Desktop\cursor-chat.png"

