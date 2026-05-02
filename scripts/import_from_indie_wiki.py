import argparse
import json
from datetime import datetime, timezone
from enum import Enum
from os import error
from pathlib import Path

from helper import hash_file, hash_string, read_json_from_url, read_json_from_file


class ChangeLog(Enum):
    DATE = "date"
    CHANGES = "changes"
    REMOVED = "removed"
    ADDED = "added"
    UPDATED = "updated"


# Source: https://github.com/KevinPayravi/indie-wiki-buddy
SOURCE_URL_FOLDER = "https://raw.githubusercontent.com/KevinPayravi/indie-wiki-buddy/refs/heads/main/data/"
SOURCE_TREE = (
    "https://api.github.com/repos/KevinPayravi/indie-wiki-buddy/git/trees/main"
)
ROOT_PATH = Path(__file__).parent.parent
IMPORT_PREFIX = "import_from_indie_wiki"
IMPORT_FOLDER = Path(ROOT_PATH, "sources")
IMPORT_FILE = Path(IMPORT_FOLDER, f"{IMPORT_PREFIX}.txt")
IMPORT_HIST_FILE = Path(ROOT_PATH, "logs", f"{IMPORT_PREFIX}.changes.json")
IMPORT_SITES_FILE = Path(ROOT_PATH, "logs", f"{IMPORT_PREFIX}.sites.json")
TEST_DUMMY = Path(ROOT_PATH, "eggs", "sites_dummy.json")

# IMPORT_STATE_FILE = Path(ROOT_PATH, "logs", f"{IMPORT_PREFIX}.state.json")
# TEST_FILE = Path(ROOT_PATH, "eggs",  "sites.json")


def get_unwanted_from_origin(origin):
    if isinstance(origin, dict):
        test_value = origin.get("origin_base_url", "")
        if len(test_value) > 0:
            # base is required, content is optional
            test_value += origin.get("origin_content_path", "")
            return test_value

    return None


def create_list_from_json(json_object, site_import_file):
    text = []
    for wiki in json_object:
        if isinstance(wiki, list):
            print(type(wiki))
            print(f"Not implemented for {wiki}")
        elif isinstance(wiki, dict):
            for origin in wiki.get("origins", []):
                text.append(get_unwanted_from_origin(origin))
        else:
            print(type(wiki))
            print(f"Strange things happened with {wiki}")

    # optimized_list = sorted(set(text.split("\n")))
    optimized_list = sorted(set(filter(None, text)))

    new_hash = hash_string("\n".join(optimized_list) + "\n")
    print(f"Hash (md5) new data: {new_hash}")

    old_hash = hash_file(site_import_file)
    print(f"Hash (md5) old data: {old_hash}")

    if old_hash == new_hash:
        print("Nothing to update.")
        return optimized_list

    if not args.dry_run and len(optimized_list) > 0:
        print(f"writing import file with {len(optimized_list)} entries")
        with open(site_import_file, "wt", encoding="utf-8") as fp:
            # always end a text file with a blank line
            fp.write("\n".join(optimized_list) + "\n")

    return optimized_list


def get_data_tree(url):
    """
    Use GitHub API to find all Site*.json files
    GitHub Trees have SHA1 values for all files, this allows to compare if needed
    """
    root_tree = read_json_from_url(url)

    if isinstance(root_tree, dict):
        for item in root_tree.get("tree", {}):
            if item.get("path", "") == "data":
                data_tree = read_json_from_url(item.get("url", None))
                return data_tree
    return None


def get_sites_with_new_data(remote_sites_cleaned, local_sites_cleaned):
    """
    Compare the new github tree to the last run (if exists)
    and only return sites where the SHA hash does not match
    """
    sites_with_changes = {}
    sites_with_changes[ChangeLog.DATE.value] = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    sites_with_changes[ChangeLog.CHANGES.value] = 0
    sites_with_changes[ChangeLog.REMOVED.value] = list(
        filter(
            lambda item: (
                next(
                    (
                        sub
                        for sub in remote_sites_cleaned
                        if sub["path"] == item["path"]
                    ),
                    None,
                )
                is None
            ),
            local_sites_cleaned,
        )
    )
    sites_with_changes[ChangeLog.CHANGES.value] += len(
        sites_with_changes[ChangeLog.REMOVED.value]
    )
    sites_with_changes[ChangeLog.ADDED.value] = list(
        filter(
            lambda item: (
                next(
                    (sub for sub in local_sites_cleaned if sub["path"] == item["path"]),
                    None,
                )
                is None
            ),
            remote_sites_cleaned,
        )
    )
    sites_with_changes[ChangeLog.CHANGES.value] += len(
        sites_with_changes[ChangeLog.ADDED.value]
    )
    sites_with_changes[ChangeLog.UPDATED.value] = list(
        filter(
            lambda item: (
                next(
                    (
                        sub
                        for sub in local_sites_cleaned
                        if sub["path"] == item["path"] and sub["sha"] != item["sha"]
                    ),
                    None,
                )
                is not None
            ),
            remote_sites_cleaned,
        )
    )
    sites_with_changes[ChangeLog.CHANGES.value] += len(
        sites_with_changes[ChangeLog.UPDATED.value]
    )
    return sites_with_changes


def validate_github_tree_list(tree) -> bool:
    """
    docstring
    """
    if not isinstance(tree, dict):
        print(
            "CANCELED: Expected root element: dict, data contains: {0}".format(
                type(tree)
            )
        )
        return False

    match tree.get("truncated", "missing"):
        case "missing":
            # First check for "missing", because a filled string is also = True (see second case)
            print("CANCELED: Source data not valid. Field 'truncated' is missing.")
            return False
        case True:
            print(
                "CANCELED: Source data is 'truncated' which indicates a change in the repository structure."
            )
            return False
        case False:
            # This is what we are looking for
            pass
        case _:
            print(
                "CANCELED: Check of truncation field ended in undefined state. Please check."
            )
            return False

    twigs = tree.get("tree", None)
    if not isinstance(twigs, list):
        print("CANCELED: No valid file listing (tree) found in data.")
        return False
    for site in twigs:
        if (
            site.get("type", None) == "blob"
            and site.get("path", "")[-5:] == ".json"
            and site.get("sha", None) is not None
            and site.get("size", None) is not None
        ):
            # Only if there is at least one page entry that can be processed, the file is considered "valid"
            return True
        else:
            print(
                f"|| {site.get('type', None)} || {site.get('path', '')[-5:]} || {site.get('sha', None)} || {site.get('size', None)} ||"
            )
            print(f"Checked {site} and found nothing valid.")

    print("Validation completed without finding at least one valid site entry.")
    return False


def clean_github_tree_list(tree):
    """
    docstring
    """
    if not isinstance(tree, dict):
        return None
    twigs = tree.get("tree", None)
    if not isinstance(twigs, list):
        return None
    sites = list(
        filter(
            lambda item: (
                item.get("type") == "blob" and item.get("path", "")[-5:] == ".json"
            ),
            twigs,
        )
    )
    if len(sites) < 1:
        return None

    whitelist = ["path", "sha", "size"]
    # NOTE: WORKS as intended! Returns a list of reduced dictionaries
    # EXAMPLE: return list(map(lambda site: {k: site[k] for k in whitelist if k in site}, sites))
    return list(map(lambda site: {k: site[k] for k in whitelist if k in site}, sites))


def update_indie_wiki_source():
    """
    docstring
    """

    # NOTE: REMOVE DUMMY AFTER TESTING!!!
    # TODO: DO NOT FORGET!
    remote_hash_tree = get_data_tree(SOURCE_TREE)
    # with open(TEST_DUMMY, "rt", encoding="utf-8") as fp:
    #     remote_hash_tree = json.load(fp)

    if not validate_github_tree_list(remote_hash_tree):
        # we need to get out of here
        # without valid remote data, there is nothing to do
        print("FAILED to validate remote_hash_tree")
        return False
    else:
        print("SUCCESS: remote_hash_tree is _valid_")

    remote_sites_cleaned = clean_github_tree_list(remote_hash_tree)
    if not remote_sites_cleaned:
        # same
        print("FAILED to clean up remote_hash_tree")
        return False
    else:
        print(
            f"SUCCESS: remote_hash_tree is _cleaned_ ({len(remote_sites_cleaned)} sites)"
        )

    local_hash_tree = read_json_from_file(IMPORT_SITES_FILE)
    local_sites_cleaned = None

    # a local comparison file is not necessary, but if we have one
    # use it to prevent constantly recreating year old stuff

    if validate_github_tree_list(local_hash_tree):
        print("SUCCESS: local_hash_tree is _valid_")
        local_sites_cleaned = clean_github_tree_list(local_hash_tree)

    if not local_sites_cleaned:
        print("SKIP: local_hash_tree because no valid entries were found.")
        # just make sure, its a list to create the needed updates against it
        local_sites_cleaned = []
    else:
        print(
            f"SUCCESS: local_hash_tree is _cleaned_ ({len(local_sites_cleaned)} sites)"
        )

    if args.debug:
        print(json.dumps(remote_sites_cleaned, indent=2))

    sites_with_changes = get_sites_with_new_data(
        remote_sites_cleaned, local_sites_cleaned
    )
    if args.debug:
        print(json.dumps(sites_with_changes, indent=2))

    if not (sites_with_changes and sites_with_changes.get("changes", 0) > 0):
        # NOTE: Until now, no files should be changed. No logs, no new timestamps
        # If the data get no update, nothing else should change in the repo from
        # automated runs of this script.
        print("NO CHANGE. There was nothing to update. FINIS")
        return False

    try:
        with open(IMPORT_HIST_FILE, "at", encoding="utf-8") as fp:
            fp.write(json.dumps(sites_with_changes, indent=2) + ",\n")
    except error as e:
        print(f"Ignored: Something went wrong when writing the changelog. {e}")

    # NOTE: Everything, that does not allow to update the
    # local hash file goes here (so that it is repeated until)
    # the error is fixed.
    critical_errors = []

    for site in sites_with_changes[ChangeLog.REMOVED.value]:
        filename = get_site_import_filename(site.get("path", None))
        if filename:
            try:
                filename.unlink()
            except FileNotFoundError:
                print(f"SKIP DELETION: {filename} does not exist.")
            except error as e:
                critical_errors.append(f"DEL: {filename}")
                print(f"FAILED DELETION: {e}")
            else:
                print(f"REMOVED: {filename.name}")

    for site in sites_with_changes[ChangeLog.ADDED.value]:
        filename = get_site_import_filename(site.get("path", None))
        if filename:
            try:
                source = read_json_from_url(SOURCE_URL_FOLDER + site.get("path", None))
                if not create_list_from_json(source, filename):
                    critical_errors.append(f"ADD: {filename}")
            except error as e:
                critical_errors.append(f"ADD: {filename}")
                print(f"FAILED ADDITION: {e}")
            else:
                print(f"ADDED: {filename.name}")

    for site in sites_with_changes[ChangeLog.UPDATED.value]:
        filename = get_site_import_filename(site.get("path", None))
        if filename:
            try:
                source = read_json_from_url(SOURCE_URL_FOLDER + site.get("path", None))
                if not create_list_from_json(source, filename):
                    critical_errors.append(f"UPD: {filename}")
            except error as e:
                critical_errors.append(f"UPD: {filename}")
                print(f"FAILED UPDATE: {e}")
            else:
                print(f"UPDATED: {filename.name}")

    if len(critical_errors) > 0:
        print(
            f"Cannot pin new hash version because of critical errors ({len(critical_errors)})"
        )
    elif args.dry_run:
        print("Hash values not updated because dry run is active.")
    else:
        # NOTE: This should be the only location where config files like hashes are updated
        with open(IMPORT_SITES_FILE, "wt", encoding="utf-8") as fp:
            json.dump(remote_hash_tree, fp=fp, indent=2)
            print(f"Saved new hashes to: {IMPORT_SITES_FILE}")
        return True

    return False


def get_site_import_filename(sitename) -> Path | None:
    """
    docstring
    """
    if sitename and sitename[-5:] == ".json":
        return Path(IMPORT_FOLDER, IMPORT_PREFIX + "." + sitename[:-5].lower() + ".txt")
    return None


# Usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    update_indie_wiki_source()
