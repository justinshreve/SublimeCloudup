SublimeCloudup
===============

A Sublime plugin that allows you to share code snippet and files to Cloudup without leaving the editor.

The current version only supports snippets/current selection but will include sharing the entire file and multiple files/directories soon.

To install, put the SublimeCloudup folder in your Sublime 'Packages' folder. 

Currently tested with SublimeText 3 on a Mac. Patches welcome to get this working elsewhere.

Once installed, create a 'Cloudup.sublime-settings' file in your settings folder and put your Cloudup credentials in the following format:

```
{
	"username": "",
	"password": "",
}
```

The current keyboard shortcut is ctrl+alt+x. You can override this in your user settings.
