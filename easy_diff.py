"""
Easy Diff

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import time
import difflib
from os.path import basename
from os import stat as osstat
import tempfile
from EasyDiff.easy_diff_global import load_settings, get_encoding
import subprocess


class EasyDiffView(object):
    def __init__(self, name, content, encoding):
        self.filename = name
        self.content = content
        self.time = time.ctime()
        self.encode = encoding

    def encoding(self):
        return self.encode

    def get_time(self):
        return self.time

    def file_name(self):
        return self.filename

    def substr(self, region):
        return self.content[region.begin():region.end() + 1]

    def size(self):
        return len(self.content)


class EasyDiffInput(object):
    def __init__(self, v1, v2, external=False):
        self.untitled = False
        index = 1
        self.process_view(v1, index, external)
        index = 2
        self.process_view(v2, index, external)

    def process_view(self, view, index, external):
        name = view.file_name()
        if name is None:
            self.set_view_buffer(view, index, self.untitled, external)
        elif isinstance(view, EasyDiffView):
            self.set_special(view, index, external)
        else:
            self.set_view(view, index)

        self.set_buffer(view, index, external)

    def set_buffer(self, view, index, external):
        setattr(
            self, 
            "b%d" % index, 
            view.substr(sublime.Region(0, view.size())).splitlines() if not external else []
        )

    def set_view(self, view, index):
        setattr(self, "f%d" % index, view.file_name())
        setattr(self, "t%d" % index, time.ctime(osstat(view.file_name()).st_mtime))

    def set_special(self, view, index, external):
        setattr(self, "f%d" % index, view.file_name())
        if external:
            setattr(self, "f%d" % index, self.create_temp(view, view.file_name().replace("*", "")))
        setattr(self, "t%d" % index, view.get_time())

    def set_view_buffer(self, view, index, untitled, external):
        setattr(
            self,
            "f%d" % index,
            self.create_temp(v1, "Untitled2" if self.untitled else "Untitled") if external else "Untitled2" if self.untitled else "Untitled"
        )
        setattr(self, "t%d" % index, time.ctime())
        self.untitled = True

    def create_temp(self, v, name):
        with tempfile.NamedTemporaryFile(delete=False, prefix=name, suffix="") as f:
            encoding = get_encoding(v)
            try:
                bfr = v.substr(sublime.Region(0, v.size())).encode(encoding)
            except:
                bfr = v.substr(sublime.Region(0, v.size())).encode("utf-8")
            f.write(bfr)
        return f.name


class EasyDiff(object):
    @classmethod
    def extcompare(cls, inputs, ext_diff):
        subprocess.Popen(
            [
                ext_diff,
                inputs.f1,
                inputs.f2
            ]
        )

    @classmethod
    def compare(cls, inputs):
        diff = difflib.unified_diff(
            inputs.b1, inputs.b2,
            inputs.f1, inputs.f2,
            inputs.t1, inputs.t2,
            lineterm=''
        )
        result = u"\n".join(line for line in diff)

        if result == "":
            sublime.status_message("No Difference")
            return

        use_buffer = bool(load_settings().get("use_buffer", False))

        win = sublime.active_window()
        if use_buffer:
            v = win.new_file()
            v.set_name("EasyDiff: %s -> %s (%s)" % (basename(inputs.f1), basename(inputs.f2), time.ctime()))
            v.set_scratch(True)
            v.assign_syntax('Packages/Diff/Diff.tmLanguage')
            v.run_command('append', {'characters': result})
        else:
            v = win.create_output_panel('easy_diff')
            v.assign_syntax('Packages/Diff/Diff.tmLanguage')
            v.run_command('append', {'characters': result})
            win.run_command("show_panel", {"panel": "output.easy_diff"})
