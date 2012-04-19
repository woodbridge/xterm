from fabric.api import local, run, cd, env
import os

env.user = 'justin'
env.hosts = ['justinwoodbridge.com']
env.code_dir = '/var/www/xterm'
env.pid_dir = os.path.join(env.code_dir, 'pids')

def stop():
  # If the app wasn't running, that's okay.
  env.warn_only = True
  with cd(env.code_dir):
    run('kill -HUP `cat %s/app.pid`' % env.pid_dir, pty=True)

def start():
  with cd(env.code_dir):
    run('XTERM_ENV=production python app.py')

def install_deps():
  with cd(env.code_dir):
    run('sudo pip install -r requirements.txt')

def deploy():
  local('git push')
  with cd(env.code_dir):
    run('git pull')
    # install_deps()
    stop()
    start()

def tail():
  with cd(os.path.join(env.code_dir, 'logs')):
    run('tail -f *.log', pty=True)