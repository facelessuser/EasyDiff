"""
git

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

_git_path = "git.exe" if _PLATFORM == "windows" else "git"

# UNSTAGED_DIFF = 0
# STAGED_DIFF = 1
# ALL_DIFF = 2


def is_system_root(target):
    """
    Check if target is the root folder
    """

    root = False
    windows = _PLATFORM == "windows"
    if windows and re.match(r"^[A-Za-z]{1}:\\$", target) is not None:
        root = True
    elif not windows and target == '/':
        root = True

    return root


def get_git_tree(target):
    """
    Recursively get Git tree
    """

    root = is_system_root(target)
    is_file = isfile(target)
    folder = dirname(target) if is_file else target
    if exists(join(folder, ".git")):
        return folder
    else:
        if root:
            return None
        else:
            return get_git_tree(dirname(folder))


def get_git_dir(tree):
    """
    Get Git directory from tree
    """

    return join(tree, ".git")


def gitopen(args, git_tree=None):
    """
    Call Git with arguments
    """

    returncode = None
    output = None

    if git_tree is not None:
        cmd = [_git_path, "--work-tree=%s" % git_tree, "--git-dir=%s" % get_git_dir(git_tree)] + args
    else:
        cmd = [_git_path] + args

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


def show(target, rev):
    """
    Show file at revision
    """

    assert exists(target), "%s does not exist!" % target
    git_tree = get_git_tree(target)
    bfr = None
    target = target.replace(git_tree, "", 1).lstrip("\\" if _PLATFORM == "windows" else "/")

    if _PLATFORM == "windows":
        target = target.replace("\\", "/")
    if git_tree is not None:
        bfr = gitopen(["show", "%s:%s" % (rev, target)], git_tree)
    return bfr


def getrevision(target, count=1):
    """
    Get revision(s)
    """

    assert exists(target), "%s does not exist!" % target
    git_tree = get_git_tree(target)
    revs = None

    if git_tree is not None:
        revs = []
        lg = gitopen(["log", "--no-color", "--pretty=oneline", "-n", str(count), target], git_tree)
        for m in re.finditer(br"([a-f\d]{40}) .*\r?\n", lg):
            revs.append(m.group(1).decode("utf-8"))
    return revs


def checkout(target, rev=None):
    """
    Checkout file
    """

    assert exists(target), "%s does not exist!" % target
    git_tree = get_git_tree(target)

    if git_tree is not None:
        args = ["checkout"]
        if rev is not None:
            args.append(rev)
        args.append(target)

        gitopen(args, git_tree)


def diff(target, last=False):
    """
    Diff current file against last revision
    """

    assert exists(target), "%s does not exist!" % target
    # assert diff_type in [ALL_DIFF, STAGED_DIFF, UNSTAGED_DIFF], "diff_type is bad!"
    git_tree = get_git_tree(target)
    results = b""

    if git_tree is not None:
        args = ["diff", "--no-color"]

        if last:
            revs = getrevision(target, 2)

            if len(revs) == 2:
                args += [revs[1], "--"]
            else:
                args = None
        else:
            args += ["HEAD", "--"]

        # Staged only
        # elif diff_type == STAGED_DIFF:
        #     args.append("--cached")

        if args:
            results = gitopen(args + [target], git_tree)
    return results


def is_versioned(target):
    """
    Check if file/folder is versioned
    """

    assert exists(target), "%s does not exist!" % target
    git_tree = get_git_tree(target)

    versioned = False
    if git_tree is not None:
        output = gitopen(["status", "--ignored", "--porcelain", target], git_tree)
        if not (output.startswith(b"!!") or output.startswith(b"??")):
            versioned = True

    return versioned


def version():
    """
    Get Git app version
    """

    version = None
    output = gitopen(['--version'])
    m = re.search(br" version ([\d\.A-Za-z]+)", output)
    if m is not None:
        version = m.group(1).decode('utf-8')
    return version


def set_git_path(pth):
    """
    Set Git path
    """

    global _git_path
    _git_path = pth
