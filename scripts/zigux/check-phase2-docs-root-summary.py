#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = Path("Documentation/zigux/README.md")

REQUIRED_FILES = [
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/phase2-closure.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-kconfig-readme-alignment.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("zigux/Makefile"),
]

REQUIRED_MARKERS = [
    "Phase 2 notes - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
    "the repo-local `.zig-toolchain` fallback reused by those Linux-style Phase 2 routes",
    "instead of overstating missing dedicated validator, manifest, cross-target, or bridge checker files as live current-`master` evidence",
]


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    doc_path = root / DOC
    if not doc_path.is_file():
        return [f"missing_file:{DOC.as_posix()}"]

    text = doc_path.read_text(encoding="utf-8")
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing_marker:{marker}")

    return issues


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_good_tree(root: Path) -> None:
    write_text(root / DOC, "\n".join(REQUIRED_MARKERS) + "\n")
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_docs_root_summary_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-docs-root:self-test:good_tree")
        cases_run += 1

        build_good_tree(root)
        (root / DOC).unlink()
        issues = collect_issues(root)
        if issues != [f"missing_file:{DOC.as_posix()}"]:
            raise SystemExit("phase2-docs-root:self-test:missing_doc")
        cases_run += 1

        build_good_tree(root)
        write_text(root / DOC, "Phase 2 notes\n")
        issues = collect_issues(root)
        if not any(issue.startswith("missing_marker:") for issue in issues):
            raise SystemExit("phase2-docs-root:self-test:missing_marker")
        cases_run += 1

        build_good_tree(root)
        (root / REQUIRED_FILES[0]).unlink()
        issues = collect_issues(root)
        if f"missing_file:{REQUIRED_FILES[0].as_posix()}" not in issues:
            raise SystemExit("phase2-docs-root:self-test:missing_required_file")
        cases_run += 1

    print("PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the docs-root Phase 2 summary stays aligned with the active toolchain packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_DOCS_ROOT_SUMMARY=fail")
        print("PHASE2_DOCS_ROOT_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_DOCS_ROOT_SUMMARY_ISSUES_END")
        return 1

    print("PHASE2_DOCS_ROOT_SUMMARY=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
