from llmstxt_lint import lint_text
from llmstxt_lint.cli import main

BASE = "# A\n\n> s\n\n## Docs\n\n"


def rules(text, **kw):
    return [i.rule for i in lint_text(text, **kw)]


def test_disable_next_line():
    t = BASE + "<!-- llmstxt-lint-disable-next-line link-notes-format -->\n- [a](https://a.io) - notes\n- [b](https://b.io) - notes\n"
    issues = lint_text(t)
    assert [(i.line, i.rule) for i in issues] == [(9, "link-notes-format")]


def test_disable_enable_block():
    t = (BASE + "<!-- llmstxt-lint-disable duplicate-link -->\n- [a](https://a.io)\n- [a2](https://a.io)\n"
         "<!-- llmstxt-lint-enable duplicate-link -->\n- [a3](https://a.io)\n")
    assert rules(t) == ["duplicate-link"]
    assert [i.line for i in lint_text(t)] == [11]


def test_disable_all_and_enable_all():
    t = BASE + "<!-- llmstxt-lint-disable -->\n- [a](ftp://x)\n<!-- llmstxt-lint-enable -->\n- [b](ftp://y)\n"
    assert [i.line for i in lint_text(t)] == [10]


def test_disable_file_multiple_rules():
    t = "<!-- llmstxt-lint-disable-file missing-summary, empty-section -->\n# A\n\n## Notes\n\n- note\n"
    # the comment before the title is still content before the H1
    assert rules(t) == ["h1-not-first"]
    t2 = "# A\n\n## Notes\n\n- note\n<!-- llmstxt-lint-disable-file missing-summary empty-section -->\n"
    assert rules(t2) == []


def test_other_rules_unaffected():
    t = BASE + "<!-- llmstxt-lint-disable-next-line duplicate-link -->\n- [a](ftp://x)\n"
    assert rules(t) == ["invalid-url"]


def test_comment_lines_not_prose():
    t = BASE + "- [a](https://a.io)\n<!-- just a normal comment -->\n"
    assert rules(t) == []


def test_inline_config_off():
    t = BASE + "<!-- llmstxt-lint-disable -->\n- [a](ftp://x)\n"
    assert rules(t) == []
    assert rules(t, inline_config=False) == ["invalid-url"]


def test_cli_no_inline_config(tmp_path):
    f = tmp_path / "llms.txt"
    f.write_text(BASE + "<!-- llmstxt-lint-disable -->\n- [a](ftp://x)\n")
    assert main([str(f)]) == 0
    assert main([str(f), "--no-inline-config"]) == 1
