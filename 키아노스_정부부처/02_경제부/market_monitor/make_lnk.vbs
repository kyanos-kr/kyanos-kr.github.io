Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
desktopPath = WshShell.SpecialFolders("Desktop")

Set shortcut = WshShell.CreateShortcut(desktopPath & "\???? ?? ??.lnk")
shortcut.TargetPath = "wscript.exe"
shortcut.Arguments = Chr(34) & currentDir & "\run_silent.vbs" & Chr(34)
shortcut.WorkingDirectory = currentDir
shortcut.WindowStyle = 7
shortcut.Description = "???? ?? ?? ??? ?? ?????"
shortcut.IconLocation = currentDir & "\??????.ico,0"
shortcut.Save