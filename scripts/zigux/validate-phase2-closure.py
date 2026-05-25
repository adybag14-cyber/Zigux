#!/usr/bin/env python3
"""Validate the current Phase 2 closure note against the shared closure packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_GENKSYMS_SURVEY_REL = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
ARCHIVE_CONTRACT_PACKET_REL = Path("scripts/zigux/check-phase2-archive-contract-packet.py")
CLOSURE_ARCHIVE_CONTRACT_REL = Path("scripts/zigux/check-phase2-closure-archive-contract.py")
TESTS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
TESTS_ROOT_SUMMARY_REL = Path("scripts/zigux/check-phase2-tests-root-summary.py")
TOOL_MANIFEST_CHECKER_REL = Path("scripts/zigux/check-phase2-tool-manifest.py")
ARCHIVE_README_REL = Path("third_party/README.md")
ARCHIVE_PAYLOAD_REL = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_CLOSURE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    PHASE2_GENKSYMS_SURVEY_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
    ARCHIVE_CONTRACT_PACKET_REL,
    CLOSURE_ARCHIVE_CONTRACT_REL,
    TESTS_ALIGNMENT_REL,
    TESTS_ROOT_SUMMARY_REL,
    TOOL_MANIFEST_CHECKER_REL,
    ARCHIVE_README_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    TESTS_README_REL,
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-archive-contract-packet.py`",
    "`scripts/zigux/check-phase2-closure-archive-contract.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`python3 scripts/zigux/check-phase2-archive-contract-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase2-archive-contract-packet.py`",
    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py --self-test`",
    "`python3 scripts/zigux/check-phase2-closure-archive-contract.py`",
    "`PHASE2_CURRENT_GAP_PACKET=third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "The current closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-archive-contract-packet.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-closure-archive-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-root-summary.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_GAPS = [ARCHIVE_PAYLOAD_REL.as_posix()]
EXPECTED_MANIFEST_SURFACES = {
    "review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ),
    "archive_support": (
        "third_party/README.md",
    ),
}


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def require_manifest_list(issues: list[tuple[str, str]], manifest: dict[str, object], key: str) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    manifest_gaps = manifest.get("repo_reality_gaps")
    if manifest_gaps != EXPECTED_MANIFEST_GAPS:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest_gaps)))

    for key, expected in EXPECTED_MANIFEST_SURFACES.items():
        expect_subset(issues, key, require_manifest_list(issues, manifest, key), expected)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_lines = [
        "# Phase 2 Closure",
        "",
        "## Current Closure Packet",
        "",
        *[f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS],
        "",
    ]
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "ZIG ?= zig",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        "",
        *REQUIRED_MAKEFILE_LINES,
    ]
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": list(EXPECTED_MANIFEST_GAPS),
        "present_surfaces": {key: list(value) for key, value in EXPECTED_MANIFEST_SURFACES.items()},
    }

    write_text(resolve(root, PHASE2_CLOSURE_REL), "\n".join(closure_lines) + "\n")
    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, MAKEFILE_REL), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")

    for rel in REQUIRED_FILES:
        if rel in {PHASE2_CLOSURE_REL, WORKFLOW_REL, MAKEFILE_REL, MANIFEST_REL}:
            continue
        if rel.suffix == ".json":
            write_text(resolve(root, rel), "{}\n")
        else:
            write_text(resolve(root, rel), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "The current closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "The current closure-side archive-contract packet now stays explicit through `scripts/zigux/check-phase2-archive-contract-packet.py`, `third_party/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/check-phase2-tool-manifest.py`, and `scripts/zigux/check-phase2-tests-readme-alignment.py` while `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` remains the lone current repo-reality gap on `master`.",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                "run: make -C zigux phase2-validate",
                "run: make -C zigux phase2-other",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", "run: make -C zigux phase2-validate") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve(root, MAKEFILE_REL)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-closure-archive-contract.py",
                "# removed",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-closure-archive-contract.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["repo_reality_gaps"] = []
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_MANIFEST_GAPS", repr([])) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["archive_support"] = []
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "archive_support:third_party/README.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (resolve(root, TESTS_README_REL)).unlink()
        assert ("MISSING_REQUIRED_FILE", TESTS_README_REL.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 closure note against the shared closure packet.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_STATUS=parked")
    print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure")
    print(f"PHASE2_CLOSURE_REMAINING_GAPS={ARCHIVE_PAYLOAD_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
