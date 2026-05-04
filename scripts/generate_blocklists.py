"""Generate different block list formats from source files"""

import argparse
import re
from enum import Enum
from os import error
from pathlib import Path

from helper import write_list_from_lines


class ListFormat(Enum):
    """Class enumerating block list formats"""

    UBLACKLIST = "ublacklist"
    ADBLOCK = "adblock"
    DNSMASQ = "dnsmasq"
    HOSTSETC = "hostsetc"
    HOSTSIP4 = "hostsip4"
    HOSTSIP6 = "hostsip6"


ROOT_PATH = Path(__file__).parent.parent
FORMAT_PATH = Path(ROOT_PATH, "by-format")
SOURCE_PATH = Path(ROOT_PATH, "sources")


def get_source_file_lines(filename) -> list[str] | None:
    """Try to read file as list of strings"""
    try:
        with open(filename, "rt", encoding="utf-8") as fp:
            return fp.readlines()
    except FileNotFoundError:
        print(f"Please check existence of file {filename}.")
        return None
    except error as e:
        print(f"File {filename} not loaded: {e}.")
        return None


def process_wiki_farm(lines: list[str], suffix: str, args: argparse.Namespace):
    """
    Special treatment for wiki farm domains
    domain name needs to be added
    """

    # lines will most likely contain whitespaces such as newlines.
    # They must be removed first because they will likely break the following string operations.
    lines = list(map(lambda x: x.strip(), lines))

    match suffix:
        case "-by-wiki-gg":
            lines_with_domain = list(map(lambda x: x + ".fandom.com", lines))
            generate_format(lines_with_domain, ListFormat.UBLACKLIST, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.ADBLOCK, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.DNSMASQ, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSETC, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP4, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP6, "wikifarms" + suffix, args)
            return lines_with_domain
        case "-by-indie-wiki":
            lines_with_path = list(map(lambda x: x.strip(r"\/ "), lines))
            lines_with_domain = list(map(lambda x: re.match(r"[^\/:?]*", x.strip(r"\/ ")).group(0), lines))
            generate_format(lines_with_path, ListFormat.UBLACKLIST, "wikifarms" + suffix, args)
            generate_format(lines_with_path, ListFormat.ADBLOCK, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.DNSMASQ, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSETC, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP4, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP6, "wikifarms" + suffix, args)
            return lines_with_path
        case ".all":
            # TODO: check, if one entry is part of another rule
            # those redundant rules should be removed.
            # Need to check domains vs subdomains
            # and subdomains vs paths
            lines_with_path = list(map(lambda x: x.strip(r"\/ "), lines))
            lines_with_domain = list(map(lambda x: re.match(r"[^\/:?]*", x.strip(r"\/ ")).group(0), lines))
            generate_format(lines_with_path, ListFormat.UBLACKLIST, "wikifarms" + suffix, args)
            generate_format(lines_with_path, ListFormat.ADBLOCK, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.DNSMASQ, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSETC, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP4, "wikifarms" + suffix, args)
            generate_format(lines_with_domain, ListFormat.HOSTSIP6, "wikifarms" + suffix, args)
            return lines_with_path
        case _:
            print(f"Suffix {suffix} not defined for processing.")
            return None


def generate_format(lines: list[str], custom_format: ListFormat, label: str, args: argparse.Namespace) -> bool:
    """
    Use list of lines to generate different formats
    """

    written_lines = []

    match custom_format:
        case ListFormat.UBLACKLIST:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "*://*." + x.strip() + "/*", lines))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.ADBLOCK:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "||" + x.strip() + "^", lines))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.DNSMASQ:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "address=/" + x.strip() + "/", lines))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.HOSTSETC:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: '"*://*.' + x.strip() + '/*",', lines))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.HOSTSIP4:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(
                map(
                    lambda x: (
                        ("0.0.0.0 " + x.strip()).replace("0 www.", "0 ")
                        + ("\n0.0.0.0 www." + x.strip()).replace("0 www.www.", "0 www.")
                    ),
                    lines,
                )
            )
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.HOSTSIP6:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(
                map(
                    lambda x: (
                        ("::1 " + x.strip()).replace("1 www.", "1 ")
                        + ("\n::1 www." + x.strip()).replace("1 www.www.", "1 www.")
                    ),
                    lines,
                )
            )
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case _:
            print(f"Format {custom_format} not implemented.")
            return None

    return len(written_lines) > 0


def init_folders(args: argparse.Namespace):
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


def main():
    """
    Entry point.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--init-folders", action="store_true")
    args = parser.parse_args()

    if init_folders(args=args):
        bundle = {}

        bundle[1] = []
        bundle[1] += get_source_file_lines(Path(SOURCE_PATH, "import_from_wiki_gg.txt"))
        bundle[1] = process_wiki_farm(bundle[1], "-by-wiki-gg", args=args)

        bundle[2] = []
        # for source_filename in glob(SOURCE_PATH.rglob("import_from_indie_wiki*")):
        for source_file in SOURCE_PATH.rglob("import_from_indie_wiki*"):
            bundle[2] += get_source_file_lines(source_file)
        bundle[2] = process_wiki_farm(bundle[2], "-by-indie-wiki", args=args)

        # process_wiki_farm(sorted(set(sum(bundle.values(), []))), ".all")
        # sorting will happen just before writing to file
        process_wiki_farm(sum(bundle.values(), []), ".all", args=args)


if __name__ == "__main__":
    main()
