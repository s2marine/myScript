#Region ;**** ���������� ACNWrapper_GUI ****
#PRE_Icon=E:\Ruijie Supplicant\8021x.exe
#PRE_Compression=4
#PRE_UseX64=n
#PRE_Res_requestedExecutionLevel=None
#EndRegion ;**** ���������� ACNWrapper_GUI ****

$path = IniRead('ruijie.ini', 'ruijie', 'path', '')
$local = IniRead('ruijie.ini', 'ruijie', 'local', '')
$vpn = IniRead('ruijie.ini', 'ruijie', 'VPN', '')
$username = IniRead('ruijie.ini', 'ruijie', 'username', '')
$passwd = IniRead('ruijie.ini', 'ruijie', 'passwd', '')
$num = Random(2, 254, 1)
$result = RunWait('netsh interface ip set address "' & $local & '" static 192.168.1.' & $num & ' 255.255.255.0 192.168.1.1 1', '', @SW_HIDE)
If( $result<>0 Or @error<>0 ) Then
	MsgBox(16, "����", "����������local�������ô���Ŷ...")
	Exit(1)
EndIf

$s = StringSplit($path, '\')
$dir = ""
For $i = 1 To $s[0]-1 Step 1
	$dir = $dir & $s[$i] & "\"
Next

$result = Run($path, $dir)
If( $result==0 Or @error<>0 ) Then
	MsgBox(16, "����", "���·���������ô���Ŷ...")
	Exit(1)
EndIf

WinWait("������ѧ��֤�ͻ���")
Sleep(500)
ControlClick("������ѧ��֤�ͻ���", "", "Button1", "left", 1)
WinWait("[CLASS:#32770]", "����������ʾ")
WinClose("[LAST]")
Sleep(5000)

$result = RunWait('netsh interface ip set address "' & $local & '" dhcp', '', @SW_HIDE)
If( $result<>0 Or @error<>0 ) Then
	MsgBox(16, "����", "�Ҳ�֪��������ʲô...")
	Exit(1)
EndIf

TrayTip("��ʾ", "���ĵȴ�������~", 5, 1)
$find = WinWait("[CLASS:#32770]", "������������", 110)

If($find) Then
	MsgBox(16, "����", "��ϲ�㣬������������һ�������������󣬽���������£�"&@CRLF&"������������"&@CRLF&"ж�����������ٸ���"&@CRLF&"���°�װԭ��win7"&@CRLF&"����֮ǰ���ܵ���Ʒ����")
	Exit(1)
EndIf

WinWait("[CLASS:#32770]", "����������ʾ")
WinClose("[LAST]")

If($vpn And	$username And $passwd) Then
	$result = RunWait('rasdial "'& $vpn & '" ' & $username & ' ' & $passwd, '', @SW_HIDE)
	If( $result<>0 Or @error<>0 ) Then
		MsgBox(16, "����", "vpn�������û��������Լ�����������˰�...")
		Exit(1)
	EndIf
EndIf


MsgBox(64, "��������", "      ò�Ƴɹ���~         ", 5)