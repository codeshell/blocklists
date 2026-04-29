import argparse
import json

from helper import hash_file, hash_string, read_json_from_url

# Source: https://github.com/wiki-gg-oss/redirect-extension
SOURCE_URL = "https://raw.githubusercontent.com/wiki-gg-oss/redirect-extension/refs/heads/master/sites.json"
IMPORT_FILE = "./sources/import_from_wiki_gg.txt"
FAILSAFE_FIRST_ID = "13sentinels"
FAILSAFE_FIRST_OLDID = "13-sentinels-aegis-rim"


def get_unwanted_from_entry(entry):
    test_value = entry.get("oldId", "")
    if len(test_value) > 0:
        return test_value

    test_value = entry.get("id", "")
    if len(test_value) > 0:
        return test_value

    return None


def create_list_from_json(json_object):
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

        print(f"Expected ID: {FAILSAFE_FIRST_ID}")
        try:
            test_first_id = source[1]["id"]
        except AttributeError, IndexError, KeyError, TypeError:
            test_first_id = ""
        print(f"First ID: {test_first_id}")

        print(f"Expected old ID: {FAILSAFE_FIRST_OLDID}")
        try:
            test_first_oldid = source[1]["oldId"]
        except AttributeError, IndexError, KeyError, TypeError:
            test_first_oldid = ""
        print(f"First old ID: {test_first_oldid}")

        if (
            FAILSAFE_FIRST_ID == test_first_id
            and FAILSAFE_FIRST_OLDID == test_first_oldid
        ):
            create_list_from_json(source)
        else:
            print(
                "IMPORT CANCELLED: First ID does not match expected value. Please verify the source data."
            )
            print("If the source has a new structure or order, adjust this script.")
