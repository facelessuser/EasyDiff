"""
hg

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import xml.etree.ElementTree as ET
from os import environ
import re
import subprocess
import sys
from os.path import exists, isfile, dirname, join

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

_hg_path = "hg.exe" if _PLATFORM == "windows" else "hg"


def hgopen(args):
    """
    Call Git with arguments
    """

    returncode = None
    output = None

    cmd = [_hg_path] + args

    env = environ.copy()
    env['LC_ALL'] = 'en_US'

    if _PLATFORM == "windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            cmd,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False,
            env=env
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=False,
            env=env
        )
    output = process.communicate()
    returncode = process.returncode

    assert returncode == 0, "Runtime Error: %s" % output[0].rstrip()

    return output[0]


def cat(target, rev=None):
    """
    Show file at revision
    """

    assert exists(target), "%s does not exist!" % target
    args = ["cat", target]
    if rev is not None:
        args += ["-r", str(rev)]
    return hgopen(args)


def getrevision(target, count=1):
    """
    Get revision(s)
    """

    assert exists(target), "%s does not exist!" % target
    results = log(target, count)
    assert results is not None, "Failed to acquire log info!"
    revs = []
    for entry in results.findall('logentry'):
        revs.append(entry.attrib["node"])
    return revs


def diff(target, last=False):
    """
    Diff current file against last revision
    """

    args = None

    assert exists(target), "%s does not exist!" % target
    if last:
        revs = getrevision(target, 2)
        if len(revs) == 2:
            args = ["diff", "-p", "-r", revs[1]]
    else:
        args = ["diff", "-p"]

    return hgopen(args + [target]) if args is not None else b""


def log(target=None, limit=0):
    """
    Get hg log(s)
    """

    assert exists(target), "%s does not exist!" % target

    args = ["log", "--style=xml"]
    if limit != 0:
        args.append("-l")
        args.append(str(limit))
    if target is not None:
        args.append(target)
    output = hgopen(args)

    if output != "":
        results = ET.fromstring(output)
    else:
        results = None

    return results


def is_versioned(target):
    """
    Check if file/folder is versioned
    """

    assert exists(target), "%s does not exist!" % target
    versioned = False
    try:
        results = log(target, 1)
        if results is not None:
            if results.find("logentry") is not None:
                versioned = True
    except:
        pass

    return versioned


def version():
    """
    Get hg app version
    """

    version = None
    output = hgopen(['--version'])
    m = re.search(br"\bversion ([\d\.A-Za-z]+)", output)
    if m is not None:
        version = m.group(1).decode('utf-8')
    return version


def set_hg_path(pth):
    """
    Set hg path
    """

    global _hg_path
    _hg_path = pth
