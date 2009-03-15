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

def makedirs(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)

def mount_bind(path):
  target = "/mnt" + path
  if os.path.isdir(path):
    makedirs(target)
  else:
    makedirs(os.path.dirname(target))
    open(target, "w").close()
  immunity.mount_bind(path, target)

def mount_tmpfs(dir):
  makedirs(dir)
  immunity.mount("tmpfs", dir, "tmpfs")
  os.chmod(dir, 0755)

def alsa():
  makedirs("/mnt/dev")
  os.spawnlp(os.P_WAIT, "cp", "cp", "-a", "/dev/snd", "/mnt/dev/")
  for dev_file in os.listdir("/mnt/dev/snd"):
    os.chmod("/mnt/dev/snd/" + dev_file, 0666)

def fake_filesystem():
  mount_tmpfs("/mnt")
  mount_bind("/bin")
  mount_bind("/dev/null")
  mount_bind("/etc/X11")
  mount_bind("/etc/alternatives")
  mount_bind("/etc/fonts")
  mount_bind("/etc/gai.conf")
  mount_bind("/etc/gconf")
  mount_bind("/etc/gnome-vfs-2.0")
  mount_bind("/etc/gtk-2.0")
  mount_bind("/etc/host.conf")
  mount_bind("/etc/hosts")
  mount_bind("/etc/iceweasel")
  mount_bind("/etc/ld.so.cache")
  mount_bind("/etc/locale.alias")
  mount_bind("/etc/localtime")
  mount_bind("/etc/mime.types")
  mount_bind("/etc/nsswitch.conf")
  mount_bind("/etc/orbitrc")
  mount_bind("/etc/pango")
  mount_bind("/etc/passwd")
  mount_bind("/etc/resolv.conf")
  mount_bind("/etc/resolvconf")
  mount_bind("/lib")
  mount_bind("/proc")
  mount_bind("/tmp/.X11-unix")
  mount_bind("/usr/bin")
  mount_bind("/usr/lib")
  mount_bind("/usr/share")
  mount_bind("/var/cache/fontconfig")
  mount_bind("/var/lib/defoma")
  mount_bind("/var/lib/gconf")
  mount_bind("/var/lib/immunity")
  immunity.set_cap("cap_setgid,cap_setuid,cap_sys_chroot+ep")
  os.chmod("/mnt/tmp", 0777)
  alsa()
  os.chroot("/mnt")
  immunity.set_cap("cap_setgid,cap_setuid+ep")

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
