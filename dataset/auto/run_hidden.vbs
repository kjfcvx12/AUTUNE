' Starts run_auto.ps1 with no console window, so the 30-minute task never flashes on screen.
CreateObject("WScript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""F:\0final\AUTUNE\dataset\auto\run_auto.ps1""", 0, False
