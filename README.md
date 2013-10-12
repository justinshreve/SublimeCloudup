SublimeCloudup
===============

A Sublime plugin that allows you to share code snippet and files to Cloudup without leaving the editor.
See https://cloudup.com/

You can upload:
* Snippets of code (currently selection or highlighted line)
* Single files (currently open file or files from the sidebar)
* Multiple files (share an entire directory from the sidebar)

The current version supports sharings snippets/current selection and the currently opened file.
Support for sharing multiple files/directories is coming soon.

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

Once the code is uploaded, the stream URL will be copied to your clipboard. You should see a status message at the bottom of the screen about it.
