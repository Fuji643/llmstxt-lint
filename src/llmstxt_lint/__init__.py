"""llmstxt-lint: validate llms.txt files."""
from .linter import Issue, lint_text as _lint
from .suppress import apply as _apply


def lint_text(text: str, kind: str = "llms", inline_config: bool = True) -> list[Issue]:
    """Lint llms.txt (kind=\"llms\") or llms-full.txt (kind=\"full\") text.

    Inline ``<!-- llmstxt-lint-disable ... -->`` comments are honoured unless inline_config=False.
    """
    issues = _lint(text, kind=kind)
    return _apply(text, issues) if inline_config else issues

__all__ = ["Issue", "lint_text"]
__version__ = "0.3.0"
