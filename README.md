# icloud-photos-cleaner

I am not paying more than 0.99 for iCloud. The script helps to download and delete photos in iCloud by a given limit date (going backward)

```
$ python3 -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ cp config.yml.template config.yml
(.venv) $ vim config.yml (Add your iCloud credentials)
```

# Examples

```
(.venv) $ python3 clean-icloud.py --config config.yml download --date 2024-12-31 --output-dir downloads
(.venv) $ python3 clean-icloud.py --config config.yml delete --date 2024-12-31
```