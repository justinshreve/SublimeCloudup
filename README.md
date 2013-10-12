SublimeCloudup
===============

A Sublime plugin that allows you to share code snippet and files to Cloudup without leaving the editor.
See https://cloudup.com/

You can upload:

* Snippets of code (current selection or highlighted line)
* Single files (currently opened file or files from the sidebar)
* Multiple files (share an entire directory from the sidebar)


## To install

Put the SublimeCloudup folder in your Sublime 'Packages' folder. 

Create a 'Cloudup.sublime-settings' file in your settings folder and put your Cloudup credentials in the following format:

```
{
	"username": "",
	"password": "",
}
```

## Notes

Currently tested with SublimeText 3 on a Mac. Patches welcome to get this working elsewhere.

The current keyboard shortcuts are:

* ctrl+alt+x for the current selection
* ctrl+alt+d for the current file 

You can override these in your user keybinding file.

Menu options for uploading can be found under File > Cloudup
Right clicking items in the sidebar will show an upload option.

The stream or item URL will be copied to your clipboard automatically. You should see a status message at the bottom of the screen about it.

## Changelog

### 1.0 

Initial Relase. Contains menu, sidebar, and keyboard shortcut support.
Allows for uploading of snippets, files, and multiple files.
