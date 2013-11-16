"""
Package File Search
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>

Search Command:
Launch get_package_files_menu, and select what kind of search to do.
If only one pattern is supplied, menu will be skipped and the first
pattern will searched.  By default, this command searches for the
current accessible file, so unpacked plugins in the Packages folder,
would override the default or installed packages.  Use "find_all" option
to list all matches, even duplicates.

Input Search Command:
Enter in search pattern and hit enter.  If a regex pattern is required,
surround in back ticks "`".  By default, this command searches for the
current accessible file, so unpacked plugins in the Packages folder,
would override the default or installed packages.  Use "find_all" option
to list all matches, even duplicates.

Color Scheme Search command:
This is a special search command that previews the color sheme, on menu
option highlight, and when selected, sets the color scheme.


Example Commands:
    //////////////////////////////////
    // Package File Search Commands
    //////////////////////////////////
    {
        "caption": "Package File Search: Menu",
        "command": "get_package_files_menu",
        "args": {
            "pattern_list": [
                {"caption": "Settings Files",        "search": {"pattern": "*.sublime-settings", "regex": false}},
                {"caption": "Keymap Files",          "search": {"pattern": "*.sublime-keymap",   "regex": false}},
                {"caption": "Command Files",         "search": {"pattern": "*.sublime-commands", "regex": false}},
                {"caption": "Readme Files",          "search": {"pattern": "*readme*",           "regex": false}},
                {"caption": "Language Syntax Files", "search": {"pattern": "*tmLanguage",        "regex": false}},
                {"caption": "Snippet Files",         "search": {"pattern": "*.sublime-snippet",  "regex": false}},
                {"caption": "Preference Files",      "search": {"pattern": "*.tmPreferences",    "regex": false}},
                {"caption": "Color Scheme Files",    "search": {"pattern": "*.tmTheme",          "regex": false}},
                {"caption": "Theme Files",           "search": {"pattern": "*.sublime-theme",    "regex": false}},
                {"caption": "Python Source Files",   "search": {"pattern": "*.py",               "regex": false}},
                {"caption": "Sublime Menues",        "search": {"pattern": "*.sublime-menu",     "regex": false}}
            ]
        }
    },
    {
        "caption": "Package false Search: Menu (find false)",
        "command": "get_package_files_menu",
        "args": {
            "pattern_list": [
                {"caption": "Settings Files",        "search": {"pattern": "*.sublime-settings", "regex": false}},
                {"caption": "Keymap Files",          "search": {"pattern": "*.sublime-keymap",   "regex": false}},
                {"caption": "Command Files",         "search": {"pattern": "*.sublime-commands", "regex": false}},
                {"caption": "Readme Files",          "search": {"pattern": "*readme*",           "regex": false}},
                {"caption": "Language Syntax Files", "search": {"pattern": "*tmLanguage",        "regex": false}},
                {"caption": "Snippet Files",         "search": {"pattern": "*.sublime-snippet",  "regex": false}},
                {"caption": "Preference Files",      "search": {"pattern": "*.tmPreferences",    "regex": false}},
                {"caption": "Color Scheme Files",    "search": {"pattern": "*.tmTheme",          "regex": false}},
                {"caption": "Theme Files",           "search": {"pattern": "*.sublime-theme",    "regex": false}},
                {"caption": "Python Source Files",   "search": {"pattern": "*.py",               "regex": false}},
                {"caption": "Sublime Menues",        "search": {"pattern": "*.sublime-menu",     "regex": false}}
            ],
            "find_all": true
        }
    },
    {
        "caption": "Package false Search: Input Search Pattern",
        "command": "get_package_files_input"
    },
    {
        "caption": "Package File Search: Input Search Pattern (find all)",
        "command": "get_package_files_input",
        "args": {"find_all": true}
    },
    {
        "caption": "Package File Search: Set Color Scheme File",
        "command": "get_package_scheme_file"
    },
"""

import sublime
import sublime_plugin
from os.path import join, basename, exists, isdir, dirname
from os import listdir
import re
import zipfile
import tempfile
import shutil
from .lib.package_search import PackageSearch, sublime_package_paths
from .lib import package_search as ps


def get_encoding(view):
    mapping = [
        ("with BOM", ""),
        ("Windows", "cp"),
        ("-", "_"),
        (" ", "")
    ]
    encoding = view.encoding()
    orig = encoding
    print(orig)
    m = re.match(r'.+\((.*)\)', encoding)
    if m is not None:
        encoding = m.group(1)

    for item in mapping:
        encoding = encoding.replace(item[0], item[1])

    return ("utf_8", "UTF-8") if encoding in ["Undefined", "Hexidecimal"] else (encoding, orig)


class WriteArchivedPackageContentCommand(sublime_plugin.TextCommand):
    bfr = None
    def run(self, edit):
        cls = WriteArchivedPackageContentCommand
        if cls.bfr is not None:
            self.view.set_read_only(False)
            self.view.set_scratch(True)
            self.view.replace(edit, sublime.Region(0, self.view.size()), cls.bfr)
            sels = self.view.sel()
            sels.clear()
            sels.add(0)
            cls.bfr = None
            self.view.set_read_only(True)


class WalkPackageFilesCommand(sublime_plugin.WindowCommand):
    def folder_select(self, value, folder_items, cwd, package_folder):
        if value > -1:
            item = folder_items[value]
            sublime.set_timeout(lambda: self.nav_folder(cwd, item, package_folder), 100)

    def nav_folder(self, cwd, child, package_folder):
        target = cwd
        if child is not None:
            child = child[:-1] if child.endswith("/") else child
            if child == ".." and dirname(cwd) == package_folder:
                sublime.set_timeout(self.show_packages, 100)
                return
            elif child == "..":
                target = dirname(target)
            else:
                target = join(target, child)
        if isdir(target):
            folders = []
            files = []
            for item in listdir(target):
                if item in [".svn", ".hg", ".git"]:
                    continue
                if isdir(join(target, item)):
                    folders.append(item + "/")
                else:
                    files.append(item)
            folders.sort()
            files.sort()
            folder_items = [".."] + folders + files
            self.window.show_quick_panel(
                folder_items,
                lambda x: self.folder_select(x, folder_items, target, package_folder)
            )
        else:
            self.window.open_file(target)

    def nav_zip(self, cwd, child, package_folder):
        pass

    def open_pkg(self, value):
        if value > -1:
            location = self.packages[value][1]
            if isdir(location):
                sublime.set_timeout(lambda: self.nav_folder(location, None, dirname(location)), 100)
            else:
                sublime.set_timeout(lambda: self.nav_zip(location, None, dirname(location)), 100)

    def run(self):
        self.packages = []
        for location in ps.get_packages():
            for pkg in location:
                self.packages.append((ps.packagename(pkg), pkg))
        self.packages.sort()
        self.show_packages()

    def show_packages(self):
        if len(self.packages):
            self.window.show_quick_panel(
                [pkg[0] for pkg in self.packages],
                self.open_pkg
            )


class GetPackageFilesInputCommand(sublime_plugin.WindowCommand):
    def find_pattern(self, pattern, find_all=False):
        regex = False
        if pattern != "":
            m = re.match(r"^[ \t]*`(.*)`[ \t]*$", pattern)
            if m != None:
                regex = True
                pattern = m.group(1)
            self.window.run_command(
                "get_package_files",
                {
                    "pattern": pattern,
                    "regex": regex,
                    "find_all": find_all
                }
            )

    def run(self, find_all=False):
        self.window.show_input_panel(
            "File Pattern: ",
            "",
            lambda x: self.find_pattern(x, find_all=find_all),
            None,
            None
        )


class GetPackageFilesMenuCommand(sublime_plugin.WindowCommand):
    def find_files(self, value, patterns, find_all):
        if value > -1:
            pat = patterns[value]
            sublime.set_timeout(
                lambda: self.window.run_command(
                    "get_package_files",
                    {
                        "pattern": pat["pattern"],
                        "regex": pat.get("regex", False),
                        "find_all": find_all
                    }
                ),
                100
            )

    def run(self, pattern_list=[], find_all=False):
        patterns = []
        types = []
        for item in pattern_list:
            patterns.append(item["search"])
            types.append(item["caption"])
        if len(types) == 1:
            self.find_files(0, patterns, find_all)
        elif len(types):
            self.window.show_quick_panel(
                types,
                lambda x: self.find_files(x, patterns=patterns, find_all=find_all)
            )


class _PackageSearchCommand(sublime_plugin.WindowCommand, PackageSearch):
    def run(self, **kwargs):
        self.search(**kwargs)


class GetPackageFilesCommand(_PackageSearchCommand):
    def open_zip_file(self, fn):
        file_name = None
        zip_package = None
        zip_file = None
        for zp in sublime_package_paths():
            items = fn.replace('\\', '/').split('/')
            zip_package = items.pop(0)
            zip_file = '/'.join(items)
            if exists(join(zp, zip_package)):
                zip_package = join(zp, zip_package)
                file_name = join(zp, fn)
                break

        if file_name is not None:
            with zipfile.ZipFile(zip_package, 'r') as z:
                text = z.read(z.getinfo(zip_file))

                # Unpack the file in a temporary location
                d = tempfile.mkdtemp(prefix="pkgfs")
                with open(join(d, basename(file_name)), "wb") as f:
                    f.write(text)

                # Open and then close the file in a view in order
                # to let sublime guess encoding and syntax
                view = self.window.open_file(f.name)
                encoding, st_encoding = get_encoding(view)
                self.window.focus_view(view)
                self.window.run_command("close_file")
                syntax = view.settings().get('syntax')
                shutil.rmtree(d)

                # When a file is opened from disk, you can't rename the
                # the path location.  If you try and use new_file,
                # you can give it a nice file path name, but the tab
                # will be huge.  If you use open_file, with a bogus path,
                # the view will be created with the desired filepath, and
                # it will properly display the basename as the tab name,
                # it will just report an issue reading the file in the console.
                # Reopen a new view and configure it with the
                # syntax and name and give the view a friendly name
                # opposed to an ugly temp directory
                view = self.window.open_file(file_name)
                view.set_syntax_file(syntax)
                view.set_encoding(st_encoding)
                try:
                    WriteArchivedPackageContentCommand.bfr = text.decode(encoding).replace('\r', '')
                except:
                    view.set_encoding("UTF-8")
                    WriteArchivedPackageContentCommand.bfr = text.decode("utf-8").replace('\r', '')
                sublime.set_timeout(lambda: view.run_command("write_archived_package_content"), 0)

    def process_file(self, value, settings):
        if value > -1:
            if self.find_all:
                if value >= self.zipped_idx:
                    self.open_zip_file(settings[value][0])
                else:
                    self.window.open_file(join(self.packages, settings[value][0]))
            else:
                self.window.run_command("open_file", {"file": settings[value].replace("Packages", "${packages}", 1)})


class GetPackageSchemeFileCommand(_PackageSearchCommand):
    def on_select(self, value, settings):
        if value != -1:
            sublime.load_settings("Preferences.sublime-settings").set("color_scheme", settings[value])

    def process_file(self, value, settings):
        if value != -1:
            sublime.load_settings("Preferences.sublime-settings").set("color_scheme", settings[value])
        else:
            if self.current_color_scheme is not None:
                sublime.load_settings("Preferences.sublime-settings").set("color_scheme", self.current_color_scheme)

    def pre_process(self, **kwargs):
        self.current_color_scheme = sublime.load_settings("Preferences.sublime-settings").get("color_scheme")
        return {"pattern": "*.tmTheme"}
