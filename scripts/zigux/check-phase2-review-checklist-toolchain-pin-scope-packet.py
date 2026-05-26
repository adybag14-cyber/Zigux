#!/usr/bin/env python3
"""Guard the shared Phase 2 review-checklist toolchain pin-scope packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TESTS_README = Path("zigux/tests/README.md")
TOOLCHAIN_PIN_SCOPE = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
TOOLCHAIN_CHECKER = Path("scripts/zigux/check-zig-toolchain.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "same pinned toolchain",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "pinned-archive integrity paths",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "pinned `x86_64-linux` bootstrap archive note",
    "repo-local `.zig-toolchain` fallback reused",
)

TOOLCHAIN_PIN_SCOPE_MARKERS = (
    "EXPECTED_PHASE = \"Phase 2\"",
    "EXPECTED_TARGETS = [\"x86_64-linux\"]",
    "\"phase2-toolchain\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    'parser.add_argument("--self-test"',
    'parser.add_argument("--write-sample-root"',
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_min_version(",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_policy_archive(",
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
)

TOOLCHAIN_POLICY_MARKERS = (
    '"phase": "Phase 2"',
    '"channel": "0.17.0-dev.87+9b177a7d2"',
    '"minimum_version": "0.17.0-dev.87+9b177a7d2"',
    '"x86_64-linux"',
    '"phase2-toolchain"',
    '"phase2-genksyms"',
    '"phase2-fixdep"',
)

FILE_MARKERS = (
    (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "REVIEW_CHECKLIST"),
    (BOOTSTRAP_NOTES, BOOTSTRAP_NOTES_MARKERS, "BOOTSTRAP_NOTES"),
    (TESTS_README, TESTS_README_MARKERS, "TESTS_README"),
    (TOOLCHAIN_PIN_SCOPE, TOOLCHAIN_PIN_SCOPE_MARKERS, "TOOLCHAIN_PIN_SCOPE"),
    (TOOLCHAIN_CHECKER, TOOLCHAIN_CHECKER_MARKERS, "TOOLCHAIN_CHECKER"),
    (WORKFLOW, WORKFLOW_MARKERS, "WORKFLOW"),
    (MAKEFILE, MAKEFILE_MARKERS, "MAKEFILE"),
    (TOOLCHAIN_POLICY, TOOLCHAIN_POLICY_MARKERS, "TOOLCHAIN_POLICY"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, relpath: Path) -> Path:
    return root / relpath


def collect_marker_issues(text: str, markers: tuple[str, ...], code_prefix: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append((f"{code_prefix}_MARKER_MISSING", marker))
        elif count != 1:
            issues.append((f"{code_prefix}_MARKER_DUPLICATED", f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for relpath, markers, code_prefix in FILE_MARKERS:
        issues.extend(
            collect_marker_issues(
                read_text(resolve_path(root, relpath)),
                markers,
                code_prefix,
            )
        )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET=fail")
    for code, detail in issues:
        print(f"{code}={detail}")
    return 1


def build_sample_root(root: Path) -> None:
    for relpath, markers, _ in FILE_MARKERS:
        write_text(resolve_path(root, relpath), "\n".join(markers) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    expected_case_count = 1 + sum(len(markers) for _, markers, _ in FILE_MARKERS) + len(FILE_MARKERS)
    checks_run = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_pin_scope_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for relpath, markers, code_prefix in FILE_MARKERS:
            for marker in markers:
                build_sample_root(root)
                path = resolve_path(root, relpath)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                issues = collect_issues(root)
                assert (f"{code_prefix}_MARKER_MISSING", marker) in issues
                checks_run += 1

        for relpath, _, _ in FILE_MARKERS:
            build_sample_root(root)
            resolve_path(root, relpath).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {relpath}")

    assert checks_run == expected_case_count
    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a focused passing sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        sample_root = args.write_sample_root.resolve()
        build_sample_root(sample_root)
        print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_REQUIRED_PATH_COUNT={len(FILE_MARKERS)}")
    print(
        "PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PIN_SCOPE_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for _, markers, _ in FILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
