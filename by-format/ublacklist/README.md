---
title: Usage of format ublacklist
date: 2026-05-02
updated: 2026-05-07
targets:
- uBlacklist
---

## <img src="../../docs/.assets/ublacklist.svg" height="24"/> uBlacklist

### Subscription links

| view | raw | bl | cdn | variant |
| --- | --- | --- | --- | --- |
| [👁️](./wikifarms.all.txt) | [➕](https://raw.githubusercontent.com/codeshell/blocklists/main/by-format/ublacklist/wikifarms.all.txt) | [<img src="../../docs/.assets/ublacklist.svg" height="24"/>](https://ublacklist.github.io/rulesets/subscribe?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcodeshell%2Fblocklists%2Fmain%2Fby-format%2Fublacklist%2Fwikifarms.all.txt) | [<img src="../../docs/.assets/jsdelivr.svg" height="24"/>](https://cdn.jsdelivr.net/gh/codeshell/blocklists/by-format/ublacklist/wikifarms.all.txt) | Aggregates all wikifarms lists |
| [👁️](./wikifarms-by-wiki-gg.txt) | [➕](https://raw.githubusercontent.com/codeshell/blocklists/main/by-format/ublacklist/wikifarms-by-wiki-gg.txt) | [<img src="../../docs/.assets/ublacklist.svg" height="24"/>](https://ublacklist.github.io/rulesets/subscribe?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcodeshell%2Fblocklists%2Fmain%2Fby-format%2Fublacklist%2Fwikifarms-by-wiki-gg.txt)  | [<img src="../../docs/.assets/jsdelivr.svg" height="24"/>](https://cdn.jsdelivr.net/gh/codeshell/blocklists/by-format/ublacklist/wikifarms-by-wiki-gg.txt) | wiki.gg identified wikifarms only |
| [👁️](./wikifarms-by-indie-wiki.txt) | [➕](https://raw.githubusercontent.com/codeshell/blocklists/main/by-format/ublacklist/wikifarms-by-indie-wiki.txt) | [<img src="../../docs/.assets/ublacklist.svg" height="24"/>](https://ublacklist.github.io/rulesets/subscribe?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcodeshell%2Fblocklists%2Fmain%2Fby-format%2Fublacklist%2Fwikifarms-by-indie-wiki.txt)  | [<img src="../../docs/.assets/jsdelivr.svg" height="24"/>](https://cdn.jsdelivr.net/gh/codeshell/blocklists/by-format/ublacklist/wikifarms-by-indie-wiki.txt) | indie-wiki identified wikifarms only |

Explanation:

- view: open the file in this repository
- raw: right-click to copy the raw link to a list for subscriptions (or open to check the content)
- bl: automatically subscribe if you have that uBlacklist feature activated (otherwise opens a page to copy the link)
- cdn: alternative link to the raw file for users that cannot or don't want to use direct links to github

> [!TIP]
> If in doubt, use the `bl` link.

### Specification

Official ruleset definition: https://github.com/iorate/ublacklist/blob/master/docs/ruleset-spec.md

Official sample subscription file: https://raw.githubusercontent.com/iorate/ublacklist-example-subscription/master/uBlacklist.txt

Rules can be written as [match patterns](https://ublacklist.github.io/docs/advanced-features#match-patterns) or [expressions](https://ublacklist.github.io/docs/advanced-features#expressions). Both variants can be mixed and matched.

> [!NOTE]
> As of now, only `match patterns` are used in this repository.

The subscription files must be encoded in `utf-8`.

It is recommended[^1], to add a YAML frontmatter with at least a name for the ruleset.

> [!NOTE]
> Adding the frontmatter enhances user experience. This repository uses:
> - `name`
> - `description`
> - `homepage`
> - `variants`

The frontmatter might break things for users who want to use the list with something other than official uBlacklist tools.

_If you experience such a use case, please let me know._

## Compatible services

_If you know of other tools, apps or services that make use of lists in "uBlacklist"-Format, please let me know._

[^1]: https://ublacklist.github.io/docs/advanced-features#publish-subscription
