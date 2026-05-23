#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

CLOSURE_MARKERS = (
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "`make -C zigux phase2-toolchain`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
)

EXPECTED_MANIFEST_ARCHIVE_SUPPORT = (
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

EXPECTED_MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)

EXPECTED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_manifest_list(
    issues: list[tuple[str, str]],
    manifest: dict[str, object],
    key: str,
) -> list[str] | None:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(
    issues: list[tuple[str, str]],
    label: str,
    actual: list[str] | None,
    expected: tuple[str, ...],
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(root / PHASE2_CLOSURE_DOC.relative_to(ROOT))
    workflow_text = read_text(root / PHASE2_WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / PHASE2_MAKEFILE.relative_to(ROOT))
    manifest = read_json(root / PHASE2_TOOL_MANIFEST.relative_to(ROOT))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    expect_subset(
        issues,
        "archive_support",
        require_manifest_list(issues, manifest, "archive_support"),
        EXPECTED_MANIFEST_ARCHIVE_SUPPORT,
    )
    expect_subset(
        issues,
        "bootstrap_helpers",
        require_manifest_list(issues, manifest, "bootstrap_helpers"),
        EXPECTED_MANIFEST_BOOTSTRAP_HELPERS,
    )
    expect_subset(
        issues,
        "checkers",
        require_manifest_list(issues, manifest, "checkers"),
        EXPECTED_MANIFEST_CHECKERS,
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_STAGE_HELPER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: object) -> None:
    write_text(path, json.dumps(content, indent=2) + "\n")


def build_sample_root(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase2-closure.md",
        "\n".join(["# Phase 2 Closure", *[f"- {marker}" for marker in CLOSURE_MARKERS]]) + "\n",
    )
    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(["name: zigux-bootstrap", *WORKFLOW_LINES]) + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(["phase2-toolchain:", *[f"\t{line}" for line in MAKEFILE_LINES]]) + "\n",
    )
    write_json(
        root / "zigux/tests/fixtures/phase2_tool_manifest.json",
        {
            "present_surfaces": {
                "archive_support": list(EXPECTED_MANIFEST_ARCHIVE_SUPPORT),
                "bootstrap_helpers": list(EXPECTED_MANIFEST_BOOTSTRAP_HELPERS),
                "checkers": list(EXPECTED_MANIFEST_CHECKERS),
            }
        },
    )


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_stage_helper_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / "Documentation/zigux/phase2-closure.md"
        closure_text = closure_path.read_text(encoding="utf-8").replace(
            "`scripts/zigux/stage-pinned-zig-archive.py`", "", 1
        )
        closure_path.write_text(closure_text, encoding="utf-8")
        assert (
            "MISSING_CLOSURE_MARKER",
            "`scripts/zigux/stage-pinned-zig-archive.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
                "run: python3 scripts/zigux/other.py",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
                "# removed",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = root / "zigux/tests/fixtures/phase2_tool_manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bootstrap_helpers"].remove(
            "scripts/zigux/stage-pinned-zig-archive.py"
        )
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "bootstrap_helpers:scripts/zigux/stage-pinned-zig-archive.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = root / "zigux/tests/fixtures/phase2_tool_manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove(
            "scripts/zigux/check-lane05-install-zig-archive-verification.py"
        )
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "checkers:scripts/zigux/check-lane05-install-zig-archive-verification.py",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_STAGE_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_STAGE_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 closure archive-stage helper packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in packet checks",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_STAGE_HELPER_PACKET=pass")
    print("PHASE2_CLOSURE_STAGE_HELPER_PACKET_SCOPE=archive_stage_helper_packet")
    print("PHASE2_CLOSURE_STAGE_HELPER_PACKET_REMAINING_GAPS=")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
