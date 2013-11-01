# PackageFileSearch

PackageFileSearch is plugin designed to allow a user to search all default, installed, and unpacked plugins for specific files.

# Usage
In order to use Package File Search, you just need to setup the commands you would like to have:

## Preset Package Search Menu
You can define a command with all of your commonly searched patterns, or you can define multiple commands each calling a separate pattern.  If the command only has one defined pattern, no menu will be shown, and the search will immediately be executed.  If there are multiple patterns, a menu will be displayed asking the user which pattern they would like to search with.  You simply give it a pattern list containing your entries.  Each entry must define a caption and the search settings: the pattern to search with and whether the pattern is a regex pattern or not.

```javascript
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
```

By default, the search will show you the currently used version of a package file.  If, for instance, you have a package overriding a default package, the default version will not be shown.  If you would like to display all versions, use the `find_all` argument.

```javascript
    {
        "caption": "Package false Search: Menu (find false)",
        "command": "get_package_files_menu",
        "args": {
            "pattern_list": [
                {"caption": "Settings Files",        "search": {"pattern": "*.sublime-settings", "regex": false}}
            ],
            "find_all": true
        }
    },
```

## Searching a Pattern on the Fly
Package File Search also allows a user to search patterns on the fly.  For this you can define a command that takes an input.  If you would like to use regex, surround your pattern with back tics *`*.

By default, the search will show you the currently used version of a package file.  If, for instance, you have a package overriding a default package, the default version will not be shown.  If you would like to display all versions, use the `find_all` argument.

```javascript
    {
        "caption": "Package false Search: Input Search Pattern",
        "command": "get_package_files_input"
    },
    {
        "caption": "Package File Search: Input Search Pattern (find all)",
        "command": "get_package_files_input",
        "args": {"find_all": true}
    },
```

## Special Color Scheme Search
This is a special command that allows you to list all color schemes.  As you highlight them in the drop down menu the color scheme will be previewed on the currently open view.  Selected the scheme will set it in your preferences; canceling will return you to your current scheme.

```javascript
    {
        "caption": "Package File Search: Set Color Scheme File",
        "command": "get_package_scheme_file"
    },
```

# License

PackageFileSearch is released under the MIT license.

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
