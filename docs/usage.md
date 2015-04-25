# User Guide {: .doctitle}
Using and configuring Easydiff.
{: .doctitle-info}

---

# Basic Usage
Easy diff is easy to use.  Simply select the `Set Left Side` option in the context menus to set what is to be compared on the left side when in a view.  Then select the what to compare to via `Compare with` menu option (select the right side view first if comparing to a view).

For version control, just select the applicable option when in a view that is versioned controlled.

# General Settings
Easy diff, by default, shows diffs in a separate view, you can display the diff in an output panel if desired using the following setting:

```javascript
    // If enabled, this allows for multiple selections.
    // Each selection is separated with a new line.
    "multi_select": false
```

Easy allows for diffing with the clipboard selections, and multi-selections.  These all can be turned off or on as desired:

```javascript
    // Use a buffer instead of the output panel
    "use_buffer": true,

    // Enable clipboard commands
    "use_clipboard": true,

    // Enable selection commands
    "use_selections": false,
```

# Dynamic Menu
Easy diff creates a dynamic menu in `User/EasyDiff/Context.sublime-menu`, `User/EasyDiff/Tab Context.sublime-menu`, and `User/EasyDiff/Side Bar.sublime-menu`.  The content of this context menu changes depending on what is enabled or disabled, hidden or shown, and depending on whether a view, selection, or clipboard has been selected for left side compare.  If a view that was previously set has been closed, that view will no longer be reported in the context menu.  You can look here to see how the commands are constructed if you would like to bind the options to shortcuts or to the command palette.

## Excluding Dynamic Menu from Certain UI Elements
Easy diff shows access commands in the view, tab, and sidebar context menu.  If it is desired to exclude access in one of these UI elements, you can remove the element from the following setting:

```javascript
    // Menus to show (view|tab|sidebar)
    "menu_types": ["view", "tab", "sidebar"],
```

# Version Control Setup
EasyDiff currently supports SVN, Git, and Mercurial.  These options should only appear in the context menus if EasyDiff can find the binaries `svn`, `git`, and `hg` respectively.

If one of these options shows up, and you wish to disable them, you can go to your settings file and disable them completely with the following settings:

```javascript
    // Turn off svn completely
    "svn_disabled": false,

    // Turn off git completely
    "git_disabled": false,

    // Turn off (Mercurial) hg completely
    "hg_disabled": false,
```

If you would simply like to hide the options (because you have bound their operations to a shortcut or to the command palette), you can hide the options without disabling them:

```javascript
    // Turn off svn menu access
    "svn_hide_menu": false,

    // Turn off git menu access
    "git_hide_menu": false,

    // Turn off (Mercurial) hg menu access
    "hg_hide_menu": false,
```

If your binaries are not in your system's path, you will need to configure the following settings with the path to your binaries:

```javascript
    // SVN path
    "svn": "",

    // Git Path
    "git": "",

    // (Mercurial) Hg path
    "hg": "",
```

Currently, by default, EasyDiff will check if the current view is versioned controlled by one of your enabled version control options when displaying the context menu.  This allows the for non-pertinent options to be grayed out.  With some version control systems, this can occasionally cause a lag when displaying those options.  You can turn off this functionality if it becomes a problem with the following settings:

```javascript
    // Do not perform a version check on files
    // when evaluating whether version control
    // commands are enabled.  May avoid slowing
    // down context menu draw in large version
    // controlled projects.
    "skip_version_check_on_is_enabled": false,
```

# Diffing with External Diff Tools
Easy diff, by default, has options to diff everything internally in a single view.  But, it can be configured to diff in external tools instead.

Configure the external binary setting to point to diff tool binary, and then enable external diff options:

```javascript
    // Show external options (options to send files to external diff tool)
    "show_external": false,

    // External diff tool path (absolute)
    "external_diff": "",
```

The external option assumes the diff the tool takes arguments as such: `tool file1 file2`.  If this is not the case, you will probably have to wrap the command in a shell script that takes the options as described, and call it directly instead.  For instance, using DeltaWalker on Mac, I copied their provided work flow configuration to a shell script, and call it directly:

```bash
#!/bin/sh
DW_PATH=/Applications/DeltaWalker.app/Contents/MacOS

java -Ddw.path=$DW_PATH -jar $DW_PATH/dw.jar "$1" "$2" "$3" "$4" "$5" "$6"

```

# Hiding External or Internal Diffing from Context Menu
EasyDiff allows you to hide either internal diffing options, external diffing options, or both.  The later options is useful if you do not use the context menu, but have bound the commands to keyboard shortcuts or to the command palette.

The settings are:
```javascript
    // Show internal diff options (Easy Diff in a view or buffer)
    "show_internal": true,

    // Show external options (options to send files to external diff tool)
    "show_external": false,
```
