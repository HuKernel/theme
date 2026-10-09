import os, paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(os.environ['WSSH_HOST'], username=os.environ['WSSH_USER'], password=os.environ['WSSH_PASS'], timeout=25)
sftp = c.open_sftp()
sftp.put(os.path.join('E:', os.sep, '桌面', 'theme', 'liquid-glass.html'), 'C:/www/theme/liquid-glass.html')
print('deployed')
c.close()
