Set WshShell = CreateObject("WScript.Shell")
userProfile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
pythonExe = userProfile & "\.local\bin\python3.11.exe"
WshShell.CurrentDirectory = "d:\안티그래비티파이튼\market_monitor"
WshShell.Run Chr(34) & pythonExe & Chr(34) & " monitor_web.py", 0, False
