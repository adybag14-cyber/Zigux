#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 docs-root summary packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = Path("Documentation/zigux/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md"),
    Path("Documentation/zigux/phase2-closure.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-genksyms-bridge.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("scripts/zigux/kconfig/conf_bridge.zig"),
    Path("scripts/zigux/kconfig/confdata_bridge.zig"),
    Path("scripts/zigux/genksyms.zig"),
    Path("scripts/zigux/fixdep.zig"),
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
    Path("third_party/README.md"),
)

REQUIRED_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`zigux/Makefile`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py` reviewer-surface guards",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are directly readable on current `master` again",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet",
)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_root(override: Path | None) -> Path:
    return override.resolve() if override else ROOT


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    doc_path = root / DOC
    if not doc_path.is_file():
        return [f"missing_file:{DOC.as_posix()}"]

    doc_text = load_text(doc_path)

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")

    for marker in REQUIRED_MARKERS:
        if marker not in doc_text:
            issues.append(f"missing_marker:{marker}")

    return issues


def write_sample_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "placeholder\n")
    write_text(root / DOC, "\n".join(REQUIRED_MARKERS) + "\n")


def run_self_test() -> int:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_docs_root_summary_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        if collect_issues(root):
            raise SystemExit("phase2-docs-root-summary:self-test:good_tree")
        cases_run += 1

        write_sample_root(root)
        (root / DOC).unlink()
        issues = collect_issues(root)
        if issues != [f"missing_file:{DOC.as_posix()}"]:
            raise SystemExit("phase2-docs-root-summary:self-test:missing_doc")
        cases_run += 1

        write_sample_root(root)
        write_text(root / DOC, "Phase 2 notes\n")
        issues = collect_issues(root)
        if not any(issue.startswith("missing_marker:") for issue in issues):
            raise SystemExit("phase2-docs-root-summary:self-test:missing_marker")
        cases_run += 1

        write_sample_root(root)
        missing_path = REQUIRED_FILES[0]
        (root / missing_path).unlink()
        issues = collect_issues(root)
        if f"missing_file:{missing_path.as_posix()}" not in issues:
            raise SystemExit("phase2-docs-root-summary:self-test:missing_required_file")
        cases_run += 1

    print("PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the docs-root Phase 2 summary stays aligned with the live current packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for focused checker replay",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_DOCS_ROOT_SUMMARY_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE2_DOCS_ROOT_SUMMARY=fail")
        print("PHASE2_DOCS_ROOT_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_DOCS_ROOT_SUMMARY_ISSUES_END")
        return 1

    print("PHASE2_DOCS_ROOT_SUMMARY=pass")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_DOCS_ROOT_SUMMARY_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
