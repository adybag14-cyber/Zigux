#!/usr/bin/env python3
"""Guard the current Lane 16 bench packet against drift in live Phase 1 surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
BENCH_CHECKER_REL = "scripts/zigux/check-phase1-bench.py"

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

MARKERS = {
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    ),
    REVIEW_CHECKLIST_REL: (
        "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    SCRIPTS_README_REL: (
        "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks",
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it",
    ),
    TESTS_README_REL: (
        "- `scripts/zigux/check-phase1-bench.py`",
        "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
    WORKFLOW_REL: (
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    BENCH_CHECKER_REL: (
        "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent",
        "def repo_root(root: str | None) -> Path:",
        "def expectations_path(root: Path) -> Path:",
        "def bench_source_path(root: Path) -> Path:",
        "def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:",
        "def validate_bench_source(text: str) -> tuple[str, object]:",
        "SOURCE_MARKER_SETS = (",
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
        'print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")',
        'print(f"PHASE1_BENCH_SOURCE={phase1_bench}")',
        'print(f"PHASE1_BENCH_ZIG={zig}")',
    ),
}

EXPECTED_BLOCKS = {
    BENCH_CHECKER_REL: (
        (
            "def load_runtime_expectations(path: Path) -> tuple[str, object]:",
            "try:",
            "expectations = load_expectations(path)",
            'return ("missing_expectations_file", path)',
            'return ("expectations_json_error", exc)',
            "kind, payload = validate_expectations(expectations)",
            'if kind != "pass":',
            'return ("pass", expectations)',
        ),
        (
            "def load_runtime_bench_source(path: Path) -> tuple[str, object]:",
            "try:",
            'text = path.read_text(encoding="utf-8")',
            'return ("missing_bench_source_file", path)',
            "return validate_bench_source(text)",
        ),
        (
            'parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")',
            'parser.add_argument("--zig", help="Path to Zig executable")',
            'parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")',
            "if args.self_test:",
            "run_self_test()",
            "return 0",
        ),
        (
            'if kind == "missing_expectations_file":',
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
            'print(f"EXPECTATIONS_PATH={payload}")',
            "return 1",
        ),
        (
            'if kind == "expectations_json_error":',
            "exc = payload",
            "assert isinstance(exc, json.JSONDecodeError)",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
            'print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
            'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
            "return 1",
        ),
        (
            "if result.returncode != 0:",
            'print("PHASE1_BENCH_CHECK=fail")',
            'print(f"BENCH_COMMAND_EXIT={result.returncode}")',
            "if result.stdout:",
            'print(result.stdout.rstrip("\\n"))',
            "if result.stderr:",
            'print(result.stderr.rstrip("\\n"))',
            "return 1",
        ),
    ),
}

FORBIDDEN_FRAGMENTS = {
    BENCH_CHECKER_REL: (
        'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
        'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
        "def validate_find_bit_bench_source(text: str) -> tuple[str, object]:",
        "PHASE1_BENCH_EXPECTATION_COUNT",
        'PHASE1_BENCH_CHECK_REASON=bench_command_exit',
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def line_indent(raw_line: str) -> int:
    return len(raw_line) - len(raw_line.lstrip(" "))


def extract_indented_block(text: str, first_line: str) -> list[str]:
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip() != first_line:
            continue
        base_indent = line_indent(raw_line)
        block = [raw_line.strip()]
        for next_raw in lines[index + 1 :]:
            stripped = next_raw.strip()
            if not stripped:
                block.append("")
                continue
            indent = line_indent(next_raw)
            if indent <= base_indent:
                return block
            block.append(stripped)
        return block
    return []


def block_contains_expected_lines(block: list[str], expected_lines: tuple[str, ...]) -> bool:
    compact_block = [line for line in block if line]
    expected_index = 0
    for line in compact_block:
        if expected_index == len(expected_lines):
            return True
        if line == expected_lines[expected_index]:
            expected_index += 1
    return expected_index == len(expected_lines)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        if relative_path == WORKFLOW_REL:
            lines = text.splitlines()
            for marker in markers:
                count = sum(1 for line in lines if line.strip() == marker)
                if count != 1:
                    issues.append(
                        f"{relative_path}:marker_count:{marker}:expected=1:actual={count}"
                    )
        else:
            for marker in markers:
                count = text.count(marker)
                if count != 1:
                    issues.append(
                        f"{relative_path}:marker_count:{marker}:expected=1:actual={count}"
                    )

        for fragment in FORBIDDEN_FRAGMENTS.get(relative_path, ()):
            count = text.count(fragment)
            if count != 0:
                issues.append(f"{relative_path}:forbidden:{fragment}:actual={count}")

        for expected_block in EXPECTED_BLOCKS.get(relative_path, ()):
            first_line = expected_block[0]
            first_count = sum(1 for line in text.splitlines() if line.strip() == first_line)
            if first_count != 1:
                issues.append(
                    f"{relative_path}:marker_count:{first_line}:expected=1:actual={first_count}"
                )
                continue
            block = extract_indented_block(text, first_line)
            if not block_contains_expected_lines(block, expected_block):
                issues.append(f"{relative_path}:block:{first_line}:{block!r}")

    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines = list(MARKERS[relative_path])
        for block in EXPECTED_BLOCKS.get(relative_path, ()):
            lines.append(block[0])
            lines.extend(f"    {line}" if line else "" for line in block[1:])
            lines.append("")
        write_text(root, relative_path, "\n".join(lines).rstrip("\n") + "\n")


def mutate_remove(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    target.write_text(
        target.read_text(encoding="utf-8") + fragment + "\n",
        encoding="utf-8",
    )


def mutate_interleave_block(
    root: Path,
    relative_path: str,
    first_line: str,
    inserted_lines: tuple[str, ...],
) -> None:
    target = root / relative_path
    lines = target.read_text(encoding="utf-8").splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip() != first_line:
            continue
        insertion = [f"    {line}" for line in inserted_lines]
        lines[index + 2:index + 2] = insertion
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    raise AssertionError(first_line)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=sample_repo")
            print(repr(issues))
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-interleave-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_interleave_block(
            root,
            BENCH_CHECKER_REL,
            'if result.returncode != 0:',
            (
                "captured_stdout = result.stdout",
                "captured_stderr = result.stderr",
            ),
        )
        issues = collect_issues(root)
        if issues:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=interleaved_block")
            print(repr(issues))
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-current-packet-remove-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        mutate_remove(root, BENCH_CHECKER_REL, "def repo_root(root: str | None) -> Path:")
        issues = collect_issues(root)
        expected = [
            f"{BENCH_CHECKER_REL}:marker_count:def repo_root(root: str | None) -> Path::expected=1:actual=0"
        ]
        if issues != expected:
            print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=fail")
            print("case=remove_repo_root")
            print(repr(issues))
            return 1

    case_count = 3
    print("PHASE1_BENCH_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BENCH_CURRENT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_BENCH_CURRENT_PACKET=pass")
    print(f"PHASE1_BENCH_CURRENT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_CURRENT_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
