"""
Hg.

Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import xml.etree.ElementTree as ET
import os
import re
import subprocess
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

_hg_path = "hg.exe" if _PLATFORM == "windows" else "hg"


def which():
    """See if executable exists."""

    location = None
    if os.path.basename(_hg_path) != _hg_path:
        if os.path.isfile(_hg_path):
            location = _hg_path
    else:
        paths = [x for x in os.environ["PATH"].split(os.pathsep) if not x.isspace()]
        for path in paths:
            exe = os.path.join(path, _hg_path)
            if os.path.isfile(exe):
                location = exe
                break
    return location


def hgopen(args, cwd=None):
    """Call Git with arguments."""

    returncode = None
    output = None

    cmd = [_hg_path] + args

    env = os.environ.copy()
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
            cwd=cwd,
            shell=False,
            env=env
        )
    else:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            cwd=cwd,
            shell=False,
            env=env
        )
    output = process.communicate()
    returncode = process.returncode

    assert returncode == 0, "Runtime Error: %s\n%s" % (output[0].rstrip(), str(cmd))

    return output[0]


def cat(target, rev=None):
    """Show file at revision."""

    assert os.path.exists(target), "%s does not exist!" % target
    args = ["cat", target]
    if rev is not None:
        args += ["-r", str(rev)]
    return hgopen(args, os.path.dirname(target))


def revert(target):
    """Revert file."""

    assert os.path.exists(target), "%s does not exist!" % target
    hgopen(["revert", "--no-backup", target], os.path.dirname(target))


def getrevision(target, count=1):
    """Get revision(s)."""

    assert os.path.exists(target), "%s does not exist!" % target
    results = log(target, count)
    assert results is not None, "Failed to acquire log info!"
    revs = []
    for entry in results.findall('logentry'):
        revs.append(entry.attrib["node"])
    return revs


def diff(target, last=False):
    """Diff current file against last revision."""

    args = None

    assert os.path.exists(target), "%s does not exist!" % target
    if last:
        revs = getrevision(target, 2)
        if len(revs) == 2:
            args = ["diff", "-p", "-r", revs[1]]
    else:
        args = ["diff", "-p"]

    return hgopen(args + [target], os.path.dirname(target)) if args is not None else b""


def log(target=None, limit=0):
    """Get hg log."""

    assert os.path.exists(target), "%s does not exist!" % target

    args = ["log", "--style=xml"]
    if limit != 0:
        args.append("-l")
        args.append(str(limit))
    if target is not None:
        args.append(target)
    output = hgopen(args, os.path.dirname(target))

    if output != "":
        results = ET.fromstring(output)
    else:
        results = None

    return results


def is_versioned(target):
    """Check if file/folder is versioned."""

    assert os.path.exists(target), "%s does not exist!" % target
    versioned = False
    try:
        results = log(target, 1)
        if results is not None:
            if results.find("logentry") is not None:
                versioned = True
    except Exception:
        pass

    return versioned


def version():
    """Get hg app version."""

    version = None
    output = hgopen(['--version'])
    m = re.search(br"\bversion ([\d\.A-Za-z]+)", output)
    if m is not None:
        version = m.group(1).decode('utf-8')
    return version


def set_hg_path(pth):
    """Set hg path."""

    global _hg_path
    _hg_path = pth
