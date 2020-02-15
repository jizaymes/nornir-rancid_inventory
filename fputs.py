#!/usr/bin/env python

def fputs(filename,content):
    hwnd = open(filename,"w+")
    hwnd.write(content)
    hwnd.close()
