#!/usr/bin/env python3
"""Validate the bilingual static serial with Python's standard library only."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "homepage"
VOLUME = re.compile(r"第[一二三四五六七八九十百0-9]+卷|\bVolume\s+(?:[IVX]+|\d+)\b", re.I)
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


class Node:
    def __init__(self, tag="document", attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def find(self, predicate):
        return ([self] if predicate(self) else []) + [
            found for child in self.children if isinstance(child, Node)
            for found in child.find(predicate)
        ]

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def text(self):
        return "".join(c.text() if isinstance(c, Node) else c for c in self.children)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)
        self.close()
        assert len(self.stack) == 1, "Unclosed HTML element"

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        assert self.stack[-1].tag == tag, f"Mismatched closing tag: {tag}"
        self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def hrefs(node):
    return [n.attrs["href"].removeprefix("./")
            for n in node.find(lambda n: n.tag == "a" and "href" in n.attrs)]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(baseline_ref=None):
    sources = {p.name: p.read_text(encoding="utf-8") for p in HOME.glob("*.html")}
    docs = {name: Document(source).root for name, source in sources.items()}
    chapter_names = set()
    counts = []
    for prefix, homepage, heading in (("", "index.html", "章节目录"),
                                       ("en-", "en.html", "All Chapters")):
        numbers = sorted(int(m[1]) for name in sources
                         if (m := re.fullmatch(prefix + r"chapter-(\d+)\.html", name)))
        require(numbers and numbers == list(range(1, numbers[-1] + 1)),
                f"{prefix or 'CN'}: missing or duplicate chapter numbers")
        counts.append(len(numbers))
        home = docs[homepage]
        directories = home.find(lambda n: n.attrs.get("id") == "chapters")
        require(len(directories) == 1, f"{homepage}: expected one directory")
        directory = directories[0]
        headings = directory.find(lambda n: n.tag == "h2")
        require(len(headings) == 1 and headings[0].text() == heading,
                f"{homepage}: expected one ungrouped directory heading")
        lists = directory.find(lambda n: n.has_class("chapter-list"))
        require(len(lists) == 1, f"{homepage}: expected one continuous chapter list")
        expected = [f"{prefix}chapter-{n}.html" for n in numbers]
        require(hrefs(lists[0]) == expected, f"{homepage}: directory order/links differ")
        latest = home.find(lambda n: n.has_class("latest-card"))
        require(len(latest) == 1 and hrefs(latest[0]) == [expected[-1]],
                f"{homepage}: latest card must link to newest published chapter")
        placeholders = directory.find(lambda n: n.has_class("disabled"))
        require(len(placeholders) == 1 and not hrefs(placeholders[0])
                and str(numbers[-1] + 1) in placeholders[0].text(),
                f"{homepage}: expected one non-clickable next-chapter placeholder")
        for n, name in zip(numbers, expected):
            chapter_names.add(name)
            doc = docs[name]
            require(len(doc.find(lambda e: e.tag == "h1")) == 1, f"{name}: chapter title")
            nav = doc.find(lambda e: e.has_class("reader-nav") or e.has_class("chapter-nav"))
            require(len(nav) == 1, f"{name}: expected one reading navigation")
            links = hrefs(nav[0])
            require(homepage in links or homepage + "#chapters" in links,
                    f"{name}: missing directory link")
            if n > 1:
                require(f"{prefix}chapter-{n - 1}.html" in links, f"{name}: previous link")
            if n < numbers[-1]:
                require(f"{prefix}chapter-{n + 1}.html" in links, f"{name}: next link")
            else:
                require(f"{prefix}chapter-{n + 1}.html" not in links,
                        f"{name}: links to unpublished next chapter")
    require(counts[0] == counts[1], "Chinese and English chapter counts differ")

    link_count = 0
    for name, doc in docs.items():
        # Volume-related words may legitimately occur in story prose. Only
        # reader chrome is constrained; homepages/about pages have no story.
        chrome = doc.find(lambda n: n.tag in ("title", "h1", "h2", "nav", "header")
                          or n.has_class("reader-title") or n.has_class("reader-nav"))
        visible_labels = " ".join(n.text() for n in chrome) if name in chapter_names else doc.text()
        require(not VOLUME.search(visible_labels), f"{name}: obsolete volume label")
        for node in doc.find(lambda n: "href" in n.attrs or "src" in n.attrs):
            value = node.attrs.get("href") or node.attrs.get("src")
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            target = HOME / unquote(url.path) if url.path else HOME / name
            require(target.is_file(), f"{name}: missing local target {value}")
            if url.fragment:
                target_doc = docs.get(target.name)
                require(target_doc and target_doc.find(lambda n: n.attrs.get("id") == unquote(url.fragment)),
                        f"{name}: missing fragment {value}")
            link_count += 1
    print(f"PASS: {counts[0]} chapters per language; two ordered, ungrouped directories; latest cards and placeholders")
    print(f"PASS: {len(chapter_names)} complete previous/next/directory navigation chains")
    print(f"PASS: {len(docs)} well-formed HTML pages; {link_count} internal links/assets; no volume labels")

    if baseline_ref:
        old_names = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", baseline_ref, "homepage/"],
            cwd=ROOT, text=True).splitlines()
        old_chapters = [name for name in old_names if re.fullmatch(r"homepage/(?:en-)?chapter-\d+\.html", name)]
        for path in old_chapters:
            name = Path(path).name
            require(name in chapter_names, f"Deleted chapter: {name}")
            before = subprocess.check_output(["git", "show", f"{baseline_ref}:{path}"], cwd=ROOT, text=True)
            after = sources[name]
            # The chapter article includes every paragraph and story separator.
            for pattern in (r"<article\b[^>]*>.*?</article>", r"<h1\b[^>]*>.*?</h1>", r"<title>.*?</title>"):
                require(re.findall(pattern, before, re.S) == re.findall(pattern, after, re.S),
                        f"{name}: existing story or chapter title changed")
        print(f"PASS: all {len(old_chapters)} existing chapter URLs, titles, and full article HTML unchanged from {baseline_ref}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", help="Git ref for optional exact story-preservation check")
    args = parser.parse_args()
    validate(args.baseline_ref)
