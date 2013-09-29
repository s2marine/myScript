#Region ;**** 参数创建于 ACNWrapper_GUI ****
#PRE_Icon=E:\Ruijie Supplicant\8021x.exe
#PRE_Compression=4
#PRE_UseX64=n
#PRE_Res_requestedExecutionLevel=None
#EndRegion ;**** 参数创建于 ACNWrapper_GUI ****

$path = IniRead('ruijie.ini', 'ruijie', 'path', '')
$local = IniRead('ruijie.ini', 'ruijie', 'local', '')
$vpn = IniRead('ruijie.ini', 'ruijie', 'VPN', '')
$username = IniRead('ruijie.ini', 'ruijie', 'username', '')
$passwd = IniRead('ruijie.ini', 'ruijie', 'passwd', '')
$num = Random(2, 254, 1)
$result = RunWait('netsh interface ip set address "' & $local & '" static 192.168.1.' & $num & ' 255.255.255.0 192.168.1.1 1', '', @SW_HIDE)
If( $result<>0 Or @error<>0 ) Then
	MsgBox(16, "错误", "本地连接名local可能设置错了哦...")
	Exit(1)
EndIf

$s = StringSplit($path, '\')
$dir = ""
For $i = 1 To $s[0]-1 Step 1
	$dir = $dir & $s[$i] & "\"
Next

$result = Run($path, $dir)
If( $result==0 Or @error<>0 ) Then
	MsgBox(16, "错误", "锐捷路径可能设置错了哦...")
	Exit(1)
EndIf

WinWait("集美大学认证客户端")
Sleep(500)
ControlClick("集美大学认证客户端", "", "Button1", "left", 1)
WinWait("[CLASS:#32770]", "管理中心提示")
WinClose("[LAST]")
Sleep(5000)

$result = RunWait('netsh interface ip set address "' & $local & '" dhcp', '', @SW_HIDE)
If( $result<>0 Or @error<>0 ) Then
	MsgBox(16, "错误", "我不知道发生了什么...")
	Exit(1)
EndIf

TrayTip("提示", "耐心等待两分钟~", 5, 1)
$find = WinWait("[CLASS:#32770]", "网卡连接正常", 110)

If($find) Then
	MsgBox(16, "错误", "恭喜你，遇见了万中无一的网卡驱动错误，解决方法如下："&@CRLF&"更新网卡驱动"&@CRLF&"卸载网卡驱动再更新"&@CRLF&"重新安装原版win7"&@CRLF&"用上之前积攒的人品祈祷吧")
	Exit(1)
EndIf

WinWait("[CLASS:#32770]", "管理中心提示")
WinClose("[LAST]")

If($vpn And	$username And $passwd) Then
	$result = RunWait('rasdial "'& $vpn & '" ' & $username & ' ' & $passwd, '', @SW_HIDE)
	If( $result<>0 Or @error<>0 ) Then
		MsgBox(16, "错误", "vpn连接名用户名密码自己找找哪里错了吧...")
		Exit(1)
	EndIf
EndIf


MsgBox(64, "当当当当", "      貌似成功了~         ", 5)