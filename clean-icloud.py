#!/usr/bin/env python3
"""
A script to interact with iCloud photos using pyicloud.

Two sub-commands are available:

1. download: Downloads all photos from iCloud whose creation date is on or before the given date.
2. delete: Deletes (after confirmation) all photos whose creation date is on or before the given date.

Usage examples:
    python script.py --config config.yaml download --date 2022-01-01 --output-dir downloads
    python script.py --config config.yaml delete --date 2022-01-01

Make sure to create a YAML file (default name "config.yaml") with your credentials.
"""

import argparse
import datetime
import os
import sys
import yaml
from pyicloud import PyiCloudService

def load_config(config_file):
    """Load configuration (iCloud credentials) from a YAML file."""
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def login(config):
    """Login to iCloud using credentials from the config.
    
    Handles multi-factor authentication (2FA or 2SA) if required.
    """
    icloud_config = config.get("icloud", {})
    username = icloud_config.get("username")
    password = icloud_config.get("password")
    if not username or not password:
        print("Username and/or password not provided in the config file.")
        sys.exit(1)
        
    api = PyiCloudService(username, password)
    
    # Handle two-factor authentication (2FA) if enabled
    if api.requires_2fa:
        print("Two-factor authentication required. A code has been sent to your devices.")
        code = input("Enter the 2FA code: ").strip()
        if not api.validate_2fa_code(code):
            print("Failed to verify the 2FA code.")
            sys.exit(1)
    
    # Handle two-step authentication (2SA) if enabled
    elif api.requires_2sa:
        print("Two-step authentication required. A code has been sent to your trusted devices.")
        code = input("Enter the 2SA code: ").strip()
        if not api.validate_2sa_code(code):
            print("Failed to verify the 2SA code.")
            sys.exit(1)
            
    return api

def parse_date(date_str):
    """Parse a date string in the format YYYY-MM-DD."""
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please provide a date in YYYY-MM-DD format.")
        sys.exit(1)

def download_photos(api, target_date, output_dir="downloads"):
    """Download all iCloud photos whose creation date is on or before the target date."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    count = 0

    # Note: api.photos.all is a generator of photo objects.
    for photo in api.photos.all:
        try:
            # Assume the photo object has a 'created' attribute as a datetime object.
            photo_date = photo.created.date()
        except Exception as e:
            print(f"Could not determine creation date for a photo: {e}")
            continue

        # If the photo was taken on or before the given date, download it.
        if photo_date <= target_date:
            try:
                print(f"Downloading {photo.filename} taken on {photo_date} ...")
                download_response = photo.download()
                file_path = os.path.join(output_dir, photo.filename)
                with open(file_path, "wb") as f:
                    f.write(download_response.raw.read())
                count += 1
            except Exception as e:
                print(f"Failed to download {photo.filename}: {e}")
    print(f"Downloaded {count} photos to '{output_dir}'.")

def delete_photos(api, target_date):
    """Delete all iCloud photos whose creation date is on or before the target date."""
    photos_to_delete = []
    for photo in api.photos.all:
        try:
            photo_date = photo.created.date()
        except Exception as e:
            print(f"Could not determine creation date for a photo: {e}")
            continue

        if photo_date <= target_date:
            photos_to_delete.append(photo)

    total = len(photos_to_delete)
    print(f"Found {total} photos to delete.")

    # Confirm deletion with the user (irreversible!)
    confirm = input("Are you sure you want to delete these photos? This action cannot be undone. (yes/[no]): ")
    if confirm.lower() != "yes":
        print("Deletion canceled.")
        return

    count = 0
    for photo in photos_to_delete:
        try:
            # Assuming the pyicloud photo object supports deletion via .delete()
            photo.delete()
            print(f"Deleted {photo.filename}")
            count += 1
        except Exception as e:
            print(f"Failed to delete {photo.filename}: {e}")
    print(f"Deleted {count} out of {total} photos.")

def main():
    parser = argparse.ArgumentParser(
        description="A script to download or delete iCloud photos from a given date back to the earliest item."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML config file with iCloud credentials (default: config.yaml)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sub-command: download
    download_parser = subparsers.add_parser(
        "download",
        help="Download all photos taken on or before a given date."
    )
    download_parser.add_argument(
        "--date",
        required=True,
        help="The date (YYYY-MM-DD). Downloads photos taken on or before this date."
    )
    download_parser.add_argument(
        "--output-dir",
        default="downloads",
        help="Directory to store downloaded photos (default: downloads)"
    )

    # Sub-command: delete
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete all photos taken on or before a given date."
    )
    delete_parser.add_argument(
        "--date",
        required=True,
        help="The date (YYYY-MM-DD). Deletes photos taken on or before this date."
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Load configuration and login
    config = load_config(args.config)
    api = login(config)
    target_date = parse_date(args.date)

    if args.command == "download":
        download_photos(api, target_date, output_dir=args.output_dir)
    elif args.command == "delete":
        delete_photos(api, target_date)

if __name__ == "__main__":
    main()
