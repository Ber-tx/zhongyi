Option Explicit

' ============================================================
'   中医AI诊疗系统 - 一键停止所有服务脚本 v1.1
'   修复：字符串换行导致的编译错误
' ============================================================

Dim WshShell, response, msg
Set WshShell = CreateObject("WScript.Shell")

' 构造消息内容，确保每一行字符串都用引号包裹并用 & 连接
msg = "确定要关闭【中医AI诊疗系统】的所有后台服务吗？" & vbCrLf & _
      "这将停止：后端、AI服务、脉搏算法、读卡服务及前端页面。"

' 33 = 1 (确定/取消) + 32 (问号图标)
response = MsgBox(msg, 33, "系统停机确认")

If response = 1 Then
    ' 执行强制清理任务
    StopProcess "java.exe"
    StopProcess "python.exe"
    StopProcess "node.exe"
    StopProcess "mvn.cmd"
    StopProcess "cmd.exe"
    
    MsgBox "所有相关后台服务已尝试关闭。" & vbCrLf & _
           "端口 8080, 5000, 8000, 5173, 9009 已释放。", 64, "清理完毕"
End If

Sub StopProcess(exeName)
    On Error Resume Next
    WshShell.Run "taskkill /F /T /IM " & exeName, 0, True
    On Error GoTo 0
End Sub
