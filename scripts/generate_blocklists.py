import argparse
from os import error
from enum import Enum
from pathlib import Path

from helper import write_list_from_lines


class ListFormat(Enum):
    UBLACKLIST = "ublacklist"
    ADBLOCK = "adblock"
    DNSMASQ = "dnsmasq"
    HOSTSETC = "hostsetc"
    HOSTSIP4 = "hostsip4"
    HOSTSIP6 = "hostsip6"


ROOT_PATH = Path(__file__).parent.parent
FORMAT_PATH = Path(ROOT_PATH, "by-format")
SOURCE_PATH = Path(ROOT_PATH, "sources")


def get_source_file_lines(filename):
    try:
        with open(filename, "rt", encoding="utf-8") as fp:
            return fp.readlines()
    except FileNotFoundError:
        print(f"Please check existence of file {filename}.")
        return None
    except error as e:
        print(f"File {filename} not loaded: {e}.")
        return None


def process_wiki_farm(lines, suffix):
    """
    Special treatment for wiki farm domains
    domain name needs to be added
    """
    lines_with_domain = list(map(lambda x: x.strip() + ".fandom.com", lines))
    generate_format(lines_with_domain, ListFormat.UBLACKLIST, "wikifarms" + suffix)
    generate_format(lines_with_domain, ListFormat.ADBLOCK, "wikifarms" + suffix)
    generate_format(lines_with_domain, ListFormat.DNSMASQ, "wikifarms" + suffix)
    generate_format(lines_with_domain, ListFormat.HOSTSETC, "wikifarms" + suffix)
    generate_format(lines_with_domain, ListFormat.HOSTSIP4, "wikifarms" + suffix)
    generate_format(lines_with_domain, ListFormat.HOSTSIP6, "wikifarms" + suffix)


def generate_format(lines, format: ListFormat, label: str):
    """
    Use list of lines to generate different formats
    """
    match format:
        case ListFormat.UBLACKLIST:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(map(lambda x: "*://*." + x.strip() + "/*", lines))
            write_list_from_lines(target_file, target_lines, args)
            return True
        case ListFormat.ADBLOCK:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(map(lambda x: "||" + x.strip() + "^", lines))
            write_list_from_lines(target_file, target_lines, args)
            return True
        case ListFormat.DNSMASQ:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(map(lambda x: "address=/" + x.strip() + "/", lines))
            write_list_from_lines(target_file, target_lines, args)
            return True
        case ListFormat.HOSTSETC:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(map(lambda x: '"*://*.' + x.strip() + '/*",', lines))
            write_list_from_lines(target_file, target_lines, args)
            return True
        case ListFormat.HOSTSIP4:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(
                map(
                    lambda x: (
                        ("0.0.0.0 " + x.strip()).replace("0 www.", "0 ")
                        + ("\n0.0.0.0 www." + x.strip()).replace("0 www.www.", "0 www.")
                    ),
                    lines,
                )
            )
            write_list_from_lines(target_file, target_lines, args)
            return True
        case ListFormat.HOSTSIP6:
            target_file = Path(FORMAT_PATH, format.value, label + ".txt")
            target_lines = list(
                map(
                    lambda x: (
                        ("::1 " + x.strip()).replace("1 www.", "1 ")
                        + ("\n::1 www." + x.strip()).replace("1 www.www.", "1 www.")
                    ),
                    lines,
                )
            )
            write_list_from_lines(target_file, target_lines, args)
            return True
        case _:
            print(f"Format {format} not implemented.")
            return None


def init_folders():
    """
    docstring
    """
    result = True
    for folder in ListFormat:
        test_path = Path(FORMAT_PATH, folder.value)
        if test_path.exists():
            print(f"OK: {test_path} exists.")
        elif args.dry_run:
            print(f"WARNING: {test_path} needs to be created.")
            result = False
        elif args.init_folders:
            # only create new folders with this flag
            test_path.mkdir(parents=False, exist_ok=False)
        else:
            print(f"WARNING: {test_path} needs to be created.")
            print("Use --init-folders to do that.")
            result = False
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--init-folders", action="store_true")
    args = parser.parse_args()

    if init_folders():
        bundle = {}
        bundle[1] = get_source_file_lines(Path(SOURCE_PATH, "import_from_wiki_gg.txt"))
        process_wiki_farm(bundle[1], "-by-wiki-gg")
        bundle[2] = get_source_file_lines(Path(SOURCE_PATH, "import_from_wiki_gg.txt"))
        # process_wiki_farm(bundle[2], "-by-wiki-gg")
        process_wiki_farm(sorted(set(sum(bundle.values(), []))), ".all")
