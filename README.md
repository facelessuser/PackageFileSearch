# PackageFileSearch

PackageFileSearch is plugin designed to allow a user to search all default, installed, and unpacked plugins for specific files.

# Usage
In order to use Package File Search, you can use one of the five commands:``

- Package File Search: Navigator
- Package File Search: Extract
- Package File Search: Search Menu
- Package File Search: Find Panel
- Package File Search: Set Color Scheme File

## Package File Search: Navigator
This is a command that allows you to navigate all the plugins.  It allows you to navigate their file system; even if they are archived in a sublime-package zip.  It only displays the plugins that would be loaded by sublime.  For example, if Package Control installed a plugin in the `Installed Packages` folder, then you downloaded that same plugin into the `Packages` folder, the `Packages` version would override the `Installed Packages` version, and the `Packages` version is what would show up in the navigator.  Unarchived files will open in an editable view.  Archived files will open in a read only view; you cannot directly modify the zipped files.

## Package File Search: Extract
The extract command allows you to unpack an archived plugin into the `Packages` folder if it has not already been done.

## Package File Search: Search Menu
With this command, a menu of pre-defined searches will be displayed.  When one is selected, all of the packages will be searched based on the selected pre-defined search pattern.  This will search only the current active plugns (not overridden plugins), unless you toggle `Find All` mode via the `Package File Search: Toggle Find All Mode` command.  Then the command will search all plugins regardless of whether they are the active plugin or not.  This may give duplicate results, but they will be distinguished by their install locatin: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the command will be shown in the command palette as `Package File Search: Search Menu (Find All)`.

You can add to the pre-defined list, or change it completely in the `package_file_search.sublime-settings` file.

```javascript
    // Default pre-set patterns
    "pattern_list": [
        {"caption": "Color Schemes",         "search": {"pattern": "*.tmTheme",          "regex": false}},
        {"caption": "Commands",              "search": {"pattern": "*.sublime-commands", "regex": false}},
        {"caption": "Keymaps",               "search": {"pattern": "*.sublime-keymap",   "regex": false}},
        {"caption": "Language Syntaxes",     "search": {"pattern": "*tmLanguage",        "regex": false}},
        {"caption": "Macros",                "search": {"pattern": "*.sublime-macro",    "regex": false}},
        {"caption": "Menus",                 "search": {"pattern": "*.sublime-menu",     "regex": false}},
        {"caption": "Preferences",           "search": {"pattern": "*.tmPreferences",    "regex": false}},
        {"caption": "Python Source Files",   "search": {"pattern": "*.py",               "regex": false}},
        {"caption": "Readme Files",          "search": {"pattern": "*readme*",           "regex": false}},
        {"caption": "Settings",              "search": {"pattern": "*.sublime-settings", "regex": false}},
        {"caption": "Snippets",              "search": {"pattern": "*.sublime-snippet",  "regex": false}},
        {"caption": "Themes",                "search": {"pattern": "*.sublime-theme",    "regex": false}}
    ],
```

- caption: the desired name to show up in the menut
- search: the search settings to be used (`pattern` and `regex`)
- pattern: the wild card or regex pattern to be used
- regex: whether the pattern is a regex pattern or not

## Package File Search: Find Panel
The Find Panel command allows a custom search pattern that can be given to search all active packages.  To searh with traditional wild cards, just enter your pattern into the input field.  To use regex, surround the regex in back tics.  This will search only the current active plugns (not overridden plugins), unless you toggle `Find All` mode via the `Package File Search: Toggle Find All Mode` command.  Then the command will search all plugins regardless of whether they are the active plugin or not.  This may give duplicate results, but they will be distinguished by their install locatin: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the command will be shown in the command palette as `Package File Search: Find Panel (Find All)`

## Package File Search: Set Color Scheme File
This a command to allow you to look at all color scheme files in active packages and to set it as the current color scheme file.  It will give you a live preview of the color scheme before you select it.  This will only show color schemes from current active plugns (not overridden plugins).

## Package File Search: Toggle Find All Mode
The `Package File Search: Search Menu` and  `Package File Search: Find Panel` command by default search only the active plugins (not the overridden plugins).  But toggling `Find All` mode to `True` via this command will search all plugins regardless of whether they are the active plugin or not.  This may give duplicate results, but they will be distinguished by their install locatin: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the commands will be shown in the command palette as `Package File Search: Search Menu (Find All)` and `Package File Search: Find Panel (Find All)` respectively.

If you desire `Find All` mode to be `True` by default, you can set the desired behavior in the `package_file_search.sublime-settings` file.

```javascript
    // "find all" means to look in every package regardless of whether
    // it is being overridden.  This means you will see duplicate files if
    // you have two instances of a plugin.
    "find_all_by_default": false
```

# License

PackageFileSearch is released under the MIT license.

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
