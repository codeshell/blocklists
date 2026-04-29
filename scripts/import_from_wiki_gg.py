import argparse
import hashlib
import json
from functools import cache
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Source: https://github.com/wiki-gg-oss/redirect-extension
SOURCE_URL = "https://raw.githubusercontent.com/wiki-gg-oss/redirect-extension/refs/heads/master/sites.json"
IMPORT_FILE = "./sources/import_from_wiki_gg.txt"
FAILSAFE_FIRST_ID = "13sentinels"


@cache
def read_json_from_url(url):
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
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def get_unwanted_from_entry(entry):
    test_value = entry.get("oldId", "")
    if len(test_value) > 0:
        return test_value

    test_value = entry.get("id", "")
    if len(test_value) > 0:
        return test_value

    return None


def hash_file(filename):
    # hashlib.file_digest() supported since Python 3.11
    # return hashlib.file_digest(fp, 'md5').hexdigest()
    # CANNOT use because it does not support text streams, only binary.
    # do not use 'rb' for binary mode because it will never compare with the string hash
    # do not use 'buffering=0'. Can't have unbuffered text I/O
    hash_object = hashlib.md5()
    with open(filename, "rt", encoding="utf-8") as fp:
        while chunk := fp.read(8192):
            hash_object.update(chunk.encode("utf-8"))

    return hash_object.hexdigest()


def hash_string(text):
    # Strings must be encoded before hashing
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def create_list_from_json(json_object, args):
    text = []
    for entry in json_object:
        if isinstance(entry, list):
            for subentry in entry:
                text.append(get_unwanted_from_entry(subentry))
        elif isinstance(entry, dict):
            text.append(get_unwanted_from_entry(entry))
        else:
            print(type(entry))
            print(f"Strange things happened with {entry}")

    # optimized_list = sorted(set(text.split("\n")))
    optimized_list = sorted(set(filter(None, text)))

    new_hash = hash_string("\n".join(optimized_list) + "\n")
    print(f"Hash (md5) new data: {new_hash}")

    old_hash = hash_file(IMPORT_FILE)
    print(f"Hash (md5) old data: {old_hash}")

    if old_hash == new_hash:
        print("Nothing to update.")
        return optimized_list

    if not args.dry_run and len(optimized_list) > 0:
        print(f"writing import file with {len(optimized_list)} entries")
        with open(IMPORT_FILE, "wt", encoding="utf-8") as fp:
            # always end a text file with a blank line
            fp.write("\n".join(optimized_list) + "\n")

    return optimized_list


# Usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = read_json_from_url(SOURCE_URL)

    if source:
        if args.debug:
            print(json.dumps(source))

        print("\nSuccessfully fetched data:")
        print("Expected ID: {FAILSAFE_FIRST_ID}")
        test_first_id = source[1]["id"]
        print(f"First ID: {test_first_id}")

        if FAILSAFE_FIRST_ID == test_first_id:
            create_list_from_json(source, args)
        else:
            print(
                "IMPORT CANCELLED: First ID does not match expected value. Please verify the source data."
            )
            print("If the source has a new structure or order, adjust this script.")
