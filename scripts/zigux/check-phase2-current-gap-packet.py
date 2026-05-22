#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
VALIDATE_PHASE2_REL = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE_REL = Path("scripts/zigux/validate-phase2-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
ARCHIVE_REL = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")

REQUIRED_PATHS = (
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/install-zig.py"),
    Path("scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    Path("scripts/zigux/check-lane05-local-archive-readme.py"),
    Path("scripts/zigux/check-phase2-cross.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-tool-manifest.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/check-phase2-fixdep-gate.py"),
    Path("scripts/zigux/check-fixdep-diff.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/validate-phase2-closure.py"),
    Path("third_party/README.md"),
    ARCHIVE_REL,
    Path("zigux/Makefile"),
    Path("zigux/tests/fixtures/phase2_tool_manifest.json"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
    Path("zigux/tests/fixtures/phase2_cross_targets.json"),
    Path("zigux/tests/fixtures/fixdep/cases.json"),
)

REQUIRED_CLOSURE_MARKERS = (
    "- `PHASE2_CURRENT_GAP_PACKET=`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`third_party/README.md`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_VALIDATE_PHASE2_MARKERS = (
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/fixdep/cases.json",
)

REQUIRED_VALIDATE_PHASE2_CLOSURE_MARKERS = (
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-fixdep",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def replace_line(text: str, old: str, new: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == old:
            lines[index] = new
            return "\n".join(lines) + "\n"
    raise AssertionError(f"expected line not found: {old!r}")


def remove_fragment(text: str, fragment: str) -> str:
    if fragment not in text:
        raise AssertionError(f"expected fragment not found: {fragment!r}")
    return text.replace(fragment, "", 1)


def remove_exact_line(text: str, needle: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == needle:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"expected exact line not found: {needle!r}")


def ensure_empty_gap_packet(closure_text: str, issues: list[tuple[str, str]]) -> None:
    marker = "- `PHASE2_CURRENT_GAP_PACKET=`"
    matching_lines = [
        line.strip()
        for line in closure_text.splitlines()
        if line.strip().startswith("- `PHASE2_CURRENT_GAP_PACKET=")
    ]
    count = sum(1 for line in matching_lines if line == marker)
    if count == 0:
        issues.append(("MISSING_GAP_PACKET_SENTINEL", marker))
    elif count != 1:
        issues.append(("DUPLICATE_GAP_PACKET_SENTINEL", f"{marker}:count={count}"))
    for line in matching_lines:
        if line != marker:
            issues.append(("NONEMPTY_GAP_PACKET_SENTINEL", line))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))

    closure_text = read_text(root, CLOSURE_REL)
    validate_phase2_text = read_text(root, VALIDATE_PHASE2_REL)
    validate_phase2_closure_text = read_text(root, VALIDATE_PHASE2_CLOSURE_REL)
    workflow_text = read_text(root, WORKFLOW_REL)
    makefile_text = read_text(root, MAKEFILE_REL)

    ensure_empty_gap_packet(closure_text, issues)

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_VALIDATE_PHASE2_MARKERS:
        if marker not in validate_phase2_text:
            issues.append(("MISSING_VALIDATE_PHASE2_MARKER", marker))

    for marker in REQUIRED_VALIDATE_PHASE2_CLOSURE_MARKERS:
        if marker not in validate_phase2_closure_text:
            issues.append(("MISSING_VALIDATE_PHASE2_CLOSURE_MARKER", marker))

    for line in REQUIRED_WORKFLOW_LINES:
        count = count_exact_line(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{line}:count={count}"))

    for line in REQUIRED_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, line)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{line}:count={count}"))

    return issues


def report_and_exit(issues: list[tuple[str, str]]) -> None:
    if issues:
        print("PHASE2_CURRENT_GAP_PACKET=fail")
        for kind, detail in issues:
            print(f"{kind}={detail}")
        raise SystemExit(1)

    print("PHASE2_CURRENT_GAP_PACKET=pass")
    print(f"PHASE2_CURRENT_GAP_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CURRENT_GAP_PACKET_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_CURRENT_GAP_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CURRENT_GAP_PACKET_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")


def sample_validate_phase2_text() -> str:
    lines = ["#!/usr/bin/env python3", "REQUIRED_PATHS = ("]
    for rel in REQUIRED_VALIDATE_PHASE2_MARKERS:
        lines.append(f'    "{rel}",')
    lines.extend(
        [
            '    "scripts/zigux/check-zig-toolchain.py",',
            '    "scripts/zigux/validate-phase2-closure.py",',
            '    "zigux/Makefile",',
            ")",
        ]
    )
    return "\n".join(lines) + "\n"


def sample_validate_phase2_closure_text() -> str:
    lines = ['"""sample"""', "REQUIRED_FILES = ("]
    for rel in REQUIRED_VALIDATE_PHASE2_CLOSURE_MARKERS:
        lines.append(f'    Path("{rel}"),')
    lines.extend(
        [
            '    Path("Documentation/zigux/phase2-closure.md"),',
            '    Path("scripts/zigux/validate-phase2.py"),',
            ")",
        ]
    )
    return "from pathlib import Path\n" + "\n".join(lines) + "\n"


def sample_closure_text() -> str:
    bullet_lines = [f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS[1:]]
    return "\n".join(
        [
            "# Phase 2 Closure",
            "",
            "## Current Repo-Reality Gaps",
            "",
            "Within the bounded Phase 2 closure packet, current `master` no longer leaves the local-first archive pair, installer hook, direct cross-route packet, returned closure-validator companions, fixdep checker packet, or fixture-backed manifest guards in the repo-reality-gap bucket.",
            "",
            *bullet_lines[:7],
            "",
            "## Closure Validation",
            "",
            *bullet_lines[7:],
            "",
            REQUIRED_CLOSURE_MARKERS[0],
            "",
        ]
    )


def sample_workflow_text() -> str:
    lines = ["name: zigux-bootstrap"]
    for line in REQUIRED_WORKFLOW_LINES:
        lines.append(line)
    return "\n".join(lines) + "\n"


def sample_makefile_text() -> str:
    return "\n".join(
        [
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "ZIGUX_ROOT := ..",
            "",
            *REQUIRED_MAKEFILE_LINES,
            "",
        ]
    )


def write_sample_root(root: Path) -> None:
    write_text(root, CLOSURE_REL, sample_closure_text())
    write_text(root, VALIDATE_PHASE2_REL, sample_validate_phase2_text())
    write_text(root, VALIDATE_PHASE2_CLOSURE_REL, sample_validate_phase2_closure_text())
    write_text(root, WORKFLOW_REL, sample_workflow_text())
    write_text(root, MAKEFILE_REL, sample_makefile_text())

    for rel in REQUIRED_PATHS:
        if rel == CLOSURE_REL or rel == VALIDATE_PHASE2_REL or rel == VALIDATE_PHASE2_CLOSURE_REL or rel == WORKFLOW_REL or rel == MAKEFILE_REL:
            continue
        if rel == ARCHIVE_REL:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"archive-placeholder")
            continue
        write_text(root, rel, f"placeholder for {rel.as_posix()}\n")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_root = Path(tmpdir) / "sample"
        write_sample_root(sample_root)
        assert collect_issues(sample_root) == []

        closure_path = sample_root / CLOSURE_REL
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(
            replace_line(
                original_closure,
                "- `PHASE2_CURRENT_GAP_PACKET=`",
                "- `PHASE2_CURRENT_GAP_PACKET=scripts/zigux/check-phase2-cross.py`",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert (
            "NONEMPTY_GAP_PACKET_SENTINEL",
            "- `PHASE2_CURRENT_GAP_PACKET=scripts/zigux/check-phase2-cross.py`",
        ) in issues
        closure_path.write_text(original_closure, encoding="utf-8")

        (sample_root / ARCHIVE_REL).unlink()
        issues = collect_issues(sample_root)
        assert ("MISSING_REQUIRED_PATH", ARCHIVE_REL.as_posix()) in issues
        write_sample_root(sample_root)

        closure_path.write_text(
            remove_fragment(original_closure, "`scripts/zigux/check-phase2-tool-manifest.py`"),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert ("MISSING_CLOSURE_MARKER", "`scripts/zigux/check-phase2-tool-manifest.py`") in issues
        closure_path.write_text(original_closure, encoding="utf-8")

        validate_phase2_path = sample_root / VALIDATE_PHASE2_REL
        original_validate_phase2 = validate_phase2_path.read_text(encoding="utf-8")
        validate_phase2_path.write_text(
            remove_fragment(original_validate_phase2, "scripts/zigux/check-phase2-cross.py"),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert ("MISSING_VALIDATE_PHASE2_MARKER", "scripts/zigux/check-phase2-cross.py") in issues
        validate_phase2_path.write_text(original_validate_phase2, encoding="utf-8")

        validate_phase2_closure_path = sample_root / VALIDATE_PHASE2_CLOSURE_REL
        original_validate_phase2_closure = validate_phase2_closure_path.read_text(encoding="utf-8")
        validate_phase2_closure_path.write_text(
            remove_fragment(
                original_validate_phase2_closure,
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert (
            "MISSING_VALIDATE_PHASE2_CLOSURE_MARKER",
            "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        ) in issues
        validate_phase2_closure_path.write_text(original_validate_phase2_closure, encoding="utf-8")

        workflow_path = sample_root / WORKFLOW_REL
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            remove_exact_line(original_workflow, "run: python3 scripts/zigux/check-fixdep-diff.py"),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-fixdep-diff.py",
        ) in issues
        workflow_path.write_text(original_workflow, encoding="utf-8")

        makefile_path = sample_root / MAKEFILE_REL
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            remove_exact_line(
                original_makefile,
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(sample_root)
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        ) in issues

    print("PHASE2_CURRENT_GAP_PACKET_SELF_TEST=pass")
    print("PHASE2_CURRENT_GAP_PACKET_SELF_TEST_CASE_COUNT=7")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 closure note's empty current-gap packet stays honest."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return

    issues = collect_issues(args.root.resolve())
    report_and_exit(issues)


if __name__ == "__main__":
    main()
