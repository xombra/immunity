#!/usr/bin/python

import immunity, os, pwd, sys
from os.path import isdir

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

def make_tmpdir(tmpdir):
  if not isdir(tmpdir):
    os.mkdir(tmpdir)
  os.putenv("TMP", tmpdir)
  os.putenv("TMPDIR", tmpdir)

def new_namespace():
  immunity.unshare_newns()

def umount_filesystems():
  os.chdir("/")
  immunity.umount("/boot")
  immunity.umount("/home")
  immunity.umount("/lib/init/rw/splashy")
  immunity.umount("/lib/init/rw")
  immunity.umount("/proc/bus/usb")
  immunity.umount("/proc/sys/fs/binfmt_misc")
  immunity.umount("/proc")
  immunity.umount("/sys/fs/fuse/connections")
  immunity.umount("/sys")

def secure_tmp():
  immunity.mount("tmpfs", "/mnt", "tmpfs")
  os.mkdir("/mnt/.X11-unix")
  immunity.mount_bind("/tmp/.X11-unix", "/mnt/.X11-unix")
  immunity.mount_move("/mnt", "/tmp")

def secure_var_tmp():
  immunity.mount("tmpfs", "/var/tmp", "tmpfs")

def secure_dev():
  immunity.mount("tmpfs", "/mnt", "tmpfs")
  os.system("cp -a /dev/null /mnt/")
  os.system("cp -a /dev/snd /mnt/")
  immunity.mount_move("/mnt", "/dev")
  os.system("chmod 666 /dev/snd/*")

def switch_user(target_user):
  pwd_data = pwd.getpwnam(target_user)
  os.setgid(pwd_data[3])
  os.setgroups([])
  os.setuid(pwd_data[2])
  os.putenv("USER", pwd_data[0])
  homedir = pwd_data[5]
  os.putenv("HOME", homedir)
  os.chdir(homedir)
  make_tmpdir(homedir + "/tmp")

def set_xauth(data):
  (input, output) = os.popen2(("xauth", "nmerge", "-"), "w")
  input.write(data)
  input.close()

def main():
  sudo_user = os.getenv("SUDO_USER")
  xauth_data = get_xauth()
  clear_environment()

  new_namespace()
  umount_filesystems()
  secure_tmp()
  secure_var_tmp()
  secure_dev()

  switch_user("immunity-" + sudo_user)

  set_xauth(xauth_data)

def exec_command():
  if len(sys.argv) > 1:
    command = sys.argv[1]
  else:
    command = "/bin/sh"
  args = [command]
  args.extend(sys.argv[2:])
  os.execv(command, args)

main()
exec_command()
