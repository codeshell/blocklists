# TMW Blocklists

Generate subscribable text files in various formats containing domains/subdomains/paths to block unwanted sites from web searches or dns queries.

## Goal

- Make existing resources available for common blocking applications by ingesting them and converting to linkable blocklist files.
- Not reinventing the wheel. Only create lists for topics that are not yet covered by recommended lists. If I miss something, please voice it.

## Generated lists

Lists are generated in separate folders sorted `by-format` as my take is that users are usually looking for lists in only one format at a time. Thus the structure allows to ignore all the unrelated stuff and allows to browse for lists and topics compatible with that specific format.

> [!IMPORTANT]
> Folders and filenames in repository paths starting with `/by-*` are meant to be static/constant and thus used as subscription targets.

Everything else is considered "technical" stuff used to generate the lists and might change as I see fit.

## Formats

- adblock ⚠️ UNTESTED
- dnsmasq ⚠️ UNTESTED
- hostsetc ⚠️ UNTESTED
- hostsip4 ⚠️ UNTESTED
- hostsip6 ⚠️ UNTESTED
- uBlacklist [README](./by-format/ublacklist/README.md)

## Topics

> [!TIP]
> Check for existing resources. Head over to
> 
> - https://ublacklist.github.io/rulesets
> - https://github.com/rjaus/awesome-ublacklist
> 
> to see if the desired topic is already covered / available as subscription.

If existing resources are missing a specific format, I might consider generating that. Feel free to suggest additions.

### wikifarms

Inspired by the no longer available nu/uBlacklistFandomWikis[^wiki1] project discussed[^wiki2] in [rjaus/awesome-ublacklist](https://github.com/rjaus/awesome-ublacklist/), this blocklist aims to hide proprietary wikis from search results in favour of independent alternatives.

Blocking is done by following the definitions of two projects:

- https://github.com/wiki-gg-oss/redirect-extension/ by https://www.wiki.gg/redirect/
- https://github.com/KevinPayravi/indie-wiki-buddy/ by https://getindie.wiki/

Both parties offer extensions that not only work on search results, but notify or redirect you if you access a "unwanted" wiki directly. Therefore, if you deal with wiki farms heavily, you might want to consider looking into those projects.

If you don't want to install dedicated extensions, this blocklist allows you to get rid of the clutter from the search results.

### topic ...

If there is a topic you couldn't find any subscription links for, feel free to propose an addition. 

Convertible public sources are obviously the preferred way because they allow for continuous updating of lists through automated workflows without my interference / manual involvement.

## Details

The original focus is on creating subscribable lists for uBlacklist. Other formats, however can be created just as easily from the source file. Bear in mind though, that the resulting blocking behavior may vary depending on the granularity and complexity of search expressions (matches) supported by the different formats.

Example: If the source file contains "subdomain.example.com/certain/path", the list file for one service does block only this path whereas another list might only be able to reject on a subdomain level and yet another service will either block the full domain or rather not contain the entry at all.

How different / unsupported entries are treated when generating a certain list format from the source file is always opinionated:

- Skipping entries with higher granularity than supported by the target list format, fails to block those unwanted sites.
- Adding only supported parts like (sub)domain instead of path of an unwanted site entry to the target list will likely cause false positives and block content that might just be unlucky to be a sibling of the unwanted site in terms of domain location.

Which approach will be used depends on the context (of both, the topic of the list as well as the content variety of the domain in question). Blocking a multi-topic platform (like SNS) because a specific path is mentioned in a specific topic list (like gaming or ai), will not be done for those topic lists because it targets the wrong (too broad) context. You are not out of options though, as you will most likely find another list for that other context. Like a list to block sites of SNS in this example, if that is what you where aiming at.

There can be other cases, where falling back to blocking a domain instead of only certain paths can be justified. That is most likely the case, if the scope of content on the platform matches that of the blocking list for a specific topic. As an example, the wikifarms source contains only paths to specific wikis as unwanted if there is a known alternative hosted elsewhere. For target blocklist formats, that do not support this level of detail, it makes sense to block the parent domain instead (it would be empty otherwise). Users are free to choose to subscribe or not. If they need / want more granularity, they must switch to a blocking solution that supports another format that supports the desired level of detail.

## Motivation

This project was created out of the desire to declutter web search results by preventing unwanted or annoying entries.
This has become increasingly relevant in recent years. Even before the advent of commonly available AI services, there was an influx of generated "content" flooding the web.

While using technical means to aggregate information is neither good nor bad by itself, the amount[^1] of content produced with malevolent or at least ignorant intentions seems to surpass the amount considered legitimate or at least non-disturbing / harmless. Click-bait, copycat, low-quality, fake, malware, addictive, you name it.
This reminds of the pitiable success of email spam[^2] <details><summary>Statista</summary><img src="https://www.statista.com/graphic/1/420400/spam-email-traffic-share-annual.jpg" alt="Statistic: Global spam volume as percentage of total e-mail traffic from 2011 to 2023 | Statista" style="width: 50%; height: auto !important;"/></details> and I even like to think of it as a evenly questionable continuation or progression.
However, bad content just sitting there shouldn't affect me enough to bother. Thus it needs to be distributed to hit .

... and that's where web search providers come in.
You probably all know the situation where searching for content within a specific context turns into drawing one blank after the other. Some you remember by name (domain) desperately fighting to keep infuriation down every time you have to skip over it. Others leave you even more exhausted when half way through an article you wake up from that well-crafted composition of mindful thoughts mantled with eloquent enunciation to the realization that this is in fact just a pile of unrelated, unhelpful, nonsensical at times even dangerously misleading garbage.

[^wiki1]: https://web.archive.org/web/20250916131203/https://git.32bit.cafe/nu/uBlacklistFandomWikis
[^wiki2]: https://github.com/rjaus/awesome-ublacklist/pull/20
[^1]: I'm using the description "amount of content" here, rather than accounting for actors because a very small group of disturbing actors is able to impact an overwhelmingly large group of legitimate actors.
[^2]: [Statistic: Global spam volume as percentage of total e-mail traffic from 2011 to 2023 | Statista](href="https://www.statista.com/statistics/420400/spam-email-traffic-share-annual/)
[^3]: https://www.spamhaus.org/reputation-statistics/countries/spam/
