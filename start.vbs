Option Explicit

' ============================================================
'   中医AI诊疗系统 - 步进式静默启动脚本 v3.5
'   1. 修复脉搏服务优先使用虚拟环境
'   2. 全后台无窗口运行
'   3. 身份证服务、后端、AI、脉搏、前端全覆盖
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
    ' 参数 0 表示隐藏窗口
    WshShell.Run "cmd /c cd /d """ & demoDir & """ && mvn spring-boot:run", 0, False
    MsgBox "后端服务(8080)已在后台启动。" & vbCrLf & "等待后端初始化（约10-20秒）后点击【确定】。", 64, "步骤 1/5"
Else
    AppendSummary "[跳过] 后端目录未找到 pom.xml"
End If

' ---------- [2] TCM AI 服务 ----------
If fso.FileExists(aiDir & "\main.py") Then
    Dim aiPython
    ' 优先检测虚拟环境
    If fso.FileExists(aiDir & "\venv\Scripts\python.exe") Then
        aiPython = aiDir & "\venv\Scripts\python.exe"
    Else
        aiPython = "python"
    End If
    
    WshShell.Run "cmd /c cd /d """ & aiDir & """ && """ & aiPython & """ main.py", 0, False
    MsgBox "AI 服务(5000)已在后台启动。" & vbCrLf & "YOLO模型加载需要时间，请稍候点击【确定】。", 64, "步骤 2/5"
Else
    AppendSummary "[跳过] AI 服务目录未找到 main.py"
End If

' ---------- [3] 脉搏算法服务 ----------
If fso.FileExists(pulseDir & "\main.py") Then
    Dim pulsePython
    ' 【核心修复】：优先检测脉搏目录下的虚拟环境
    If fso.FileExists(pulseDir & "\venv\Scripts\python.exe") Then
        pulsePython = pulseDir & "\venv\Scripts\python.exe"
    Else
        pulsePython = "python"
    End If
    
    WshShell.Run "cmd /c cd /d """ & pulseDir & """ && """ & pulsePython & """ main.py", 0, False
    MsgBox "脉搏算法(8000)已在后台启动。" & vbCrLf & "确认无误后点击【确定】启动身份证服务。", 64, "步骤 3/5"
Else
    AppendSummary "[跳过] 脉搏服务目录未找到 main.py"
End If

' ---------- [4] 身份证读卡服务 ----------
If fso.FolderExists(idCardDir) Then
    If fso.FileExists(idCardDir & "\run.bat") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && run.bat", 0, False
    ElseIf fso.FileExists(idCardDir & "\IdCardReaderService\IdCardReaderService.csproj") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && dotnet run --project IdCardReaderService\IdCardReaderService.csproj", 0, False
    ElseIf fso.FileExists(idCardDir & "\main.py") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && python main.py", 0, False
    End If
    MsgBox "身份证读卡服务(9009)已启动。" & vbCrLf & "点击【确定】启动前端服务。", 64, "步骤 4/5"
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
    MsgBox "前端服务(5173)已发送启动指令。" & vbCrLf & "待 Vite 编译完成后点击【确定】打开浏览器。", 64, "步骤 5/5"
Else
    AppendSummary "[跳过] 前端目录未找到 package.json"
End If

' ---------- 最后：打开浏览器 ----------
WScript.Sleep 2000
OpenFrontendBrowser

If Len(summary) > 0 Then
    MsgBox "启动流程结束。部分异常说明：" & vbCrLf & summary, 48, "运行状态"
End If

' --- 功能子程序 ---

Sub KillPort(port)
    On Error Resume Next
    Dim oExec, line, pid, parts, i
    ' 查找占用指定端口的监听进程
    Set oExec = WshShell.Exec("cmd /c netstat -ano | findstr LISTENING | findstr :" & port)
    Do While Not oExec.StdOut.AtEndOfStream
        line = Trim(oExec.StdOut.ReadLine())
        If InStr(line, ":" & port & " ") > 0 Then
            parts = Split(line, " ")
            ' 获取行末的 PID
            For i = UBound(parts) To 0 Step -1
                If Trim(parts(i)) <> "" Then
                    pid = Trim(parts(i))
                    Exit For
                End If
            Next
            If IsNumeric(pid) And CInt(pid) > 4 Then
                WshShell.Run "taskkill /PID " & pid & " /F", 0, True
            End If
        End If
    Loop
    On Error GoTo 0
End Sub

Sub OpenFrontendBrowser()
    Dim url : url = "http://localhost:5173"
    ' 优先级检测：Chrome -> Edge -> 系统默认
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
End SubOption Explicit

' ============================================================
'   ��ҽAI����ϵͳ - ��Ĭ���������ű� v3.0
'   �ص㣺�޺ڿ򡢺�̨���С��ֶ����ȷ�Ͻ�����һ��
' ============================================================

Dim WshShell, fso, scriptDir
Dim demoDir, aiDir, pulseDir, vueDir, idCardDir
Dim summary

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' �ű�����Ŀ¼
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' Ŀ¼����
demoDir   = scriptDir & "\demo"
aiDir     = scriptDir & "\tcm-ai-service"
pulseDir    = scriptDir & "\pulse2"
vueDir      = scriptDir & "\Vue\zhongyi"
idCardDir   = scriptDir & "\IdCardReaderService"

summary = ""

' ����ǰ���
If Not fso.FolderExists(demoDir) Then
    MsgBox "�Ҳ��� demo Ŀ¼������ű�����λ�á�", 16, "����ʧ��"
    WScript.Quit 1
End If

' �����ɶ˿�ռ��
KillPort 8080
KillPort 5000
KillPort 8000
KillPort 5173
KillPort 9009

' ---------- [1] Spring Boot ��� ----------
If fso.FileExists(demoDir & "\pom.xml") Then
    ' ʹ�� 0 ����ʵ���޺ڿ�����
    WshShell.Run "cmd /c cd /d """ & demoDir & """ && mvn spring-boot:run", 0, False
    MsgBox "��˷���(8080)���ں�̨������" & vbCrLf & "���Ժ�Ƭ�̣�ȷ�Ϻ�˾���������ȷ�������� AI ����", 64, "���� 1/5"
Else
    AppendSummary "[����] δ�ҵ���� pom.xml"
End If

' ---------- [2] TCM AI ���� ----------
If fso.FileExists(aiDir & "\main.py") Then
    If fso.FileExists(aiDir & "\venv\Scripts\python.exe") Then
        WshShell.Run "cmd /c cd /d """ & aiDir & """ && venv\Scripts\python.exe main.py", 0, False
    Else
        WshShell.Run "cmd /c cd /d """ & aiDir & """ && python main.py", 0, False
    End If
    MsgBox "AI ����(5000)���ں�̨������" & vbCrLf & "������ȷ�������������㷨����", 64, "���� 2/5"
Else
    AppendSummary "[����] δ�ҵ� AI ���� main.py"
End If

' ---------- [3] �����㷨���� ----------
If fso.FileExists(pulseDir & "\main.py") Then
    WshShell.Run "cmd /c cd /d """ & pulseDir & """ && python main.py", 1, False
    MsgBox "�����㷨(8000)���ں�̨������" & vbCrLf & "������ȷ������������֤��������", 64, "���� 3/5"
Else
    AppendSummary "[����] δ�ҵ��������� main.py"
End If

' ---------- [4] ����֤�������� ----------
If fso.FolderExists(idCardDir) Then
    If fso.FileExists(idCardDir & "\run.bat") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && run.bat", 0, False
        MsgBox "����֤����(9009)��ͨ�� bat ������" & vbCrLf & "������ȷ��������ǰ�˷���", 64, "���� 4/5"
    ElseIf fso.FileExists(idCardDir & "\IdCardReaderService\IdCardReaderService.csproj") Then
        WshShell.Run "cmd /c cd /d """ & idCardDir & """ && dotnet run --project IdCardReaderService\IdCardReaderService.csproj", 0, False
        MsgBox "����֤����(9009)��ͨ�� dotnet ������" & vbCrLf & "������ȷ��������ǰ�˷���", 64, "���� 4/5"
    End If
Else
    AppendSummary "[����] δ�ҵ�����֤���������ļ���"
End If

' ---------- [5] Vue3 ǰ�� ----------
If fso.FileExists(vueDir & "\package.json") Then
    If Not fso.FolderExists(vueDir & "\node_modules") Then
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm install && npm run dev", 0, False
    Else
        WshShell.Run "cmd /c cd /d """ & vueDir & """ && npm run dev", 0, False
    End If
    MsgBox "ǰ�˷���(5173)���������ѷ��͡�" & vbCrLf & "���Ե� Vite ������ɣ������ȷ�������������", 64, "���� 5/5"
Else
    AppendSummary "[����] δ�ҵ�ǰ�� package.json"
End If

' ---------- ��󣺴������ ----------
OpenFrontendBrowser

If Len(summary) > 0 Then
    MsgBox "������ϡ�����ģ��״̬��" & vbCrLf & summary, 48, "��ʾ"
End If

' --- �ӳ������� ---

Sub KillPort(port)
    Dim oExec, line, pid, parts
    On Error Resume Next
    ' ��Ĭ���Ҳ�ǿɱ�˿�
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
    ' ����Ѱ���������ȫ����
    Dim browserPath, url
    url = "http://localhost:5173"
    
    ' �����������ȼ���Chrome -> Edge -> ϵͳĬ��
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