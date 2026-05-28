#!/usr/bin/env python3
"""Guard the current Phase 2 toolchain action-path packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS = "Documentation/zigux/README.md"
NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW = "Documentation/zigux/review-checklist.md"
TESTS = "zigux/tests/README.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
TOOLCHAIN = "scripts/zigux/check-zig-toolchain.py"
PINNING = "scripts/zigux/check-phase2-toolchain-pinning.py"
PIN_SCOPE = "scripts/zigux/check-phase2-toolchain-pin-scope.py"

FILES = (
    DOCS,
    NOTES,
    REVIEW,
    TESTS,
    WORKFLOW,
    MAKEFILE,
    TOOLCHAIN,
    PINNING,
    PIN_SCOPE,
)

DOCS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`third_party/README.md`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`third_party/README.md`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

TESTS_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)


def r(root: Path, rel: str) -> Path:
    return root / rel


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def line_issues(text: str, markers: tuple[str, ...], missing: str, duplicate: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker in markers:
        count = lines.count(marker)
        if count == 0:
            issues.append((missing, marker))
        elif count != 1:
            issues.append((duplicate, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in FILES:
        if not r(root, rel).exists():
            issues.append(("MISSING_FILE", rel))
    if issues:
        return issues

    issues.extend(missing_markers(read(r(root, DOCS)), DOCS_MARKERS, "MISSING_DOCS_MARKER"))
    issues.extend(missing_markers(read(r(root, NOTES)), NOTES_MARKERS, "MISSING_NOTES_MARKER"))
    issues.extend(missing_markers(read(r(root, REVIEW)), REVIEW_MARKERS, "MISSING_REVIEW_MARKER"))
    issues.extend(missing_markers(read(r(root, TESTS)), TESTS_MARKERS, "MISSING_TESTS_MARKER"))
    issues.extend(line_issues(read(r(root, WORKFLOW)), WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))
    issues.extend(line_issues(read(r(root, MAKEFILE)), MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write(r(root, DOCS), "\n".join(["# docs", *DOCS_MARKERS, ""]))
    write(r(root, NOTES), "\n".join(["# notes", *NOTES_MARKERS, ""]))
    write(r(root, REVIEW), "\n".join(["# review", *REVIEW_MARKERS, ""]))
    write(r(root, TESTS), "\n".join(["# tests", *TESTS_MARKERS, ""]))
    write(r(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write(r(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    for rel in FILES:
        if rel in {DOCS, NOTES, REVIEW, TESTS, WORKFLOW, MAKEFILE}:
            continue
        write(r(root, rel), "present\n")


def self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_action_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = r(root, WORKFLOW)
            path.write_text("\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() != marker) + "\n", encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = r(root, WORKFLOW)
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if line.strip() == marker:
                    lines.insert(index + 1, line)
                    break
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = r(root, MAKEFILE)
            path.write_text("\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() != marker) + "\n", encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = r(root, MAKEFILE)
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if line.strip() == marker:
                    lines.insert(index + 1, line)
                    break
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        representative_markers = (
            (DOCS, DOCS_MARKERS[0], "MISSING_DOCS_MARKER"),
            (DOCS, DOCS_MARKERS[-1], "MISSING_DOCS_MARKER"),
            (NOTES, NOTES_MARKERS[0], "MISSING_NOTES_MARKER"),
            (NOTES, NOTES_MARKERS[-1], "MISSING_NOTES_MARKER"),
            (REVIEW, REVIEW_MARKERS[0], "MISSING_REVIEW_MARKER"),
            (REVIEW, REVIEW_MARKERS[-1], "MISSING_REVIEW_MARKER"),
            (TESTS, TESTS_MARKERS[0], "MISSING_TESTS_MARKER"),
            (TESTS, TESTS_MARKERS[-1], "MISSING_TESTS_MARKER"),
        )
        for rel, marker, code in representative_markers:
            build_sample_root(root)
            path = r(root, rel)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks += 1

        for rel in FILES:
            build_sample_root(root)
            r(root, rel).unlink()
            assert ("MISSING_FILE", rel) in collect_issues(root)
            checks += 1

    print("PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_TOOLCHAIN_ACTION_PATH_SAMPLE_ROOT=written")
        print(f"PHASE2_TOOLCHAIN_ACTION_PATH_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOLCHAIN_ACTION_PATH=pass")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_DOCS_MARKER_COUNT={len(DOCS_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_ACTION_PATH_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
