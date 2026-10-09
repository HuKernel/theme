import os, paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(os.environ['WSSH_HOST'], username=os.environ['WSSH_USER'], password=os.environ['WSSH_PASS'], timeout=30)
sftp = c.open_sftp()
sftp.put(os.path.join('E:', os.sep, '桌面', 'theme', 'style-catalog.html'), 'C:/www/theme/style-catalog.html')
print('deployed')
c.close()
