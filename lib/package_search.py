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

__all__ = [
    "sublime_package_paths",
    "scan_for_packages",
    "packagename",
    "get_packages",
    "PackageSearch"
]


def sublime_package_paths(full_path=False):
    """
    Get all the locations where plugins live
    """
    return [sublime.installed_packages_path(), join(dirname(sublime.executable_path()), "Packages"), sublime.packages_path()]


def scan_for_packages(file_path, resolve_override=True):
    """
    Look for zipped and unzipped plugins.
    """
    zips = [join(file_path, item) for item in listdir(file_path) if fnmatch(item, "*.sublime-package")]
    dirs = [join(file_path, item) for item in listdir(file_path) if isdir(join(file_path, item))]

    # Do zips take precedence or do folders? Currently I am having folders take precedence.
    if resolve_override:
        resolve_overrides(zips, dirs)
    return zips + dirs


def packagename(pth, normalize=True):
    """
    Get the package name from the path
    """
    if isdir(pth):
        name = basename(pth)
    else:
        name = splitext(basename(pth))[0]
    return name.lower() if sublime.platform() == "windows" and normalize else name


def resolve_overrides(package_list, override_list):
    """
    Remove packages from the list that are being overridden
    """
    override_names = [packagename(x) for x in override_list[:]]
    count = 0
    offset = 0
    for p in package_list[:]:
        pkg_name = packagename(p)
        for o in override_names:
            if o == pkg_name:
                del package_list[count - offset]
                offset += 1
                break
        count += 1


def resolve_pkgs(defaults, installed, user):
    """
    Resolve which packages to return. Account for package override.
    """
    resolve_overrides(defaults, installed)
    resolve_overrides(defaults, user)
    resolve_overrides(installed, user)


def get_packages(resolve_override=True):
    """
    Get all packages.  Optionally disable resolving override packages.
    """
    installed_pth, default_pth, user_pth= sublime_package_paths()

    installed_pkgs = scan_for_packages(installed_pth, resolve_overrides)
    default_pkgs = scan_for_packages(default_pth, resolve_overrides)
    user_pkgs = scan_for_packages(user_pth, resolve_overrides)

    if resolve_override:
        resolve_pkgs(default_pkgs, installed_pkgs, user_pkgs)

    return default_pkgs, installed_pkgs, user_pkgs


class PackageSearch(object):
    def pre_process(self, **kwargs):
        return kwargs

    def on_select(self, value, settings):
        pass

    def process_file(self, value, settings):
        pass

    ################
    # Qualify Files
    ################
    def find_files(self, files, file_path, pattern, settings, regex):
        """
        Find the file that matches the pattern
        """
        for f in files:
            if regex:
                if re.match(pattern, f[0], re.IGNORECASE) != None:
                    settings.append([f[0].replace(file_path, "").lstrip("\\").lstrip("/"), f[1]])
            else:
                if fnmatch(f[0], pattern):
                    settings.append([f[0].replace(file_path, "").lstrip("\\").lstrip("/"), f[1]])

    ################
    # Zipped
    ################
    def walk_zip(self, settings, plugin, pattern, regex):
        """
        Walk the archived files within the plugin
        """
        with zipfile.ZipFile(plugin[0], 'r') as z:
            zipped = [(join(basename(plugin[0]), normpath(fn)), plugin[1]) for fn in sorted(z.namelist())]
            self.find_files(zipped, "", pattern, settings, regex)

    def get_zip_packages(self, settings, file_path, package_type, pattern, regex=False):
        """
        Get all the archived plugins in the plugin folder
        """
        plugins = [(join(file_path, item), package_type) for item in listdir(file_path) if fnmatch(item, "*.sublime-package")]
        for plugin in plugins:
            self.walk_zip(settings, plugin, pattern.strip(), regex)

    def search_zipped_files(self, settings, pattern, regex):
        """
        Search the plugin folders for archived plugins
        """
        st_packages = sublime_package_paths()
        self.get_zip_packages(settings, st_packages[2], "Packages", pattern, regex)
        self.get_zip_packages(settings, st_packages[0], "Installed", pattern, regex)
        self.get_zip_packages(settings, st_packages[1], "Default", pattern, regex)

    ################
    # Unzipped
    ################
    def walk(self, settings, file_path, plugin, package_type, pattern, regex=False):
        """
        Walk the files within the plugin
        """
        for base, dirs, files in walk(plugin):
            files = [(join(base, f), package_type) for f in files]
            self.find_files(files, file_path, pattern, settings, regex)

    def get_unzipped_packages(self, settings, file_path, package_type, pattern, regex=False):
        """
        Get all of the plugins in the plugin folder
        """
        plugins = [join(file_path, item) for item in listdir(file_path) if isdir(join(file_path, item))]
        for plugin in plugins:
            self.walk(settings, file_path, plugin, package_type, pattern.strip(), regex)

    def search_unzipped_files(self, settings, pattern, regex):
        """
        Search the plugin folders for unzipped packages
        """
        st_packages = sublime_package_paths()
        self.get_unzipped_packages(settings, st_packages[2], "Packages", pattern, regex)
        self.get_unzipped_packages(settings, st_packages[0], "Installed", pattern, regex)
        self.get_unzipped_packages(settings, st_packages[1], "Default", pattern, regex)

    ################
    # Search All
    ################
    def find_raw(self, pattern, regex=False):
        """
        Search all packages regardless of whether it is being overridden
        """
        settings = []
        self.search_unzipped_files(settings, pattern, regex)
        self.zipped_idx = len(settings)
        self.search_zipped_files(settings, pattern, regex)

        self.window.show_quick_panel(
            settings,
            lambda x: self.process_file(x, settings=settings)
        )

    ################
    # Search Override
    ################
    def find(self, pattern, regex):
        """
        Search just the active packages.  Not the ones that have been overridden
        """
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
        """
        Search packages
        """
        kwargs = self.pre_process(**kwargs)
        pattern = kwargs.get("pattern", None)
        regex = kwargs.get("regex", False)
        self.find_all = kwargs.get("find_all", False)

        if not self.find_all:
            self.find(pattern, regex)
        else:
            self.find_raw(pattern, regex)
