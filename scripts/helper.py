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


def compare_url_subsets(main_str: str, search_str: str) -> bool:
    """
    Split search, but not before the length of main because that creates false negatives and could never match anyway
    There is no start pos for split so we need to slice the protected part first, then split and add it back

    For best match quality make sure the input does not contain protocol prefixes (http://, https://, etc://)
    """

    # speed things up
    if len(main_str) > len(search_str):
        return False

    # get direct hits out of the way. This includes all root domain entries.
    # root domains MUST NOT be tested later with "in string" search, because this will create false matches
    # e.g. anotherexample.com vs example.com
    if search_str.startswith(main_str):
        return True

    protected_search_part = search_str[: len(main_str)]
    restored_search = protected_search_part + search_str[len(main_str) :].split("/", maxsplit=1)[0]
    # print(f"Protected {protected_search_part} from {search_str} when checking {main_str}.")
    # print(f"Reassembled search is {restored_search}")

    # make sure this never triggers on parts of domain names, because they are totally unrelated
    # e.g. crap-and-not-amazing.example.com vs amazing.example.com
    return "." + main_str in restored_search


def write_list_from_lines(
    filename: str, lines: list[str], args, header: list[str] = None, footer: list[str] = None
) -> list[str]:
    """
    all lines need to pass here before being written so this is the best place
    to remove duplicates and sort to ensure it is done the same way for all files.
    """

    if header is None:
        header = []

    if footer is None:
        footer = []

    lines = header + sorted(set(lines)) + footer

    new_hash = hash_string("\n".join(lines) + "\n")
    print(f"Hash (md5) new data: {new_hash}")

    old_hash = hash_file(filename)
    print(f"Hash (md5) old data: {old_hash}")

    if old_hash == new_hash:
        print(f"Nothing to update ({filename}).")
        return lines

    if not args.dry_run and len(lines) > 0:
        print(f"writing import file with {len(lines)} entries")
        with open(filename, "wt", encoding="utf-8") as fp:
            # always end a text file with a blank line
            fp.write("\n".join(lines) + "\n")

    return lines
