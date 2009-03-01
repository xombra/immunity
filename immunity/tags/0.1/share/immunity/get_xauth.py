#!/usr/bin/python

import os, pwd

def switch_user(target_user):
  pwd_data = pwd.getpwnam(target_user)
  os.setgid(pwd_data[3])
  os.setgroups([])
  os.setuid(pwd_data[2])
  os.putenv("USER", pwd_data[0])
  homedir = pwd_data[5]
  os.putenv("HOME", homedir)
  os.chdir(homedir)

def get_xauth():
  os.execl("/usr/bin/xauth", "xauth", "nlist", ":0")

def main():
  sudo_user = os.getenv("SUDO_USER")
  switch_user(sudo_user)
  get_xauth()

main()
