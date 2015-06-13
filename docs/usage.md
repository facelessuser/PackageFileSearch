# User Guide {: .doctitle}
Configuration and usage of PackageFileSearch.

---

## Overview
In order to use Package File Search, you can use one of the five commands:

- Package File Search: Navigator
- Package File Search: Extract
- Package File Search: Search Menu
- Package File Search: Find Panel
- Package File Search: Set Color Scheme File

## Package File Search: Navigator
This is a command that allows you to navigate all the plugins.  It allows you to navigate their file system even if they are archived in a sublime-package zip.  If plugins have some parts in a zip, and some parts unpacked overriding parts in the zip, PackageFileSearch will show a composite of the two with the override file taking precedence.  Unarchived files will open in an editable view.  Archived files will open in a read only view; you cannot directly modify the zipped files.

## Package File Search: Extract
The extract command allows you to unpack an archived plugin into the `Packages` folder if it has not already been done.

## Package File Search: Search Menu
With this command, a menu of pre-defined searches will be displayed.  When one is selected, all of the packages will be searched based on the selected pre-defined search pattern.  This will search only the current active plugin files. If you toggle `Find All` mode via the `Package File Search: Toggle Find All Mode` command, it will search and find override files and the original file and even disabled plugins.  Duplicate results will be distinguished by their install location: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the command will be shown in the command palette as `Package File Search: Search Menu (Find All)`.

You can add to the pre-defined list or change it completely in the `package_file_search.sublime-settings` file.  The setting name is `pattern_list` and it has 3 configurable parameters:

| Parameter | Description |
|-----------|-------------|
| caption | The desired name to show up in the menu. |
| search | The search settings to be used (`pattern` and `regex`). |
| pattern | The wild card or regex pattern to be used. |
| regex | Whether the pattern is a regex pattern or not. |

**Examples**:

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

## Package File Search: Find Panel
The Find Panel command allows for an on demand custom search pattern that can be given to search all active packages.  The pattern is entered into a Sublime input panel.  To search with traditional wild cards, just enter your pattern into the input field.  To use regex, surround the regex in back tics.  This will search only the current active plugin files, unless you toggle `Find All` mode via the `Package File Search: Toggle Find All Mode` command.  Then the command will search all plugin files regardless of whether they are the active plugin or being overridden.  This may give duplicate results, but they will be distinguished by their install location: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the command will be shown in the command palette as `Package File Search: Find Panel (Find All)`.

## Package File Search: Set Color Scheme File
This a command to allow you to look at all color scheme files in active package files and to set it as the current color scheme file.  It will give you a live preview of the color scheme before you select it.  This will only show color schemes that are currently active (not being overridden).

## Package File Search: Toggle Find All Mode
The `Package File Search: Search Menu` and  `Package File Search: Find Panel` command by default search only the active plugin files (not the overridden plugin files).  But toggling `Find All` mode to `True` via this command will search all plugin files regardless of whether they are the active one or not.  This may give duplicate results, but they will be distinguished by their install location: `Default`, `Installed Packages`, and `Packages`.  When `Find All` mode is active, the commands will be shown in the command palette as `Package File Search: Search Menu (Find All)` and `Package File Search: Find Panel (Find All)` respectively.

If you desire `Find All` mode to be `True` by default, you can set the desired behavior in the `package_file_search.sublime-settings` file.

```javascript
    // "find all" means to look in every package regardless of whether
    // it is being overridden.  This means you will see duplicate files if
    // you have two instances of a plugin.
    "find_all_by_default": false
```
