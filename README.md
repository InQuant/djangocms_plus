
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


## Add to settings
```python
INSTALLED_APPS = [
  ...
  'sass_processor', # site styles
  'adminsortable2', # site styles
  ...
]
```

## include html to your project
```html
{% include 'cmsplus/includes/assets.html' %}
{% include 'cmsplus/includes/_site_styles.html' %}
```

##

```python add to context_processors
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'cmsplus.context_processors.font_assets',
                'cmsplus.context_processors.site_styles',
                ...
            ],
        },
        ...
    },
]
```


## Known Issues
