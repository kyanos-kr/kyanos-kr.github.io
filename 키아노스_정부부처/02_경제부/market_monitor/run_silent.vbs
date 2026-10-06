Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
userProfile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
pythonExe = userProfile & "\.local\bin\python3.11.exe"
WshShell.CurrentDirectory = scriptDir
WshShell.Run Chr(34) & pythonExe & Chr(34) & " monitor_web.py", 0, False