# -*- coding: utf-8 -*-
# SSH 通道大流量被断：分块 base64 追加写入
import os, base64, time, paramiko

SRC = os.path.join('E:', os.sep, '桌面', 'theme', 'liquid-glass.html')
data = open(SRC, 'rb').read()
b64 = base64.b64encode(data).decode()
CHUNK = 4000
chunks = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)]
print('total b64:', len(b64), 'chunks:', len(chunks))

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(os.environ['WSSH_HOST'], username=os.environ['WSSH_USER'],
          password=os.environ['WSSH_PASS'], timeout=25)

def run(cmd, t=20):
    _, out, err = c.exec_command(cmd, timeout=t)
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    if e:
        raise RuntimeError(e[:150])
    return o

run('powershell -NoProfile -c "Set-Content -Path C:/www/theme/_lg.b64 -Value \'\' -NoNewline"')
for i, ch in enumerate(chunks):
    # 单引号安全：base64 字符集不含单引号
    run('powershell -NoProfile -c "Add-Content -Path C:/www/theme/_lg.b64 -Value \'%s\' -NoNewline"' % ch)
    if (i + 1) % 8 == 0:
        print('  chunk', i + 1, '/', len(chunks))

size = run('powershell -NoProfile -c "(Get-Item C:/www/theme/_lg.b64).Length"')
print('b64 assembled:', size)
run('powershell -NoProfile -c "$b=[IO.File]::ReadAllText(\'C:/www/theme/_lg.b64\'); [IO.File]::WriteAllBytes(\'C:/www/theme/liquid-glass.html\', [Convert]::FromBase64String($b)); Remove-Item C:/www/theme/_lg.b64"')
final = run('powershell -NoProfile -c "(Get-Item C:/www/theme/liquid-glass.html).Length"')
print('final file size on server:', final, '(expect', len(data), ')')
c.close()
