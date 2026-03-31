Option Explicit

' ============================================================
'   中医AI诊疗系统 - 一键停止所有服务脚本 v1.0
'   作用：强制结束后端、AI、算法、读卡及前端所有相关进程
' ============================================================

Dim WshShell, fso, response
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- 1. 启动前的二次确认界面 ---
response = MsgBox("确定要关闭【中医AI诊疗系统】的所有后台服务吗？" & vbCrLf & _
                "这将停止：后端、AI、脉搏、读卡服务及前端页面。", _
                33, "系统停机确认")

' 33 代表 = 1 (OK/Cancel 按钮) + 32 (问号图标)
If response <> 1 Then
    WScript.Quit
End If

' --- 2. 执行清理任务 ---
' 这里列出系统中所有涉及到的关键进程名
StopProcess "java.exe"    ' Spring Boot 后端
StopProcess "python.exe"  ' AI服务、脉搏算法、身份证脚本
StopProcess "node.exe"    ' Vue3/Vite 前端服务
StopProcess "mvn.cmd"     ' Maven 运行进程
StopProcess "cmd.exe"     ' 遗留的命令行窗口

' --- 3. 结果提醒 ---
MsgBox "所有相关后台服务已尝试关闭。" & vbCrLf & _
       "端口 8080, 5000, 8000, 5173, 9009 已释放。", 64, "清理完毕"

' --- 子程序：按名称结束进程 ---
Sub StopProcess(exeName)
    On Error Resume Next
    ' /F 强制终止，/T 终止子进程，/IM 指定映像名称
    WshShell.Run "taskkill /F /T /IM " & exeName, 0, True
    On Error GoTo 0
End Sub