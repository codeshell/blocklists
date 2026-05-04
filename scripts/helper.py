"""Helper functions"""

import hashlib
import json
from functools import cache
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


@cache
def read_json_from_url(url: str):
    """Read url content into json object

    Args:
        url (str): Url pointing to a json file

    Returns:
        Any | None: JSON object or None
    """
    try:
        with urlopen(url) as r:
            data = json.load(r)
            # data = json.loads(r.read().decode())
            return data

    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None


def read_json_from_file(filename):
    """Read file content into json object

    Args:
        filename (Any): String or Path pointing to file

    Returns:
        Any | None: JSON object or None
    """
    try:
        with open(filename, "rt", encoding="utf-8") as fp:
            data = json.load(fp)
            # data = json.loads(r.read().decode())
            return data

    except FileNotFoundError:
        print(f"{filename} does not exist.")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None


def hash_file(filename) -> None | str:
    """Generate md5 hash for file if it exists"""
    # hashlib.file_digest() supported since Python 3.11
    # return hashlib.file_digest(fp, 'md5').hexdigest()
    # CANNOT use because it does not support text streams, only binary.
    # do not use 'rb' for binary mode because it will never compare with the string hash
    # do not use 'buffering=0'. Can't have unbuffered text I/O
    hash_object = hashlib.md5()
    try:
        with open(filename, "rt", encoding="utf-8") as fp:
            while chunk := fp.read(8192):
                hash_object.update(chunk.encode("utf-8"))
    except FileNotFoundError:
        print(f"{filename} does not exists (yet).")
        return None

    return hash_object.hexdigest()


def hash_string(text):
    """Generate md5 hash for string"""
    # Strings must be encoded before hashing
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def write_list_from_lines(filename: str, lines: dict, args):
    """
    all lines need to pass here before being written so this is the best place
    to remove duplicates and sort to ensure it is done the same way for all files.
    """

    lines = sorted(set(lines))

    new_hash = hash_string("\n".join(lines) + "\n")
    print(f"Hash (md5) new data: {new_hash}")

    old_hash = hash_file(filename)
    print(f"Hash (md5) old data: {old_hash}")

    if old_hash == new_hash:
        print("Nothing to update.")
        return lines

    if not args.dry_run and len(lines) > 0:
        print(f"writing import file with {len(lines)} entries")
        with open(filename, "wt", encoding="utf-8") as fp:
            # always end a text file with a blank line
            fp.write("\n".join(lines) + "\n")

    return lines
