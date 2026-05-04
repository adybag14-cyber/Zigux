#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_ROOT_CHECKER_SNIPPETS = [
    "RELEASE_BOUNDARY_LINES = [",
    '"PHASE14_RELEASE_BOUNDARY=present"',
    '"PHASE14_SHARED_REPLAY_PRESENT=yes"',
    '"PHASE14_RELEASE_CLOSED=no"',
    '"shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture"',
    'require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES)',
]

MAKEFILE_SNIPPETS = [
    "phase14-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_line(text: str, snippet: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == snippet)


def require_exact_count(label: str, text: str, snippets: list[str]) -> list[str]:
    issues: list[str] = []
    for snippet in snippets:
        actual = text.count(snippet)
        if actual != 1:
            issues.append(f"{label}:{actual}:{snippet}")
    return issues


def require_exact_line_count(label: str, text: str, snippets: list[str]) -> list[str]:
    issues: list[str] = []
    for snippet in snippets:
        actual = count_exact_line(text, snippet)
        if actual != 1:
            issues.append(f"{label}:{actual}:{snippet}")
    return issues


def validate_alignment(docs_root_checker_text: str, makefile_text: str) -> list[str]:
    issues = require_exact_count("docs_root_checker", docs_root_checker_text, DOCS_ROOT_CHECKER_SNIPPETS)
    issues.extend(require_exact_line_count("makefile", makefile_text, MAKEFILE_SNIPPETS))
    return issues


def run_self_test() -> int:
    docs_root_checker_text = """
RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
]
issues = require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES)
""".strip()

    makefile_text = """
phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
""".strip()

    good = validate_alignment(docs_root_checker_text, makefile_text)
    bad = validate_alignment(
        docs_root_checker_text.replace(
            "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`, ", "", 1
        ),
        makefile_text,
    )
    if good or not bad:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=2")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    docs_root_checker_path = ROOT / "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
    makefile_path = ROOT / "zigux/Makefile"
    required_paths = [docs_root_checker_path, makefile_path]
    missing_files = [str(path) for path in required_paths if not path.exists()]
    if missing_files:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    issues = validate_alignment(read(docs_root_checker_path), read(makefile_path))
    if issues:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("ISSUES_START")
        for issue in issues:
            print(issue)
        print("ISSUES_END")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass")
    print(f"PHASE14_DOCS_ROOT_CHECKER_SNIPPET_COUNT={len(DOCS_ROOT_CHECKER_SNIPPETS)}")
    print(f"PHASE14_MAKEFILE_SNIPPET_COUNT={len(MAKEFILE_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))