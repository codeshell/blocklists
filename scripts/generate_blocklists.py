"""Generate different block list formats from source files"""

import argparse
import difflib
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


def sanitize_lines(lines: list[str]) -> list[str]:
    """
    lines from files will most likely contain whitespaces such as newlines.
    They must be removed first because they will likely break the following string operations.
    Additionally (not! overwriting the default), this strips any leading and trailing slashes.
    """
    return list(map(lambda x: x.strip().strip(r"\/ "), lines))


def optimize_lines(lines: list[str]) -> list[str]:
    """
    NOT IMPLEMENTED YET
    Remove lines that are only a subset of another line
    """
    # TODO: check, if one entry is part of another rule
    # those redundant rules should be removed.
    # Need to check domains vs subdomains
    # and subdomains vs paths

    # NOTE: no need to sort and remove duplicates here, because this
    # is done only and directly before writing files to storage
    # with helper.write_list_from_lines(). optimize_lines() would
    # catch most but not all cases (e.g. generate_format() changes the
    # lines output for multi-variant lists) and might run multiple times.

    # lines = sorted(set(lines))

    return lines


class UnwantedSites:
    """
    Present lines in different flavors as supported by lists.

    This should not be done inline/on-the-fly because lines need to be optimized
    after changing to prevent unnecessary duplicates
    """

    def __init__(self, lines: list[str], label: str):
        """
        lines: as given by source

        label: identifies the source data context
        """
        self._lines_up_to_domain = None
        self._lines_up_to_path = None
        self.label = label
        self.lines = lines

    @property
    def lines(self) -> list[str]:
        """lines as presented by source"""
        return self._lines

    @lines.setter
    def lines(self, value: list[str]):
        self._lines = value
        self._update_line_flavors()

    @property
    def lines_up_to_subdomain(self) -> list[str]:
        """lines containing domain + subdomain"""
        return self._lines_up_to_domain

    @property
    def lines_up_to_path(self) -> list[str]:
        """lines containing domain + subdomain + path"""
        return self._lines_up_to_path

    def _notice_if_lines_adjusted(self, a, b):
        """
        If the source values are adjusted because of input validation,
        output the difference because they indicate potential errors in the source data
        """
        test_lines = difflib.unified_diff(a, b, "Source", "Adjusted", n=0, lineterm="")
        test_result = "\n".join(test_lines)
        if test_result:
            print(f"There where changes made when ingesting source data ({self.label}).")
            print("Please check if they are intended:")
            print(test_result)
        else:
            print(f"No crazy stuff found ({self.label}).")

    def _update_line_flavors(self):
        """when lines are changed, (re-)generate all line flavors"""
        lines = self._lines

        path_pattern = re.compile(r"(?:.*://)?((?:[^/:?&]+/?)+)[?&]?.*")
        lines = list(map(lambda x: re.match(path_pattern, x).group(1), lines))
        self._notice_if_lines_adjusted(self.lines, lines)
        lines = optimize_lines(lines)
        self._lines_up_to_path = lines

        lines = list(map(lambda x: re.match(r"[^\/:?]*", x).group(0), lines))
        lines = optimize_lines(lines)
        self._lines_up_to_domain = lines


def process_wiki_farm(lines: list[str], suffix: str, args: argparse.Namespace):
    """
    Special treatment for wiki farm domains
    domain name needs to be added
    """

    match suffix:
        case "-by-wiki-gg":
            lines = sanitize_lines(lines)
            lines = list(map(lambda x: x + ".fandom.com", lines))
        case "-by-indie-wiki":
            lines = sanitize_lines(lines)
        case ".all":
            lines = optimize_lines(lines)  # input for aggregated lists is already sanitized
        case _:
            print(f"Suffix {suffix} not defined for processing.")
            return None

    unwanted = UnwantedSites(lines=lines, label="wikifarms" + suffix)
    generate_format(unwanted, ListFormat.UBLACKLIST, args)
    generate_format(unwanted, ListFormat.ADBLOCK, args)
    generate_format(unwanted, ListFormat.DNSMASQ, args)
    generate_format(unwanted, ListFormat.HOSTSETC, args)
    generate_format(unwanted, ListFormat.HOSTSIP4, args)
    generate_format(unwanted, ListFormat.HOSTSIP6, args)
    return unwanted.lines


def generate_format(unwanted: UnwantedSites, custom_format: ListFormat, args: argparse.Namespace) -> bool:
    """
    Use list of lines to generate different formats
    """

    label = unwanted.label
    written_lines = []

    match custom_format:
        case ListFormat.UBLACKLIST:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "*://*." + x.strip() + "/*", unwanted.lines_up_to_path))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.ADBLOCK:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "||" + x.strip() + "^", unwanted.lines_up_to_path))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.DNSMASQ:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: "address=/" + x.strip() + "/", unwanted.lines_up_to_subdomain))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.HOSTSETC:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(map(lambda x: '"*://*.' + x.strip() + '/*",', unwanted.lines_up_to_subdomain))
            written_lines = write_list_from_lines(target_file, target_lines, args)
        case ListFormat.HOSTSIP4:
            target_file = Path(FORMAT_PATH, custom_format.value, label + ".txt")
            target_lines = list(
                map(
                    lambda x: (
                        ("0.0.0.0 " + x.strip()).replace("0 www.", "0 ")
                        + ("\n0.0.0.0 www." + x.strip()).replace("0 www.www.", "0 www.")
                    ),
                    unwanted.lines_up_to_subdomain,
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
                    unwanted.lines_up_to_subdomain,
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
