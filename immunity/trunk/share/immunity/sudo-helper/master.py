#!/usr/bin/python

import immunity, os, pwd, sys
from os.path import isdir

def reduce_capabilities():
  immunity.set_cap("cap_setgid,cap_setuid,cap_sys_admin,cap_sys_chroot+ep")

def clear_environment():
  language = os.getenv("LANG")
  for key in os.environ.keys():
    os.unsetenv(key)
  os.putenv("DISPLAY", ":0")
  os.putenv("LANG", language)
  os.putenv("PATH", "/bin:/usr/bin")

def get_xauth():
  (input, output) = os.popen2(("/usr/share/immunity/get_xauth.py",), "r")
  return output.readline()

def new_namespace():
  immunity.unshare_newns()

def mount_bind(dir):
  target = "/mnt" + dir
  os.makedirs(target)
  immunity.mount_bind(dir, target)

def secure_dev():
  os.makedirs("/mnt/dev")
  immunity.mount("tmpfs", "/mnt/dev", "tmpfs")
  os.spawnlp(os.P_WAIT, "cp", "cp", "-a", "/dev/null", "/mnt/dev/")
  os.spawnlp(os.P_WAIT, "cp", "cp", "-a", "/dev/snd", "/mnt/dev/")
  for dev_file in os.listdir("/mnt/dev/snd"):
    os.chmod("/mnt/dev/snd/" + dev_file, 0666)

def fake_filesystem():
  immunity.mount("tmpfs", "/mnt", "tmpfs")
  mount_bind("/bin")
  mount_bind("/etc")
  mount_bind("/lib")
  mount_bind("/tmp/.X11-unix")
  mount_bind("/usr")
  mount_bind("/var")
  os.chmod("/mnt/tmp", 0777)
  immunity.mount("tmpfs", "/mnt/var/tmp", "tmpfs")
  secure_dev()
  os.chroot("/mnt")

def switch_user(target_user):
  pwd_data = pwd.getpwnam(target_user)
  os.setgid(pwd_data[3])
  os.setgroups([])
  os.setuid(pwd_data[2])
  os.putenv("USER", pwd_data[0])
  homedir = pwd_data[5]
  os.putenv("HOME", homedir)
  os.chdir(homedir)

def set_xauth(data):
  (input, output) = os.popen2(("xauth", "nmerge", "-"), "w")
  input.write(data)
  input.close()

def main():
  reduce_capabilities()

  sudo_user = os.getenv("SUDO_USER")
  xauth_data = get_xauth()
  clear_environment()

  new_namespace()
  fake_filesystem()

  switch_user("immunity-" + sudo_user)

  set_xauth(xauth_data)

def exec_command():
  if len(sys.argv) > 1:
    command = sys.argv[1]
  else:
    command = "/bin/sh"
  args = [command]
  args.extend(sys.argv[2:])
  os.execvp(command, args)

main()
exec_command()
