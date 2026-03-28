Dim WshShell, fso, scriptDir, objWMIService, colProcesses, objProcess, cmdLine

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMIService.ExecQuery("Select * from Win32_Process")

For Each objProcess In colProcesses
    On Error Resume Next
    cmdLine = LCase(objProcess.CommandLine & "")

    If cmdLine <> "" Then
        If InStr(cmdLine, LCase(scriptDir & "demo")) > 0 _
           Or InStr(cmdLine, LCase(scriptDir & "tcm-ai-service")) > 0 _
           Or InStr(cmdLine, LCase(scriptDir & "pulse2")) > 0 _
           Or InStr(cmdLine, LCase(scriptDir & "Vue\\zhongyi")) > 0 _
           Or InStr(cmdLine, "mvn") > 0 _
           Or InStr(cmdLine, "spring-boot:run") > 0 _
        Then
            objProcess.Terminate()
        End If
    End If
    On Error GoTo 0
Next

' Fallbacks: terminate common runtimes that may be left behind
WshShell.Run "taskkill /F /IM node.exe /T", 0, True
WshShell.Run "taskkill /F /IM python.exe /T", 0, True
WshShell.Run "taskkill /F /IM java.exe /T", 0, True

' Close common browsers
WshShell.Run "taskkill /F /IM chrome.exe /T", 0, True
WshShell.Run "taskkill /F /IM msedge.exe /T", 0, True

Set WshShell = Nothing
Set fso = Nothing
Set objWMIService = Nothing
Set colProcesses = Nothing
Set objProcess = Nothing
