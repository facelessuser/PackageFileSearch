"""
Package File Search
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""

import sublime
import sublime_plugin
from os.path import join, basename, exists, isdir, dirname, normpath
from os import listdir, mkdir
import re
import zipfile
import tempfile
import shutil
from .lib.package_search import *


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


class PackageFileSearchNavCommand(sublime_plugin.WindowCommand):
    def folder_select(self, value, folder_items, cwd, package_folder):
        if value > -1:
            item = folder_items[value]
            sublime.set_timeout(lambda: self.nav_folder(cwd, item, package_folder), 100)

    def zip_select(self, value, folder_items, zippkg, cwd, package_folder):
        if value > -1:
            item = folder_items[value]
            sublime.set_timeout(lambda: self.nav_zip(zippkg, cwd, item, package_folder), 100)

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

    def open_zip_file(self, z, zip_file, file_name):
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

    def nav_zip(self, zippkg, cwd, child, package_folder):
        target = "" if cwd is None else cwd
        if child is not None:
            child = child[:-1] if child.endswith('/') else child
            if child == ".." and cwd == "":
                sublime.set_timeout(self.show_packages, 100)
                return
            elif child == "..":
                target = dirname(target)
            else:
                target = join(target, child)
        target.replace("\\", '/')
        folders = []
        files = []
        with zipfile.ZipFile(zippkg, 'r') as z:
            for item in z.infolist():
                if target == item.filename:
                    self.open_zip_file(z, item.filename, join(zippkg, normpath(item.filename)))
                    return
                if target != "" and not item.filename.startswith(target + '/'):
                    continue
                if target != "":
                    parts = item.filename.replace(target + '/', '', 1).split('/')
                else:
                    parts = item.filename.split('/')
                if parts[-1] == '':
                    if parts[0] == "":
                        continue
                    entry = parts[0] + '/'
                    if entry not in folders:
                        folders.append(entry)
                else:
                    if len(parts) > 1:
                        entry = parts[0] + '/'
                        if entry not in folders:
                            folders.append(parts[0] + '/')
                    else:
                        files.append(parts[0])
        folders.sort()
        files.sort()
        folder_items = [".."] + folders + files
        self.window.show_quick_panel(
            folder_items,
            lambda x: self.zip_select(x, folder_items, zippkg, target, package_folder)
        )

    def open_pkg(self, value):
        if value > -1:
            location = self.packages[value][1]
            if isdir(location):
                sublime.set_timeout(lambda: self.nav_folder(location, None, dirname(location)), 100)
            else:
                sublime.set_timeout(lambda: self.nav_zip(location, None, None, dirname(location)), 100)

    def run(self):
        self.packages = []
        for location in get_packages():
            for pkg in location:
                self.packages.append((packagename(pkg), pkg))
        self.packages.sort()
        self.show_packages()

    def show_packages(self):
        if len(self.packages):
            self.window.show_quick_panel(
                [pkg[0] for pkg in self.packages],
                self.open_pkg
            )


class _GetPackageFilesInputCommand(sublime_plugin.WindowCommand):
    find_mode = False

    def find_pattern(self, pattern, find_all=False):
        regex = False
        if pattern != "":
            m = re.match(r"^[ \t]*`(.*)`[ \t]*$", pattern)
            if m != None:
                regex = True
                pattern = m.group(1)
            self.window.run_command(
                "package_file_search",
                {
                    "pattern": pattern,
                    "regex": regex,
                    "find_all": find_all
                }
            )

    def run(self):
        self.window.show_input_panel(
            "File Pattern: ",
            "",
            lambda x: self.find_pattern(x, find_all=self.find_mode),
            None,
            None
        )

class PackageFileSearchInputCommand(_GetPackageFilesInputCommand):
    find_mode = False

    def is_enabled(self):
        return not FIND_ALL_MODE


class PackageFileSearchAllInputCommand(_GetPackageFilesInputCommand):
    find_mode = True

    def is_enabled(self):
        return FIND_ALL_MODE


class _GetPackageFilesMenuCommand(sublime_plugin.WindowCommand):
    find_mode = False

    def find_files(self, value, patterns, find_all):
        if value > -1:
            pat = patterns[value]
            sublime.set_timeout(
                lambda: self.window.run_command(
                    "package_file_search",
                    {
                        "pattern": pat["pattern"],
                        "regex": pat.get("regex", False),
                        "find_all": find_all
                    }
                ),
                100
            )

    def run(self, pattern_list=None):
        patterns = []
        if pattern_list is None:
            pattern_list = sublime.load_settings("package_file_search.sublime-settings").get("pattern_list", [])
        types = []
        for item in pattern_list:
            patterns.append(item["search"])
            types.append(item["caption"])
        if len(types) == 1:
            self.find_files(0, patterns, self.find_mode)
        elif len(types):
            self.window.show_quick_panel(
                types,
                lambda x: self.find_files(x, patterns=patterns, find_all=self.find_mode)
            )


class PackageFileSearchMenuCommand(_GetPackageFilesMenuCommand):
    find_mode = False

    def is_enabled(self):
        return not FIND_ALL_MODE


class PackageFileSearchAllMenuCommand(_GetPackageFilesMenuCommand):
    find_mode = True

    def is_enabled(self):
        return FIND_ALL_MODE


class PackageFileSearchExtractCommand(sublime_plugin.WindowCommand):
    def extract(self, value, packages):
        if value > -1:
            pkg = packages[value]
            name = packagename(pkg)
            dest = join(sublime.packages_path(), name)
            if not exists(dest):
                mkdir(dest)
            with zipfile.ZipFile(pkg) as z:
                z.extractall(dest)

    def run(self):
        defaults, installed, _ = get_packages()
        packages = defaults + installed
        if len(packages):
            self.window.show_quick_panel(
                [packagename(pkg) for pkg in packages],
                lambda x: self.extract(x, packages)
            )


class _PackageSearchCommand(sublime_plugin.WindowCommand, PackageSearch):
    def run(self, **kwargs):
        self.search(**kwargs)


class PackageFileSearchCommand(_PackageSearchCommand):
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


class PackageFileSearchColorSchemeCommand(_PackageSearchCommand):
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


class TogglePackageSearchFindAllModeCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        global FIND_ALL_MODE
        FIND_ALL_MODE = False if FIND_ALL_MODE else True
        sublime.status_message("Package File Search: Find All = %s" % str(FIND_ALL_MODE))


def plugin_loaded():
    global FIND_ALL_MODE
    FIND_ALL_MODE = sublime.load_settings("package_file_search.sublime-settings").get("find_all_by_default", False)
