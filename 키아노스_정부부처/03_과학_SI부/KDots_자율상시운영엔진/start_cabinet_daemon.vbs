Set WshShell = CreateObject("WScript.Shell")
strDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run """C:\Program Files\nodejs\node.exe"" """ & strDir & "\kdots_feed_server.js""", 0, True
