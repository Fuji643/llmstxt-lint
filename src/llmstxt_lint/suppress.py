"""Inline suppression comments.

    <!-- llmstxt-lint-disable [rule, ...] -->      until a matching enable (all rules if none given)
    <!-- llmstxt-lint-enable [rule, ...] -->
    <!-- llmstxt-lint-disable-next-line [rule, ...] -->
    <!-- llmstxt-lint-disable-file [rule, ...] -->  anywhere in the file
"""
from __future__ import annotations

import re

from .linter import Issue

DIRECTIVE = re.compile(
    r"<!--\s*llmstxt-lint-(?P<kind>disable-next-line|disable-file|disable|enable)\b(?P<rules>[^>]*?)\s*-->")
ALL = "*"


def _rules(raw: str) -> set[str]:
    rs = {r.strip() for r in raw.replace(",", " ").split() if r.strip()}
    return rs or {ALL}


def parse_directives(text: str):
    """Return (file_rules, per_line) where per_line maps line number -> disabled rule set."""
    lines = text.splitlines()
    file_rules: set[str] = set()
    per_line: dict[int, set[str]] = {}
    active: set[str] = set()
    next_line: set[str] = set()
    for n, line in enumerate(lines, 1):
        cur = set(active) | next_line
        next_line = set()
        for m in DIRECTIVE.finditer(line):
            kind, rules = m["kind"], _rules(m["rules"])
            if kind == "disable":
                active |= rules
            elif kind == "enable":
                active = set() if ALL in rules else active - rules
            elif kind == "disable-next-line":
                next_line |= rules
            else:
                file_rules |= rules
        if cur:
            per_line[n] = cur
    return file_rules, per_line


def apply(text: str, issues: list[Issue]) -> list[Issue]:
    file_rules, per_line = parse_directives(text)
    if not file_rules and not per_line:
        return issues

    def hidden(i: Issue) -> bool:
        s = file_rules | per_line.get(i.line, set())
        return ALL in s or i.rule in s

    return [i for i in issues if not hidden(i)]


def is_comment_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("<!--") and s.endswith("-->")
