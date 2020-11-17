
# DjangoCMS Plus

## Info
IconPlugin:
- include icon css in projects head
- include css in CKEDITOR Settings in `settings.py`

## Features
- Plugin Data stored as JSON, no need for migrations if plugin changes
- Copy & Paste Plugin structures through JSON and the clipboard functionality
- Marks Plugins red if plugin form contains errors


## TODO 
- Clipboard: Refresh page when Clipboard import was successful
    - modal on_close=REFRESH_PAGE is not working 


## Known Issuesb
- Icon Plugin is not working in CKTextEditor-Preview. Fonts need to be included in ckeditor js files, but how?