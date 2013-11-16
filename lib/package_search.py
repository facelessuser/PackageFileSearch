"""
Submlime Text Package File Search
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
"""
import sublime
import re
from os import walk, listdir
from os.path import basename, dirname, isdir, join, normpath, splitext
from fnmatch import fnmatch
import zipfile


def sublime_package_paths(full_path=False):
    return [sublime.installed_packages_path(), join(dirname(sublime.executable_path()), "Packages"), sublime.packages_path()]


def scan_for_packages(file_path):
    zips = [join(file_path, item) for item in listdir(file_path) if fnmatch(item, "*.sublime-package")]
    dirs = [join(file_path, item) for item in listdir(file_path) if isdir(join(file_path, item))]

    copy_dirs = [packagename(d) for d in dirs[:]]
    count = 0
    offset = 0
    for z in zips[:]:
        z_pkg_name = packagename(z)
        for d in copy_dirs:
            if d == z_pkg_name:
                del zips[count - offset]
                offset += 1
                break
        count += 1
    return dirs + zips


def packagename(pth, normalize=True):
    if isdir(pth):
        name = basename(pth)
    else:
        name = splitext(basename(pth))[0]
    return name.lower() if sublime.platform() == "windows" and normalize else name


def resolve_pkgs(defaults, installed, user):
    copy_installed = [packagename(i) for i in installed[:]]

    # resolve defaults/installed
    count = 0
    offset = 0
    for d in defaults[:]:
        d_pkg_name = packagename(d)
        for i in copy_installed:
            if i == d_pkg_name:
                del defaults[count - offset]
                offset += 1
                break
        count += 1

    copy_user = [packagename(u) for u in user[:]]

    # resolve defaults/user
    count = 0
    offset = 0
    for d in defaults[:]:
        d_pkg_name = packagename(d)
        for u in copy_user:
            if u == d_pkg_name:
                del defaults[count - offset]
                offset += 1
                break
        count += 1

    # resolve installed/user
    count = 0
    offset = 0
    for i in installed[:]:
        i_pkg_name = packagename(i)
        for u in copy_user:
            if u == i_pkg_name:
                del installed[count - offset]
                offset += 1
                break
        count += 1


def get_packages(resolve_overrides=True):
    installed_pth, default_pth, user_pth= sublime_package_paths()

    installed_pkgs = scan_for_packages(installed_pth)
    default_pkgs = scan_for_packages(default_pth)
    user_pkgs = scan_for_packages(user_pth)

    if resolve_overrides:
        resolve_pkgs(default_pkgs, installed_pkgs, user_pkgs)

    return default_pkgs, installed_pkgs, user_pkgs


class PackageSearch(object):
    def pre_process(self, **kwargs):
        return kwargs

    def on_select(self, value, settings):
        pass

    def process_file(self, value, settings):
        pass

    def find_files(self, files, pattern, settings, regex):
        for f in files:
            if regex:
                if re.match(pattern, f[0], re.IGNORECASE) != None:
                    settings.append([f[0].replace(self.packages, "").lstrip("\\").lstrip("/"), f[1]])
            else:
                if fnmatch(f[0], pattern):
                    settings.append([f[0].replace(self.packages, "").lstrip("\\").lstrip("/"), f[1]])

    def walk(self, settings, plugin, pattern, regex=False):
        for base, dirs, files in walk(plugin):
            files = [(join(base, f), "Packages") for f in files]
            self.find_files(files, pattern, settings, regex)

    def get_zip_packages(self, file_path, package_type):
        plugins = [(join(file_path, item), package_type) for item in listdir(file_path) if fnmatch(item, "*.sublime-package")]
        return plugins

    def search_zipped_files(self):
        plugins = []
        st_packages = sublime_package_paths()
        plugins += self.get_zip_packages(st_packages[0], "Installed")
        plugins += self.get_zip_packages(st_packages[1], "Default")
        return plugins

    def walk_zip(self, settings, plugin, pattern, regex):
        with zipfile.ZipFile(plugin[0], 'r') as z:
            zipped = [(join(basename(plugin[0]), normpath(fn)), plugin[1]) for fn in sorted(z.namelist())]
            self.find_files(zipped, pattern, settings, regex)

    def find_raw(self, pattern, regex=False):
        self.packages = normpath(sublime.packages_path())
        settings = []
        plugins = [join(self.packages, item) for item in listdir(self.packages) if isdir(join(self.packages, item))]
        for plugin in plugins:
            self.walk(settings, plugin, pattern.strip(), regex)

        self.zipped_idx = len(settings)

        zipped_plugins = self.search_zipped_files()
        for plugin in zipped_plugins:
            self.walk_zip(settings, plugin, pattern.strip(), regex)

        self.window.show_quick_panel(
            settings,
            lambda x: self.process_file(x, settings=settings)
        )

    def find(self, pattern, regex):
        resources = []
        if not regex:
            resources = sublime.find_resources(pattern)
        else:
            temp = sublime.find_resources("*")
            for t in temp:
                if re.match(pattern, t, re.IGNORECASE) != None:
                    resources.append(t)

        self.window.show_quick_panel(
            resources,
            lambda x: self.process_file(x, settings=resources),
            0,
            0,
            lambda x: self.on_select(x, settings=resources)
        )

    def search(self, **kwargs):
        kwargs = self.pre_process(**kwargs)
        pattern = kwargs.get("pattern", None)
        regex = kwargs.get("regex", False)
        self.find_all = kwargs.get("find_all", False)

        if not self.find_all:
            self.find(pattern, regex)
        else:
            self.find_raw(pattern, regex)
