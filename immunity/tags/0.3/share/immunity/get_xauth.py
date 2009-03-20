#!/usr/bin/python

import immunity, os

immunity.set_cap("")
os.execl("/usr/bin/xauth", "xauth", "nlist", ":0")
