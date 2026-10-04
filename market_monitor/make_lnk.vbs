Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("C:\Users\태봉\OneDrive\Desktop\키아노스 마켓 펄스.lnk")
shortcut.TargetPath = "wscript.exe"
shortcut.Arguments = Chr(34) & "d:\안티그래비티파이튼\market_monitor\run_silent.vbs" & Chr(34)
shortcut.WorkingDirectory = "d:\안티그래비티파이튼\market_monitor"
shortcut.WindowStyle = 7
shortcut.Description = "키아노스 마켓 펄스 실시간 금융 인텔리전스"
shortcut.IconLocation = "C:\Windows\System32\shell32.dll,220"
shortcut.Save
