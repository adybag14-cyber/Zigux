#!/usr/bin/env python3
"""Guard the bootstrap Phase 2 genksyms route packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
VALIDATOR = "scripts/zigux/validate-phase2.py"
CLOSURE = "Documentation/zigux/phase2-closure.md"
SCRIPTS_README = "scripts/zigux/README.md"
TESTS_README = "zigux/tests/README.md"
BRIDGE_CHECKER = "scripts/zigux/check-genksyms-bridge.py"
ALIGNMENT_CHECKER = "scripts/zigux/check-phase2-genksyms-selftest-alignment.py"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    VALIDATOR,
    CLOSURE,
    SCRIPTS_README,
    TESTS_README,
    BRIDGE_CHECKER,
    ALIGNMENT_CHECKER,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
)
WORKFLOW_TAIL_MARKER = "run: make -C zigux phase2-validate"

MAKEFILE_LINES = (
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

VALIDATOR_MARKERS = (
    '"run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",',
    '"run: python3 scripts/zigux/check-genksyms-bridge.py",',
    '"run: zig test scripts/zigux/genksyms.zig",',
    '"run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",',
    '"run: make -C zigux phase2-genksyms",',
    '"scripts/zigux/check-genksyms-bridge.py",',
    '"scripts/zigux/check-phase2-genksyms-selftest-alignment.py",',
)

CLOSURE_MARKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
)

SCRIPTS_README_MARKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "make -C zigux phase2-genksyms",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
)

EXPECTED_SELF_TEST_CASE_COUNT = 12


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def collect_marker_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def ensure_workflow_order(workflow_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    positions: list[int] = []
    for marker in WORKFLOW_LINES:
        index = workflow_text.find(marker)
        if index == -1:
            return issues
        positions.append(index)
    if positions != sorted(positions):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "genksyms route packet markers are out of order"))

    tail_index = workflow_text.find(WORKFLOW_TAIL_MARKER)
    route_index = workflow_text.find(WORKFLOW_LINES[-1])
    if tail_index == -1:
        issues.append(("MISSING_WORKFLOW_TAIL_MARKER", WORKFLOW_TAIL_MARKER))
    elif route_index > tail_index:
        issues.append(("WORKFLOW_TAIL_ORDER_MISMATCH", WORKFLOW_TAIL_MARKER))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    validator_text = read_text(resolve(root, VALIDATOR))
    closure_text = read_text(resolve(root, CLOSURE))
    scripts_readme_text = read_text(resolve(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve(root, TESTS_README))

    issues.extend(
        collect_marker_issues(
            workflow_text,
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(ensure_workflow_order(workflow_text))
    issues.extend(
        collect_marker_issues(
            makefile_text,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )

    for marker in VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
    for marker in CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))
    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKER", marker))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                *WORKFLOW_LINES,
                WORKFLOW_TAIL_MARKER,
            )
        )
        + "\n",
    )
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve(root, VALIDATOR), "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(resolve(root, CLOSURE), "# Phase 2 Closure\n\n" + "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "# scripts/zigux\n\n" + "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "# zigux/tests\n\n" + "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve(root, BRIDGE_CHECKER), "# present\n")
    write_text(resolve(root, ALIGNMENT_CHECKER), "# present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_bootstrap_genksyms_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[0], "run: python3 broken.py"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[1]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            remove_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_TAIL_MARKER + "\n")
            if WORKFLOW_TAIL_MARKER + "\n" in workflow_path.read_text(encoding="utf-8")
            else remove_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_TAIL_MARKER),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_TAIL_MARKER", WORKFLOW_TAIL_MARKER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_text = replace_exact_line(workflow_text, WORKFLOW_TAIL_MARKER, WORKFLOW_LINES[-1])
        workflow_text = replace_exact_line(workflow_text, WORKFLOW_LINES[-1], WORKFLOW_TAIL_MARKER)
        workflow_path.write_text(workflow_text, encoding="utf-8")
        assert ("WORKFLOW_TAIL_ORDER_MISMATCH", WORKFLOW_TAIL_MARKER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[2], "$(PYTHON) broken.py"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[3]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[3]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        validator_path = resolve(root, VALIDATOR)
        validator_path.write_text(
            remove_once(validator_path.read_text(encoding="utf-8"), VALIDATOR_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", VALIDATOR_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        closure_path = resolve(root, CLOSURE)
        closure_path.write_text(
            remove_once(closure_path.read_text(encoding="utf-8"), CLOSURE_MARKERS[3]),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        scripts_readme_path = resolve(root, SCRIPTS_README)
        scripts_readme_path.write_text(
            remove_once(scripts_readme_path.read_text(encoding="utf-8"), SCRIPTS_README_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        tests_readme_path = resolve(root, TESTS_README)
        tests_readme_path.write_text(
            remove_once(tests_readme_path.read_text(encoding="utf-8"), TESTS_README_MARKERS[3]),
            encoding="utf-8",
        )
        assert ("MISSING_TESTS_README_MARKER", TESTS_README_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve(root, BRIDGE_CHECKER).unlink()
        assert ("MISSING_REQUIRED_PATH", BRIDGE_CHECKER) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the bootstrap Phase 2 genksyms route packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_ROOT={root}")
    print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_GENKSYMS_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
