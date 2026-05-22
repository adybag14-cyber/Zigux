#!/usr/bin/env python3
"""Check that the docs-root Phase 2 summary stays aligned with the live closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_README_REL = Path("Documentation/zigux/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase2-closure.md"),
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/fixdep.zig"),
    Path("third_party/README.md"),
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
)

REQUIRED_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile` keep the bounded Phase 2 docs-root packet explicit through the returned closure-side validator pair",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
)

FORBIDDEN_MARKERS = (
    "`check-phase2-tool-manifest-packets.py`",
    "missing dedicated validator, manifest, cross-target, or bridge checker files as live current-`master` evidence",
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    readme_path = root / DOCS_ROOT_README_REL
    if not readme_path.is_file():
        return [f"missing_file:{DOCS_ROOT_README_REL.as_posix()}"]

    readme_text = readme_path.read_text(encoding="utf-8")

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing_marker:{marker}")

    for marker in FORBIDDEN_MARKERS:
        count = readme_text.count(marker)
        if count != 0:
            issues.append(f"forbidden_marker:{marker}:count={count}:expected=0")

    return issues


def build_good_tree(root: Path) -> None:
    write_text(root / DOCS_ROOT_README_REL, "\n".join(REQUIRED_MARKERS) + "\n")
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_docs_root_summary_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_tree(root)
        if collect_issues(root):
            raise SystemExit("phase2-docs-root-summary:self-test:good_tree")
        case_count += 1

        build_good_tree(root)
        (root / DOCS_ROOT_README_REL).unlink()
        issues = collect_issues(root)
        if issues != [f"missing_file:{DOCS_ROOT_README_REL.as_posix()}"]:
            raise SystemExit("phase2-docs-root-summary:self-test:missing_readme")
        case_count += 1

        build_good_tree(root)
        readme_path = root / DOCS_ROOT_README_REL
        readme_path.write_text(readme_path.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[0], "", 1))
        issues = collect_issues(root)
        if f"missing_marker:{REQUIRED_MARKERS[0]}" not in issues:
            raise SystemExit("phase2-docs-root-summary:self-test:missing_marker")
        case_count += 1

        build_good_tree(root)
        (root / REQUIRED_FILES[0]).unlink()
        issues = collect_issues(root)
        if f"missing_file:{REQUIRED_FILES[0].as_posix()}" not in issues:
            raise SystemExit("phase2-docs-root-summary:self-test:missing_required_file")
        case_count += 1

        build_good_tree(root)
        readme_path = root / DOCS_ROOT_README_REL
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8") + FORBIDDEN_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if f"forbidden_marker:{FORBIDDEN_MARKERS[0]}:count=1:expected=0" not in issues:
            raise SystemExit("phase2-docs-root-summary:self-test:forbidden_marker")
        case_count += 1

    print("PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_good_tree(root)
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the docs-root Phase 2 summary stays aligned with the live closure packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for replay coverage",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

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
