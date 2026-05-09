#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-phase7-make-wrapper.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
NOTE = Path("Documentation/zigux/phase7-make-wrapper-selftest-alignment.md")
VALIDATOR = Path("scripts/zigux/validate-phase7.py")
SAMPLES_README = Path("samples/zigux/README.md")

REQUIRED_CHECKER_MARKERS = (
    "EXPECTED_MAKE_EXPANSIONS = {",
    '"phase7-validate": [',
    '"phase7-test": [',
    '"phase7": [',
    '"python3 scripts/zigux/check-phase7-build-wiring.py --self-test",',
    '"python3 scripts/zigux/check-phase7-build-wiring.py",',
    '"zig build test --build-file zigux/tests/phase7_build.zig --summary all",',
    '"phase7-test: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py",',
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")',
    'print(f"PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT={case_count}")',
    'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")',
)
REQUIRED_CHECKER_EXACT_COUNTS = {
    '"phase7-validate": [': 1,
    '"phase7-test": [': 1,
    '"phase7": [': 1,
    '"python3 scripts/zigux/check-phase7-build-wiring.py --self-test",': 1,
    '"python3 scripts/zigux/check-phase7-build-wiring.py",': 1,
    '"zig build test --build-file zigux/tests/phase7_build.zig --summary all",': 1,
    '"phase7-test: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py",': 1,
    'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")': 1,
    'print(f"PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT={case_count}")': 1,
    'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")': 1,
}
REQUIRED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
)
REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase7-validate",
    "run: make -C zigux phase7-test",
)
REQUIRED_NOTE_MARKERS = (
    "PHASE7_LANE_KEY=P7-Y05",
    "sample-root no-sample reminder drifts away from the same self-test packet",
    "`scripts/zigux/validate-phase7.py`",
    "the no-sample reminder in `samples/zigux/README.md` aligned around that centralized self-test path",
)
REQUIRED_VALIDATOR_MARKERS = (
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "samples/zigux/README.md",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
)
REQUIRED_SAMPLES_MARKERS = (
    "Documentation/zigux/phase7-make-wrapper-selftest-alignment.md",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "zigux/Makefile",
)
FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "run: python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
    "run: python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "run: python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "run: python3 scripts/zigux/check-phase7-build-wiring.py",
)
EXPECTED_SELF_TEST_CASE_COUNT = 25


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_text = read_text(root / CHECKER)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    note_text = read_text(root / NOTE)
    validator_text = read_text(root / VALIDATOR)
    samples_text = read_text(root / SAMPLES_README)

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKERS", marker))

    for marker, expected_count in REQUIRED_CHECKER_EXACT_COUNTS.items():
        count = checker_text.count(marker)
        if count != expected_count:
            issues.append(
                (
                    "DUPLICATE_CHECKER_MARKERS",
                    f"{marker}:count={count}:expected={expected_count}",
                )
            )

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKERS", marker))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKERS", marker))

    for marker in REQUIRED_SAMPLES_MARKERS:
        if marker not in samples_text:
            issues.append(("MISSING_SAMPLES_MARKERS", marker))

    for marker in FORBIDDEN_WORKFLOW_LINES:
        if count_exact_lines(workflow_text, marker):
            issues.append(("FORBIDDEN_WORKFLOW_HOOKS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CHECKER,
        "\n".join(
            (
                "EXPECTED_MAKE_EXPANSIONS = {",
                '    "phase7-validate": [',
                '    "phase7-test": [',
                '    "phase7": [',
                '    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",',
                '    "python3 scripts/zigux/check-phase7-build-wiring.py",',
                '    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",',
                '    "phase7-test: unexpected wrapper expansion: python3 scripts/zigux/check-phase7-build-wiring.py",',
                "}",
                'print("PHASE7_MAKE_WRAPPER_SELF_TEST=pass")',
                'print(f"PHASE7_MAKE_WRAPPER_SELF_TEST_CASE_COUNT={case_count}")',
                'print(f"PHASE7_MAKE_WRAPPER_TARGET_COUNT={len(EXPECTED_MAKE_EXPANSIONS)}")',
                "",
            )
        ),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase7-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py",
                "",
            )
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 7 runtime helper gates",
                "        run: make -C zigux phase7-validate",
                "      - name: Run Phase 7 runtime helper tests",
                "        run: make -C zigux phase7-test",
                "",
            )
        ),
    )
    write_text(root / NOTE, "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    write_text(root / VALIDATOR, "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n")
    write_text(root / SAMPLES_README, "\n".join(REQUIRED_SAMPLES_MARKERS) + "\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p7_make_wrapper_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[8], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[8]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[9], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[9]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                REQUIRED_CHECKER_MARKERS[3],
                REQUIRED_CHECKER_MARKERS[3] + "\n" + REQUIRED_CHECKER_MARKERS[3],
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "DUPLICATE_CHECKER_MARKERS",
            f'{REQUIRED_CHECKER_MARKERS[3]}:count=2:expected=1',
        ) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "\ttrue"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: true"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2") in issues
        cases += 1

        for marker in FORBIDDEN_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(
                path.read_text(encoding="utf-8") + f"        {marker}\n",
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("FORBIDDEN_WORKFLOW_HOOKS", marker) in issues
            cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[10], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[10]) in issues
        cases += 1

        for marker in (
            REQUIRED_CHECKER_MARKERS[4],
            REQUIRED_CHECKER_MARKERS[5],
            REQUIRED_CHECKER_MARKERS[6],
            REQUIRED_CHECKER_MARKERS[7],
        ):
            build_self_test_root(root)
            path = root / CHECKER
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker, "", 1),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_CHECKER_MARKERS", marker) in issues
            cases += 1

        build_self_test_root(root)
        path = root / NOTE
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_NOTE_MARKERS[3], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_NOTE_MARKERS", REQUIRED_NOTE_MARKERS[3]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[1], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[1]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / SAMPLES_README
        path.write_text(
            path.read_text(encoding="utf-8").replace(REQUIRED_SAMPLES_MARKERS[3], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_SAMPLES_MARKERS", REQUIRED_SAMPLES_MARKERS[3]) in issues
        cases += 1

    assert cases == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 7 workflow keeps dedicated validation hooks centralized in the shared make route."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_NOTE_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_VALIDATOR_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    print(f"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SAMPLES_MARKER_COUNT={len(REQUIRED_SAMPLES_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
