#!/usr/bin/python

import immunity, os

def main():
  immunity.set_cap("")
  os.execl("/usr/bin/xauth", "xauth", "nlist", ":0")

main()
