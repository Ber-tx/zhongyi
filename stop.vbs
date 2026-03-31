Option Explicit

' ============================================================
'   中医AI诊疗系统 - 静默步进启动脚本 v3.0
'   特点：无黑框、后台运行、手动点击确认进入下一步
' ============================================================

Dim WshShell, fso, scriptDir
Dim demoDir, aiDir, pulseDir, vueDir, idCardDir
Dim summary

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 脚本所在目录
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' 目录配置
demoDir   = scriptDir & "\demo"
aiDir     = scriptDir & "\tcm-ai-service"
pulseDir    = scriptDir & "\pulse2"
vueDir      = scriptDir & "\Vue\zhongyi"
idCardDir   = scriptDir & "\IdCardReaderService"

summary = ""

' 启动前检查
If Not fso.FolderExists(demoDir) Then
    MsgBox "找不到 demo 目录，请检查脚本放置位置。", 16, "启动失败"
    WScript.Quit 1
End If

' 清理旧端口占用
KillPort 8080
KillPort 5000
KillPort 8000
KillPort 5173
KillPort 9009

' ---------- [1] Spring Boot 后端 ----------
If fso.FileExists(demoDir & "\pom.xml") Then
    ' 使用 0 参数实现无黑框运行
    WshShell.Run "cmd /c cd /d """ & demoDir & """ && mvn spring-boot:run", 0, False
    MsgBox "后端服务(8080)已在后台启动。" & vbCrLf & "请稍候片刻，确认后端就绪后点击【确定】启动 AI 服务。", 64, "步骤 1/5"
Else
    AppendSummary "[跳过] 未找到后端 pom.xml"
End If

' ---------- [2] TCM AI 服务 ----------
If fso.FileExists(aiDir & "\main.py") Then
    If fso.FileExists(aiDir & "\venv\Scripts\python.exe") Then
        WshShell.Run "cmd /c cd /d """ & aiDir & """ && venv\Scripts\python.exe main.py", 0, False
    Else
        WshShell.Run "cmd /c cd /d """ & aiDir & """ && python main.py", 0, False
    End If
    MsgBox "AI 服务(5000)已在后台启动。" & vbCrLf & "请点击【确定】启动脉搏算法服务。", 64, "步骤 2/5"
Else
    AppendSummary "[跳过] 未找到 AI 服务 main.py"
End If

' ---------- [3] 脉搏算法服务 ----------
If fso.FileExists(pulseDir & "\main.py") Then
    WshShell.Run "cmd /c cd /d """ & pulseDir & """ && python main.py", 0, False
    MsgBox "脉搏算法(8000)已在后台启动。" & vbCrLf & "请点击【确定】启动身份证读卡服务。", 64, "步骤 3/5"
Else
    AppendSummary "[跳过] 未找到脉搏服务 main.py"
End If

' ---------- [4] 身份证读卡服务 ----------
If fso.FolderExists(idCardDir) Then
    If fso.FileExists(idCardDir & "\run.bat") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && run.bat", 0, False
        MsgBox "身份证服务(9009)已通过 bat 启动。" & vbCrLf & "请点击【确定】启动前端服务。", 64, "步骤 4/5"
    ElseIf fso.FileExists(idCardDir & "\IdCardReaderService\IdCardReaderService.csproj") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && dotnet run --project IdCardReaderService\IdCardReaderService.csproj", 0, False
        MsgBox "身份证服务(9009)已通过 dotnet 启动。" & vbCrLf & "请点击【确定】启动前端服务。", 64, "步骤 4/5"
    End If
Else
    AppendSummary "[跳过] 未找到身份证读卡服务文件夹"
End If

' ---------- [5] Vue3 前端 ----------
If fso.FileExists(vueDir & "\package.json") Then
    If Not fso.FolderExists(vueDir & "\node_modules") Then
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm install && npm run dev", 0, False
    Else
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm run dev", 0, False
    End If
    MsgBox "前端服务(5173)启动命令已发送。" & vbCrLf & "请稍等 Vite 编译完成，点击【确定】打开浏览器。", 64, "步骤 5/5"
Else
    AppendSummary "[跳过] 未找到前端 package.json"
End If

' ---------- 最后：打开浏览器 ----------
OpenFrontendBrowser

If Len(summary) > 0 Then
    MsgBox "启动完毕。部分模块状态：" & vbCrLf & summary, 48, "提示"
End If

' --- 子程序区域 ---

Sub KillPort(port)
    Dim oExec, line, pid, parts
    On Error Resume Next
    ' 静默查找并强杀端口
    Set oExec = WshShell.Exec("cmd /c netstat -ano")
    Do While Not oExec.StdOut.AtEndOfStream
        line = Trim(oExec.StdOut.ReadLine())
        If InStr(line, ":" & port & " ") > 0 And InStr(line, "LISTEN") > 0 Then
            parts = Split(line, " ")
            pid = Trim(parts(UBound(parts)))
            If IsNumeric(pid) And CInt(pid) > 4 Then
                WshShell.Run "taskkill /PID " & pid & " /F", 0, True
            End If
        End If
    Loop
    On Error GoTo 0
End Sub

Sub OpenFrontendBrowser()
    ' 尝试寻找浏览器并全屏打开
    Dim browserPath, url
    url = "http://localhost:5173"
    
    ' 浏览器检测优先级：Chrome -> Edge -> 系统默认
    If fso.FileExists("C:\Program Files\Google\Chrome\Application\chrome.exe") Then
        WshShell.Run """C:\Program Files\Google\Chrome\Application\chrome.exe"" --start-fullscreen " & url, 1, False
    ElseIf fso.FileExists("C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") Then
        WshShell.Run """C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"" --start-fullscreen " & url, 1, False
    Else
        WshShell.Run "explorer " & url, 1, False
    End If
End Sub

Sub AppendSummary(text)
    summary = summary & text & vbCrLf
End Sub