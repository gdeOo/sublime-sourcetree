# Sublime SourceTree

A [Sublime Text 2 & 3](http://www.sublimetext.com/) plugin that integrates with [Atlassian SourceTree](https://www.atlassian.com/software/sourcetree/overview) to provide some useful commands.

## Installation

### Manual installation

Copy the `sublime-sourcetree` folder to the `Packages` folder of Sublime Text 2, which will be located in:
  * Windows 7+:  `C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages`;
  * Windows XP: `C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages`;
  * OSX: `~/Library/Application Support/Sublime Text 2/Packages/`.

## Settings

In order for the commands to be enabled, the plugin must be able to locate the Atlassian SourceTree executable.
The plugin will automatically search for the executable in the most common installation directories.
You may, however, provide the path to the executable yourself by changing the `detect_sourcetree` and `sourcetree_path` settings:
```
{
    "detect_sourcetree": false,
    "sourcetree_path": "<path_to_sourcetree_executable>"
}
```

## Usage

The plugin offers the following commands:
  * **SourceTree File Log**

      Opens SourceTree's file log view for the current file.

  * **SourceTree Search for Selection**

      Opens SourceTree's search view using the current selection as the search term.

  * **SourceTree Commit**

      Opens SourceTree's commit view for the current repository.

