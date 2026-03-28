Dim WshShell, scriptDir, chrome, edge, fso

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

WshShell.Run "cmd /c cd /d """ & scriptDir & "demo"" && mvn spring-boot:run", 0, False

WshShell.Run "cmd /c cd /d """ & scriptDir & "tcm-ai-service"" && python main.py", 0, False

WScript.Sleep 2000

WshShell.Run "cmd /c cd /d """ & scriptDir & "pulse2"" && python main.py", 0, False

WScript.Sleep 2000

WshShell.Run "cmd /c cd /d """ & scriptDir & "Vue\zhongyi"" && npm run dev", 0, False

WScript.Sleep 2000

chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
edge   = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

If fso.FileExists(chrome) Then
    WshShell.Run """" & chrome & """ --start-fullscreen http://localhost:5173", 1, False
ElseIf fso.FileExists(edge) Then
    WshShell.Run """" & edge & """ --start-fullscreen http://localhost:5173", 1, False
Else
    WshShell.Run "explorer http://localhost:5173", 1, False
End If

Set WshShell = Nothing
Set fso = Nothing
