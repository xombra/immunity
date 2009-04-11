#!/usr/bin/python

import immunity, os, sys, tempfile

immunity.set_cap("")
xauthfile, name = tempfile.mkstemp()
os.spawnl(os.P_WAIT, "/usr/bin/xauth", "xauth", "-f", name, "generate",
    ":0", ".", "trusted", "timeout", "1200")
xauthfile = open(name, "r")
sys.stdout.write(xauthfile.read())
os.remove(name)
