# icloud-photos-cleaner

I am not paying more than 0.99 for iCloud. The script helps to download and delete photos in iCloud by a given limit date (going backward)

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ cp config.yml.template config.yml
$ vim config.yml (Add your iCloud credentials)
```

# Examples

```
$ python3 clean-icloud.py --config config.yaml download --date 2024-12-31 --output-dir downloads
$ python3 clean-icloud.py --config config.yaml delete --date 2024-12-31
```