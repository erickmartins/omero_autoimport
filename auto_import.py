#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 16:40:47 2018

@author: erick
"""

from import_from_dvs import from_dvs
from import_from_win import from_win
from import_from_lattice import from_lattice


if __name__ == "__main__":
    import sys

    inventory = sys.argv[1]
    #inventory = "/home/erick/Desktop/omero_autoimport/inventory.txt"

    f = open(inventory, "r")
    lines = f.readlines()
    print(lines)
    for line in lines:
        content = line.split(", ")
        IP = content[0]
        micro = content[3]
        vers = content[4]
        multi = content[5].rstrip("\n")
        print(IP, vers, multi, micro)
        if multi == "Y":
            from_dvs(IP, vers, micro)
        else:
            if (micro == "LLSM"):
                from_lattice(IP, vers, True, micro)
            else:
                from_win(IP, vers, False, micro)
