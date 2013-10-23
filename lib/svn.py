"""
svn

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import xml.etree.ElementTree as ET
from os import environ
import re
import subprocess
import sys
from os.path import exists, isfile

NO_LOCK = 0
LOCAL_LOCK = 1
REMOTE_LOCK = 2
ORPHAN_LOCK = 3

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

_svn_path = "svn.exe" if _PLATFORM == "windows" else "svn"


def svnopen(args):
    """
    Call SVN with arguments
    """

    returncode = None
    output = None
    cmd = [_svn_path, "--non-interactive"] + args

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


def info(target):
    """
    Get general SVN info
    """

    assert (target.startswith("http://") or target.startswith("https://")) or exists(target), "%s does not exist!" % target
    output = svnopen(['info', "--xml", target])
    return ET.fromstring(output)


def searchinfo(xml, *args):
    """
    Search the info (acquired via the info method) for the keys given.
    Return the related info for each key in a dictionary.
    """

    entry = xml.find("info").find("entry")

    if len(args) == 0:
        return {}

    keys = {}
    for a in args:
        try:
            if a == "url":
                keys[a] = entry.find(a).text
            elif a in ["root", "uuid"]:
                repo = entry.find("repository")
                keys[a] = repo.find(a).text
            elif a in ["revision", "author", "date"]:
                com = entry.find("commit")
                if a == "revision":
                    keys[a] = com.attrib["revision"]
                else:
                    keys[a] = com.find(a).text
            elif a in ["token", "owner", "created", "expires"]:
                lk = entry.find("lock")
                keys[a] = lk.find(a).text
        except:
            keys[a] = None
    return keys


def geturl(pth):
    """
    Get SVN url from file
    """

    output = info(pth)
    search_targets = ["url"]
    keys = searchinfo(output, *search_targets)
    return keys.get(search_targets[0])


def getrevision(pth):
    """
    Get SVN revision
    """

    output = info(pth)
    search_targets = ["revision"]
    keys = searchinfo(output, *search_targets)
    return keys.get(search_targets[0])


def diff_current(target):
    """
    Get SVN diff of last version
    """

    assert exists(target), "%s does not exist!" % target
    assert isfile(target), "%s is not a file!" % target
    return svnopen(['diff', target])


def diff_last(target):
    """
    Get SVN diff of last version
    """

    assert exists(target), "%s does not exist!" % target
    assert isfile(target), "%s is not a file!" % target
    return svnopen(['diff', '-rPREV', target])


def commit(pth, msg=""):
    """
    Commit changes
    """

    assert exists(pth), "%s does not exist!" % pth
    svnopen(["commit", pth, "-m", msg])


def checklock(pth):
    """
    Check if file is locked
    """

    lock_msg = ""
    lock_type = NO_LOCK
    lock_token = None
    last_token = None

    url = geturl(pth)

    for obj in [pth, url]:
        output = info(pth)
        search_targets = ["owner", "created", "token"]
        keys = searchinfo(output, *search_targets)
        owner = keys.get(search_targets[0])
        when = keys.get(search_targets[1])
        lock_token = keys.get(search_targets[2])

        if owner is not None:
            msg = "SVN (checklock): %s was locked by '%s' at %s" % (pth, owner, when)
            if obj == pth:
                lock_type = ORPHAN_LOCK
                last_token = lock_token
                lock_token = None
                lock_msg = msg + " : BAD LOCK"
            elif obj == url and last_token is not None and last_token == lock_token:
                lock_type = LOCAL_LOCK
                lock_msg = msg + " : LOCAL LOCK"
            elif obj == url and last_token is None:
                lock_type = REMOTE_LOCK
                lock_msg = msg + " : REMOTE LOCK"

    return lock_msg, lock_type


def lock(pth):
    """
    Lock file
    """

    assert exists(pth), "%s does not exist!" % pth
    svnopen(['lock', pth])


def breaklock(pth, force=False):
    """
    Breack file lock
    """

    assert exists(pth), "%s does not exist!" % pth

    args = ['unlock']
    if force:
        args += ["--force", pth]
    else:
        args.append(pth)

    svnopen(args)


def checkout(url, pth):
    """
    Checkout SVN url
    """

    svnopen(['checkout', url, pth])
    assert exists(pth)


def update(pth):
    """
    Update SVN directory
    """

    assert exists(pth), "%s does not exist!" % pth
    svnopen(['update', pth])


def export(url, name):
    """
    Export file
    """

    svnopen(['export', url, name])
    assert exists(name), "%s appears to not have been exported!" % name


def add(pth):
    """
    Add a file
    """

    assert exists(pth), "%s does not exist!" % pth
    svnopen(['add', pth])


def cleanup(pth):
    """
    Clean up a folder
    """

    assert exists(pth), "%s does not exist!" % pth
    svnopen(['cleanup', pth])


def status(pth, ignore_externals=False, ignore_unversioned=False, depth="infinity"):
    """
    Get the SVN status for the folder
    """

    assert exists(pth), "%s does not exist!" % pth

    attributes = {
        "added": [],
        "conflicted": [],
        "deleted": [],
        "external": [],
        "ignored": [],
        "incomplete": [],
        "merged": [],
        "missing": [],
        "modified": [],
        "none": [],
        "normal": [],
        "obstructed": [],
        "replaced": [],
        "unversioned": []
    }

    args = ['status', '--xml', '--depth', depth]
    if ignore_externals:
        args.append('--ignore-externals')

    args.append(pth)

    output = svnopen(args)
    root = ET.fromstring(output)

    target = root.find("target")
    entries = target.findall("entry")
    if len(entries):
        for entry in entries:
            s = entry.find("wc-status")
            item = s.attrib["item"]
            if ignore_unversioned and item == "unversioned":
                continue
            if ignore_externals and item == "external":
                continue
            if item in attributes:
                attributes[item].append(entry.attrib["path"])
    elif not ignore_unversioned and re.search(r"svn: warning: '.*' is not a working copy", target.text.lstrip()) is not None:
        attributes["unversioned"].append(target.attrib["path"])

    return attributes


def is_versioned(target):
    """
    Check if file/folder is versioned
    """

    assert exists(target), "%s does not exist!" % target

    versioned = False
    entries = status(target, depth="empty")
    if len(entries["unversioned"]) == 0:
        versioned = True

    return versioned


def version():
    """
    Get SVN app version
    """

    version = None
    output = svnopen(['--version'])
    m = re.search(br" version (\d+\.\d+\.\d+) ", output)
    if m is not None:
        version = m.group(1).decode('utf-8')
    return version


def set_svn_path(pth):
    """
    Set SVN path
    """

    global _svn_path
    _svn_path = pth
