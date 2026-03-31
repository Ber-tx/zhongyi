Option Explicit

' ============================================================
'   中医AI诊疗系统 - 步进式静默启动脚本 v4.0 (修复虚拟环境隔离BUG)
'   1. 彻底绕过 activate 脚本，直接调用解释器路径
'   2. 自动检测并强制关联 AI 和 脉搏服务的 Python 环境
'   3. 修复中文路径/特殊字符的路径转义问题
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
pulseDir  = scriptDir & "\pulse2"
vueDir    = scriptDir & "\Vue\zhongyi"
idCardDir = scriptDir & "\IdCardReaderService"

summary = ""

' 启动前检查
If Not fso.FolderExists(demoDir) Then
    MsgBox "找不到项目根目录，请确保脚本放在正确位置。" & vbCrLf & "检测路径：" & demoDir, 16, "启动失败"
    WScript.Quit 1
End If

' 预清理：释放所有相关端口
KillPort 8080
KillPort 5000
KillPort 8000
KillPort 5173
KillPort 9009

' ---------- [1] Spring Boot 后端 ----------
If fso.FileExists(demoDir & "\pom.xml") Then
    WshShell.Run "cmd /c cd /d """ & demoDir & """ && mvn spring-boot:run", 0, False
    MsgBox "后端服务(8080)已在后台启动。" & vbCrLf & "等待后端初始化（约10-20秒）后点击【确定】。", 64, "步骤 1/5"
Else
    AppendSummary "[跳过] 后端目录未找到 pom.xml"
End If

' ---------- [2] TCM AI 服务 (修复核心) ----------
If fso.FileExists(aiDir & "\main.py") Then
    Dim aiExe
    ' 检查 .venv 文件夹（你截图里用的是 .venv）
    If fso.FileExists(aiDir & "\.venv\Scripts\python.exe") Then
        aiExe = """" & aiDir & "\.venv\Scripts\python.exe"""
    ElseIf fso.FileExists(aiDir & "\venv\Scripts\python.exe") Then
        aiExe = """" & aiDir & "\venv\Scripts\python.exe"""
    Else
        aiExe = "python"
    End If
    
    ' 直接调用 python.exe main.py，不走 activate 逻辑
    WshShell.Run "cmd /c cd /d """ & aiDir & """ && " & aiExe & " main.py", 0, False
    MsgBox "AI 服务(5000)已启动。" & vbCrLf & "已尝试绕过虚拟环境激活逻辑，直接调用解释器。", 64, "步骤 2/5"
Else
    AppendSummary "[跳过] AI 服务目录未找到 main.py"
End If

' ---------- [3] 脉搏算法服务 (同步修复) ----------
If fso.FileExists(pulseDir & "\main.py") Then
    Dim pulseExe
    If fso.FileExists(pulseDir & "\.venv\Scripts\python.exe") Then
        pulseExe = """" & pulseDir & "\.venv\Scripts\python.exe"""
    ElseIf fso.FileExists(pulseDir & "\venv\Scripts\python.exe") Then
        pulseExe = """" & pulseDir & "\venv\Scripts\python.exe"""
    Else
        pulseExe = "python"
    End If
    
    WshShell.Run "cmd /c cd /d """ & pulseDir & """ && " & pulseExe & " main.py", 0, False
    MsgBox "脉搏算法(8000)已在后台启动。", 64, "步骤 3/5"
Else
    AppendSummary "[跳过] 脉搏服务目录未找到 main.py"
End If

' ---------- [4] 身份证读卡服务 ----------
' (保持原逻辑)
If fso.FolderExists(idCardDir) Then
    If fso.FileExists(idCardDir & "\run.bat") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && run.bat", 0, False
    ElseIf fso.FileExists(idCardDir & "\main.py") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && python main.py", 0, False
    End If
    MsgBox "身份证读卡服务(9009)已启动。", 64, "步骤 4/5"
End If

' ---------- [5] Vue3 前端 ----------
If fso.FileExists(vueDir & "\package.json") Then
    If Not fso.FolderExists(vueDir & "\node_modules") Then
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm install && npm run dev", 0, False
    Else
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm run dev", 0, False
    End If
    MsgBox "前端服务(5173)启动中... 准备打开浏览器。", 64, "步骤 5/5"
End If

' ---------- 最后：打开浏览器 ----------
WScript.Sleep 2000
OpenFrontendBrowser

If Len(summary) > 0 Then
    MsgBox "启动流程结束。异常报告：" & vbCrLf & summary, 48, "运行状态"
End If

' --- 功能子程序 ---

Sub KillPort(port)
    On Error Resume Next
    Dim objExec, strOutput, strLine, objRegExp, objMatch, objMatches
    Set objRegExp = New RegExp
    objRegExp.Pattern = "\s+LISTENING\s+(\d+)" ' 匹配最后一位 PID
    
    Set objExec = WshShell.Exec("cmd /c netstat -ano | findstr :" & port)
    Do While Not objExec.StdOut.AtEndOfStream
        strLine = objExec.StdOut.ReadLine()
        If InStr(strLine, "LISTENING") > 0 Then
            Set objMatches = objRegExp.Execute(strLine)
            For Each objMatch In objMatches
                WshShell.Run "taskkill /PID " & objMatch.SubMatches(0) & " /F", 0, True
            Next
        End If
    Loop
End Sub

Sub OpenFrontendBrowser()
    Dim url : url = "http://localhost:5173"
    If fso.FileExists("C:\Program Files\Google\Chrome\Application\chrome.exe") Then
        WshShell.Run """C:\Program Files\Google\Chrome\Application\chrome.exe"" --start-fullscreen " & url, 1, False
    Else
        WshShell.Run "explorer " & url, 1, False
    End If
End Sub

Sub AppendSummary(text)
    summary = summary & text & vbCrLf
End Sub