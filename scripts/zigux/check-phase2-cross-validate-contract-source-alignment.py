#!/usr/bin/env python3
"""Guard the source contract for the Phase 2 cross validate-contract checker."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TARGET = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"

REQUIRED_MARKERS = (
    '"""Guard the Phase 2 cross packet inside the shared validator contract."""',
    'ROOT = Path(__file__).resolve().parents[2]',
    'VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"',
    'WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"',
    'MAKEFILE = ROOT / "zigux" / "Makefile"',
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'DIRECT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
    'ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
    'FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"',
    'EXPECTED_ROUTE_NAME = "phase2-cross"',
    'EXPECTED_ROUTE = "make -C zigux phase2-cross"',
    'EXPECTED_DIRECT_CHECKER_ROUTE_LINE = \'ROUTE = "make -C zigux phase2-cross"\'',
    '"run: python3 scripts/zigux/check-phase2-cross.py --self-test"',
    '"run: python3 scripts/zigux/check-phase2-cross.py"',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test"',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py"',
    '"run: make -C zigux phase2-cross"',
    '"phase2-cross:"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py"',
    '"scripts/zigux/check-phase2-cross.py"',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py"',
    '"zigux/tests/fixtures/phase2_cross_targets.json"',
    '"x86_64-linux": "archive_required"',
    '"aarch64-linux": "route_contract_only"',
    'expected_case_count = 15',
    'def write_sample_root(destination: Path) -> int:',
    'print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST=pass")',
    'print("PHASE2_CROSS_VALIDATE_CONTRACT=pass")',
    'print(f"PHASE2_CROSS_VALIDATE_CONTRACT_WORKFLOW_LINE_COUNT={len(EXPECTED_VALIDATOR_WORKFLOW_LINES)}")',
    'print(f"PHASE2_CROSS_VALIDATE_CONTRACT_REQUIRED_PATH_COUNT={len(EXPECTED_VALIDATOR_PATHS)}")',
)

EXPECTED_WORKFLOW_LINE_COUNT = 5
EXPECTED_REQUIRED_PATH_COUNT = 3
EXPECTED_SELF_TEST_CASE_COUNT = 13


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    target_text = read_text(resolve_path(root, TARGET))

    for marker in REQUIRED_MARKERS:
        count = target_text.count(marker)
        if count == 0:
            issues.append(("MISSING_SOURCE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SOURCE_MARKER", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, TARGET),
        "\n".join(
            (
                "#!/usr/bin/env python3",
                REQUIRED_MARKERS[0],
                "",
                "from __future__ import annotations",
                "",
                "import argparse",
                "import json",
                "import tempfile",
                "from pathlib import Path",
                "",
                REQUIRED_MARKERS[1],
                REQUIRED_MARKERS[2],
                REQUIRED_MARKERS[3],
                REQUIRED_MARKERS[4],
                REQUIRED_MARKERS[5],
                REQUIRED_MARKERS[6],
                REQUIRED_MARKERS[7],
                REQUIRED_MARKERS[8],
                "",
                REQUIRED_MARKERS[9],
                REQUIRED_MARKERS[10],
                REQUIRED_MARKERS[11],
                "EXPECTED_VALIDATOR_WORKFLOW_LINES = (",
                f"    {REQUIRED_MARKERS[12]},",
                f"    {REQUIRED_MARKERS[13]},",
                f"    {REQUIRED_MARKERS[14]},",
                f"    {REQUIRED_MARKERS[15]},",
                f"    {REQUIRED_MARKERS[16]},",
                ")",
                "EXPECTED_VALIDATOR_MAKEFILE_LINES = (",
                f"    {REQUIRED_MARKERS[17]},",
                f"    {REQUIRED_MARKERS[18]},",
                f"    {REQUIRED_MARKERS[19]},",
                ")",
                "EXPECTED_VALIDATOR_PATHS = (",
                f"    {REQUIRED_MARKERS[20]},",
                f"    {REQUIRED_MARKERS[21]},",
                f"    {REQUIRED_MARKERS[22]},",
                ")",
                "EXPECTED_FIXTURE_TARGETS = {",
                f"    {REQUIRED_MARKERS[23]},",
                f"    {REQUIRED_MARKERS[24]},",
                "}",
                "",
                "def run_self_test() -> int:",
                f"    {REQUIRED_MARKERS[25]}",
                f"    {REQUIRED_MARKERS[27]}",
                "    return 0",
                "",
                REQUIRED_MARKERS[26],
                "    print(f\"PHASE2_CROSS_VALIDATE_CONTRACT_SAMPLE_ROOT={destination.resolve()}\")",
                "    return 0",
                "",
                "def main() -> int:",
                "    parser = argparse.ArgumentParser()",
                "    parser.add_argument(\"--self-test\", action=\"store_true\")",
                "    parser.add_argument(\"--write-sample-root\", type=Path, default=None)",
                "    args = parser.parse_args()",
                "    if args.self_test:",
                "        return run_self_test()",
                "    if args.write_sample_root is not None:",
                "        return write_sample_root(args.write_sample_root)",
                f"    {REQUIRED_MARKERS[28]}",
                f"    {REQUIRED_MARKERS[29]}",
                f"    {REQUIRED_MARKERS[30]}",
                "    return 0",
                "",
                "if __name__ == \"__main__\":",
                "    raise SystemExit(main())",
            )
        )
        + "\n",
    )


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def duplicate_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_contract_source_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in (
            REQUIRED_MARKERS[0],
            REQUIRED_MARKERS[12],
            REQUIRED_MARKERS[17],
            REQUIRED_MARKERS[20],
            REQUIRED_MARKERS[23],
            REQUIRED_MARKERS[25],
            REQUIRED_MARKERS[26],
            REQUIRED_MARKERS[28],
        ):
            build_sample_root(root)
            target_path = resolve_path(root, TARGET)
            target_path.write_text(remove_marker(target_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SOURCE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in (
            REQUIRED_MARKERS[10],
            REQUIRED_MARKERS[18],
            REQUIRED_MARKERS[29],
        ):
            build_sample_root(root)
            target_path = resolve_path(root, TARGET)
            target_path.write_text(duplicate_marker(target_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_SOURCE_MARKER", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        resolve_path(root, TARGET).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing target checker did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(destination: Path) -> int:
    build_sample_root(destination.resolve())
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT_SAMPLE_ROOT={destination.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 cross validate-contract checker keeps its source contract intact."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in source contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE2_CROSS_VALIDATE_CONTRACT_SOURCE_ALIGNMENT_EXPECTED_COUNTS="
        f"workflow:{EXPECTED_WORKFLOW_LINE_COUNT},paths:{EXPECTED_REQUIRED_PATH_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
