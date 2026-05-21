#!/usr/bin/env python3
"""Guard the current rematerialized Phase 2 `phase2-tools` wrapper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: make -C zigux phase2-tools",
)

MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

DOCS_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
)

BOOTSTRAP_MARKERS = (
    "`python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test`",
    "`python3 scripts/zigux/check-phase2-kbuild-routes.py`",
    "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`",
    "`python3 scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`",
    "`python3 scripts/zigux/check-phase2-required-make-routes.py`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
)

TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`make -C zigux phase2-tools`",
)

TEXT_SURFACES = (
    (DOCS_README, DOCS_MARKERS, "DOCS_README"),
    (BOOTSTRAP_NOTES, BOOTSTRAP_MARKERS, "BOOTSTRAP_NOTES"),
    (REVIEW_CHECKLIST, REVIEW_MARKERS, "REVIEW_CHECKLIST"),
    (SCRIPTS_README, SCRIPTS_MARKERS, "SCRIPTS_README"),
    (TESTS_README, TESTS_MARKERS, "TESTS_README"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_marker_issues(
    text: str, markers: tuple[str, ...], missing_code: str
) -> list[tuple[str, str]]:
    return [(missing_code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINES",
            "DUPLICATE_WORKFLOW_LINES",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINES",
            "DUPLICATE_MAKEFILE_LINES",
        )
    )

    for path, markers, label in TEXT_SURFACES:
        issues.extend(
            collect_marker_issues(
                read_text(resolve_path(root, path)),
                markers,
                f"MISSING_{label}_MARKERS",
            )
        )

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")

    for path, markers, _ in TEXT_SURFACES:
        header = f"# {path.name}"
        write_text(resolve_path(root, path), "\n".join((header, "", *markers)) + "\n")

    for path in SURFACE_PATHS:
        write_text(resolve_path(root, path), "present\n")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + sum(len(markers) for _, markers, _ in TEXT_SURFACES)
        + len(SURFACE_PATHS)
        + 2
    )
    checks_run = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tools_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for path, markers, label in TEXT_SURFACES:
            for marker in markers:
                build_sample_root(root)
                sample_path = resolve_path(root, path)
                sample_path.write_text(
                    replace_once(sample_path.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                assert (f"MISSING_{label}_MARKERS", marker) in collect_issues(root)
                checks_run += 1

        for path in SURFACE_PATHS:
            build_sample_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

        for path in (WORKFLOW, MAKEFILE):
            build_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count, (checks_run, expected_case_count)
    print("PHASE2_TOOLS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample repository root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TOOLS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLS_PACKET=pass")
    print(f"PHASE2_TOOLS_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLS_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLS_PACKET_SURFACE_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
