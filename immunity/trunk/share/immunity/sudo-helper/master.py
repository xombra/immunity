#!/usr/bin/python

import os, pwd
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

  switch_user("immunity-" + sudo_user)

  set_xauth(xauth_data)

def exec_browser():
  os.execl("/usr/bin/firefox", "immunity", "-a", "immunity")

main()
exec_browser()
